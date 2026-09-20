"""Safe, reusable text-output support for completion tooling."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

try:
    from tools.validate import Diagnostic
except ModuleNotFoundError:
    from validate import Diagnostic

CA_OUTPUT_EXISTS = "CA_OUTPUT_EXISTS"
CA_OUTPUT_PATH = "CA_OUTPUT_PATH"
CA_OUTPUT_WRITE = "CA_OUTPUT_WRITE"


def write_output(path: Path, text: str, force: bool) -> Diagnostic | None:
    """Create output exclusively, or atomically replace a regular file with force."""
    if not path.parent.exists() or not path.parent.is_dir():
        return Diagnostic(CA_OUTPUT_PATH, str(path), "parent directory must already exist")
    if path.is_symlink() or (path.exists() and (path.is_dir() or not path.is_file())):
        return Diagnostic(CA_OUTPUT_PATH, str(path), "destination must be a regular non-symlink file")
    if path.exists() and not force:
        return Diagnostic(CA_OUTPUT_EXISTS, str(path), "destination already exists; use --force to replace a regular file")
    try:
        if not path.exists():
            created = False
            try:
                with path.open("x", encoding="utf-8", newline="\n") as stream:
                    created = True
                    stream.write(text)
                    stream.flush()
                    os.fsync(stream.fileno())
            except Exception:
                if created and path.exists() and not path.is_symlink(): path.unlink()
                raise
            return None
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(text); stream.flush(); os.fsync(stream.fileno())
            os.replace(temporary, path)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        return None
    except OSError as exc:
        return Diagnostic(CA_OUTPUT_WRITE, str(path), str(exc))
