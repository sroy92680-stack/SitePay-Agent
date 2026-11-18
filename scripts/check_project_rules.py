#Owner::ANIKET::ANHOTRA = MR.Panda
"""Enforce owner tags, source file length and forbidden em dash punctuation."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

OWNER_TEXT = "#Owner::ANIKET::ANHOTRA = MR.Panda"
REQUIRED_HEADERS: dict[str, str] = {
    ".py": OWNER_TEXT,
    ".sh": OWNER_TEXT,
    ".js": f"// {OWNER_TEXT}",
    ".jsx": f"// {OWNER_TEXT}",
    ".ts": f"// {OWNER_TEXT}",
    ".tsx": f"// {OWNER_TEXT}",
    ".css": f"/* {OWNER_TEXT} */",
    ".html": f"<!-- {OWNER_TEXT} -->",
    ".sql": f"-- {OWNER_TEXT}",
}
TEXT_EXTENSIONS = {
    ".py", ".sh", ".js", ".jsx", ".ts", ".tsx", ".css", ".html",
    ".sql", ".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".csv",
}
TEXT_FILENAMES = {".gitignore", ".editorconfig", ".env.example", "Makefile", "LICENSE"}
EXCLUDED_DIRECTORIES = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".ruff_cache", ".mypy_cache", "node_modules", "dist",
    "build", "coverage", "uploads", "local_data",
}
MAX_CODE_LINES = 299


@dataclass(frozen=True)
class Violation:
    """Store a repository policy violation and its relative file path."""

    path: str
    description: str


def check_file(file_path: Path, root: Path) -> list[Violation]:
    """Validate one text file and return all violations.

    Unreadable files are reported rather than silently excluded.
    """
    relative_path = file_path.relative_to(root).as_posix()
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return [Violation(relative_path, f"Cannot read file: {error}")]
    lines = content.splitlines()
    required_header = REQUIRED_HEADERS.get(file_path.suffix.lower())
    findings: list[Violation] = []
    if required_header and (not lines or lines[0] != required_header):
        findings.append(Violation(relative_path, "Missing or incorrect first-line owner tag"))
    if required_header and len(lines) > MAX_CODE_LINES:
        findings.append(Violation(relative_path, f"Source file has {len(lines)} lines"))
    for line_number, line in enumerate(lines, start=1):
        if "\u2014" in line:
            findings.append(Violation(relative_path, f"Em dash on line {line_number}"))
    return findings


def check_repository(root: Path) -> tuple[int, list[Violation]]:
    """Check the full repository, excluding generated caches and private files.

    Return the checked file count and ordered policy findings.
    """
    if not root.is_dir():
        return 0, [Violation(str(root), "Directory not found")]
    checked = 0
    findings: list[Violation] = []
    for file_path in sorted(root.rglob("*")):
        if not file_path.is_file():
            continue
        relative_parts = file_path.relative_to(root).parts
        if any(part in EXCLUDED_DIRECTORIES for part in relative_parts[:-1]):
            continue
        if file_path.suffix.lower() not in TEXT_EXTENSIONS and file_path.name not in TEXT_FILENAMES:
            continue
        checked += 1
        findings.extend(check_file(file_path, root))
    return checked, findings


def main(arguments: list[str] | None = None) -> int:
    """Run the repository policy scan and print reproducible results.

    Return a nonzero exit code if a violation is present.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parsed = parser.parse_args(arguments)
    checked, findings = check_repository(Path(parsed.root).resolve())
    for finding in findings:
        print(f"FAIL {finding.path}: {finding.description}", file=sys.stderr)
    if findings:
        print(f"FAIL {len(findings)} findings in {checked} checked files")
        return 1
    print(f"PASS {checked} checked text files, zero violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
