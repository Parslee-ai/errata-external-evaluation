from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
from typing import Iterable

from .authority import AuthorityPolicy, _command_executable


_UNTRUSTED_EXECUTABLES = {
    "cargo",
    "dotnet",
    "make",
    "pytest",
    "python",
    "python3",
    "ruff",
}


def contained_command(
    argv: tuple[str, ...],
    *,
    authority: AuthorityPolicy,
    runtime_root: Path,
    effect: str,
    network: str,
) -> tuple[tuple[str, ...], dict[str, object]]:
    """Wrap a command in host enforcement or fail closed for workspace code."""

    if effect not in {"read", "local_write"}:
        raise ValueError("containment effect must be read or local_write")
    if network not in {"none", "loopback"}:
        raise ValueError("containment network must be none or loopback")
    runtime_root.mkdir(parents=True, exist_ok=True)
    sandbox = Path("/usr/bin/sandbox-exec")
    if sys.platform == "darwin" and sandbox.is_file():
        profile = _seatbelt_profile(
            authority, runtime_root, argv, effect=effect, network=network
        )
        profile_digest = _sha256(profile.encode("utf-8"))
        profile_path = runtime_root / f"command-{profile_digest}.sb"
        if not profile_path.exists():
            profile_path.write_text(profile, encoding="utf-8")
        return (
            (str(sandbox), "-f", str(profile_path), "--", *argv),
            {
                "kind": "macos-seatbelt",
                "network": "numeric loopback only" if network == "loopback" else "none",
                "writes": (
                    "workspace and isolated runtime, excluding protected paths"
                    if effect == "local_write"
                    else "isolated runtime only"
                ),
                "protected_reads": (
                    "workspace .git, all .errata run custody, and non-workspace project "
                    "data are unavailable to the child except explicit runtime dependencies; "
                    "use dedicated Git and evidence tools"
                ),
                "profile_sha256": profile_digest,
            },
        )
    if _requires_host_containment(argv, authority.workspace):
        raise PermissionError(
            "workspace code and interpreters require an available host containment backend"
        )
    return argv, {
        "kind": "allowlisted-read-command",
        "network": "none",
        "writes": "none authorized",
        "protected_reads": "command arguments remain constrained by workspace authority",
    }


def _requires_host_containment(argv: tuple[str, ...], workspace: Path) -> bool:
    executable = _command_executable(argv[0])
    if executable in _UNTRUSTED_EXECUTABLES:
        return True
    candidate = Path(argv[0])
    if not candidate.is_absolute():
        candidate = workspace / candidate
    try:
        candidate.resolve(strict=True).relative_to(workspace)
    except (FileNotFoundError, ValueError):
        return False
    return True


def _seatbelt_profile(
    authority: AuthorityPolicy,
    runtime_root: Path,
    argv: tuple[str, ...],
    *,
    effect: str,
    network: str,
) -> str:
    readable = {
        authority.workspace,
        runtime_root,
        Path("/System"),
        Path("/usr"),
        Path("/bin"),
        Path("/sbin"),
        Path("/Library"),
        Path("/opt/homebrew"),
        Path("/private/etc"),
        Path("/private/var/db/timezone"),
        Path("/private/var/select"),
        Path("/dev"),
    }
    developer_runtime = Path("/Applications/Xcode.app/Contents")
    if developer_runtime.is_dir():
        readable.add(developer_runtime)
    executable = shutil.which(argv[0])
    if executable:
        executable_path = Path(executable).resolve()
        readable.add(executable_path.parent)
        try:
            if executable_path == Path(sys.executable).resolve(strict=True):
                readable.add(Path(sys.base_prefix).resolve(strict=True))
        except FileNotFoundError:
            pass
    for item in sys.path:
        if not item:
            continue
        path = Path(item).resolve()
        # Only package installation roots are runtime dependencies. Editable
        # installs commonly append arbitrary source checkouts to sys.path; if
        # those are admitted here, code in one selected workspace can inspect
        # another checkout and its observations acquire false provenance.
        if (
            path.exists()
            and path != authority.workspace
            and {"site-packages", "dist-packages"}.intersection(path.parts)
        ):
            readable.add(path if path.is_dir() else path.parent)
    lines = [
        "(version 1)",
        "(deny default)",
        '(import "system.sb")',
        "(allow process*)",
        "(allow sysctl-read)",
        "(allow file-map-executable)",
        "(allow file-read-metadata)",
    ]
    lines.extend(_rules("allow", "file-read*", readable))
    venv_config = _running_interpreter_venv_config(argv[0])
    if venv_config is not None:
        lines.append(
            f"(allow file-read* (literal {json.dumps(str(venv_config))}))"
        )
    writable = [runtime_root]
    if effect == "local_write":
        writable.append(authority.workspace)
    lines.extend(_rules("allow", "file-write*", writable))
    # Children inherit the profile. Network is absent unless the action receipt
    # explicitly requests loopback; DNS and every external socket remain denied.
    if network == "loopback":
        lines.extend(
            (
                '(allow network-inbound (local ip "localhost:*"))',
                '(allow network-outbound (remote ip "localhost:*"))',
            )
        )
    read_denied: set[Path] = set()
    write_denied: set[Path] = set(authority.immutable_paths)
    for protected in authority.protected_paths:
        try:
            runtime_root.relative_to(protected)
        except ValueError:
            read_denied.add(protected)
            write_denied.add(protected)
            continue
        # Process custody must remain writable to the contained child, but the
        # sibling model requests, notebook, state, and evidence log do not.
        for name in (
            "contract.json",
            "contracts",
            "events.jsonl",
            "model",
            "notebook.md",
            "snapshot.json",
            "state.json",
        ):
            read_denied.add(protected / name)
            write_denied.add(protected / name)
    lines.extend(_rules("deny", "file-read*", read_denied))
    lines.extend(_rules("deny", "file-write*", write_denied))
    return "\n".join(lines) + "\n"


def _running_interpreter_venv_config(raw_executable: str) -> Path | None:
    candidate = Path(raw_executable)
    if not candidate.is_absolute():
        selected = shutil.which(raw_executable)
        if selected is None:
            return None
        candidate = Path(selected)
    try:
        if candidate.resolve(strict=True) != Path(sys.executable).resolve(strict=True):
            return None
    except FileNotFoundError:
        return None
    config = candidate.parent.parent / "pyvenv.cfg"
    return config.resolve(strict=True) if config.is_file() else None


def _rules(disposition: str, operation: str, paths: Iterable[Path]) -> list[str]:
    result = []
    for path in sorted({item.resolve() for item in paths}, key=str):
        result.append(
            f"({disposition} {operation} (subpath {json.dumps(str(path))}))"
        )
    return result


def _sha256(value: bytes) -> str:
    from hashlib import sha256

    return sha256(value).hexdigest()
