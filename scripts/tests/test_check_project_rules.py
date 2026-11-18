#Owner::ANIKET::ANHOTRA = MR.Panda
"""Prove that mandatory repository rules fail closed."""

from pathlib import Path

from scripts.check_project_rules import check_file, check_repository


def test_valid_python_owner_tag(tmp_path: Path) -> None:
    """Accept a correctly tagged Python source file."""

    file_path = tmp_path / "feature.py"
    file_path.write_text("#Owner::ANIKET::ANHOTRA = MR.Panda\nprint('ok')\n")
    assert check_file(file_path, tmp_path) == []


def test_missing_owner_tag_is_rejected(tmp_path: Path) -> None:
    """Reject Python files without the mandatory first line."""

    file_path = tmp_path / "feature.py"
    file_path.write_text("print('unowned')\n")
    assert any("owner tag" in finding.description for finding in check_file(file_path, tmp_path))


def test_typescript_owner_tag_is_required(tmp_path: Path) -> None:
    """Use legal comment syntax for TypeScript owner tags."""

    file_path = tmp_path / "feature.ts"
    file_path.write_text("// #Owner::ANIKET::ANHOTRA = MR.Panda\nexport {};\n")
    assert check_file(file_path, tmp_path) == []


def test_em_dash_is_rejected_in_docs(tmp_path: Path) -> None:
    """Scan documentation for forbidden punctuation."""

    file_path = tmp_path / "notes.md"
    file_path.write_text("Text with \u2014 punctuation.\n")
    assert any("Em dash" in finding.description for finding in check_file(file_path, tmp_path))


def test_code_more_than_299_lines_is_rejected(tmp_path: Path) -> None:
    """Enforce the roadmap code file size limit."""

    file_path = tmp_path / "long.py"
    file_path.write_text("#Owner::ANIKET::ANHOTRA = MR.Panda\n" + "pass\n" * 299)
    assert any("300 lines" in finding.description for finding in check_file(file_path, tmp_path))


def test_missing_repository_path_fails(tmp_path: Path) -> None:
    """Never present a nonexistent repository as passing."""

    total, findings = check_repository(tmp_path / "missing")
    assert total == 0
    assert findings


def test_generated_cache_is_ignored(tmp_path: Path) -> None:
    """Exclude generated Python bytecode and cached test artifacts."""

    excluded = tmp_path / "__pycache__"
    excluded.mkdir()
    (excluded / "invalid.py").write_text("print('not checked')\n")
    checked, findings = check_repository(tmp_path)
    assert checked == 0
    assert findings == []
