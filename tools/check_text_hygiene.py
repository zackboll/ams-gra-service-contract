"""Check repository text files against the shared .editorconfig hygiene rules."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, order=True)
class Diagnostic:
    path: str
    line: int
    kind: str
    message: str

    def format(self) -> str:
        location = self.path if self.line == 0 else f"{self.path}:{self.line}"
        return f"{location}: {self.message}"


def check_text_bytes(path: Path, data: bytes) -> list[Diagnostic]:
    """Return deterministic hygiene diagnostics for one repository text file.

    Files containing a NUL byte are treated as binary and intentionally skipped.
    """
    path_text = str(path)
    if b"\0" in data:
        return []

    try:
        data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return [Diagnostic(path_text, 0, "invalid-utf-8", "invalid UTF-8")]

    diagnostics: list[Diagnostic] = []
    line = 1
    line_start = 0
    index = 0
    while index < len(data):
        byte = data[index]
        if byte == ord("\r"):
            if data[line_start:index].endswith((b" ", b"\t")):
                diagnostics.append(
                    Diagnostic(path_text, line, "trailing-whitespace", "trailing whitespace")
                )
            if index + 1 < len(data) and data[index + 1] == ord("\n"):
                diagnostics.append(
                    Diagnostic(path_text, line, "crlf", "CRLF line ending; expected LF")
                )
                index += 1
            else:
                diagnostics.append(
                    Diagnostic(path_text, line, "bare-cr", "bare CR line ending; expected LF")
                )
            line += 1
            index += 1
            line_start = index
        elif byte == ord("\n"):
            if data[line_start:index].endswith((b" ", b"\t")):
                diagnostics.append(
                    Diagnostic(path_text, line, "trailing-whitespace", "trailing whitespace")
                )
            line += 1
            index += 1
            line_start = index
        else:
            index += 1

    if line_start < len(data) and data.endswith((b" ", b"\t")):
        diagnostics.append(Diagnostic(path_text, line, "trailing-whitespace", "trailing whitespace"))
    if data and not data.endswith(b"\n"):
        diagnostics.append(Diagnostic(path_text, 0, "missing-final-newline", "missing final newline"))

    return sorted(diagnostics)


def repository_paths(root: Path = REPOSITORY_ROOT) -> list[Path]:
    """Return tracked and untracked, non-ignored repository paths in stable order."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    names = sorted(name for name in result.stdout.split(b"\0") if name)
    return [Path(name.decode("utf-8", errors="surrogateescape")) for name in names]


def repository_diagnostics(root: Path = REPOSITORY_ROOT) -> list[Diagnostic]:
    """Check every discovered repository file and return sorted diagnostics."""
    diagnostics: list[Diagnostic] = []
    for relative_path in repository_paths(root):
        path = root / relative_path
        if path.is_file():
            diagnostics.extend(check_text_bytes(relative_path, path.read_bytes()))
    return sorted(diagnostics)


def main() -> int:
    try:
        diagnostics = repository_diagnostics()
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.decode("utf-8", errors="replace").strip()
        print(f"error: unable to discover repository files: {stderr}", file=sys.stderr)
        return 2

    if diagnostics:
        for diagnostic in diagnostics:
            print(diagnostic.format())
        return 1

    print("OK: repository text hygiene")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
