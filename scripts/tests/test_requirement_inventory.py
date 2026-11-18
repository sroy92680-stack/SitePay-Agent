#Owner::ANIKET::ANHOTRA = MR.Panda
"""Validate the PDF-derived deliverable inventory and functional-control register."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_STATUSES = {
    "Not started", "In progress", "Blocked",
    "Implemented", "Tested", "Verified complete",
}
PHASE_ENDS = (21, 60, 113, 162, 217, 257, 324, 349, 360, 378, 395)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read an audited CSV file using deterministic UTF-8 handling.

    Return the original source column names and rows without deduplication.
    """
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_roadmap_has_exactly_395_ordered_entries() -> None:
    """Reject incomplete or reordered source inventory entries."""

    rows = read_csv(ROOT / "docs/requirements/roadmap_inventory.csv")
    assert len(rows) == 395
    assert [int(row["order"]) for row in rows] == list(range(1, 396))
    assert len({row["file_or_folder"] for row in rows}) == 395


def test_roadmap_phase_and_priority_are_valid() -> None:
    """Check the PDF's file-order boundaries and allowed priorities."""

    rows = read_csv(ROOT / "docs/requirements/roadmap_inventory.csv")
    for row in rows:
        order = int(row["order"])
        expected_phase = next(i for i, maximum in enumerate(PHASE_ENDS) if order <= maximum)
        assert int(row["phase"]) == expected_phase
        assert row["priority"] in {"Critical", "High", "Medium", "Low"}
        assert row["status"] in ALLOWED_STATUSES


def test_implemented_files_exist() -> None:
    """Never mark absent source paths as implemented."""

    rows = read_csv(ROOT / "docs/requirements/roadmap_inventory.csv")
    for row in rows:
        if row["status"] in {"Implemented", "Tested", "Verified complete"}:
            assert (ROOT / row["file_or_folder"]).exists(), row["file_or_folder"]


def test_functional_control_register_is_complete() -> None:
    """Track 77 independent cross-cutting control requirements."""

    rows = read_csv(ROOT / "docs/requirements/functional_requirements.csv")
    assert len(rows) == 77
    assert [row["requirement_id"] for row in rows] == [
        f"FUNC-{index:03d}" for index in range(1, 78)
    ]
    for row in rows:
        assert row["requirement"]
        assert row["roadmap_page"].startswith("PDF page ")
        assert row["status"] in ALLOWED_STATUSES
        assert row["status"] != "Verified complete" or row["verification_result"]

def test_tested_rows_have_test_and_execution_evidence() -> None:
    """Reject test-status promotion without a source and verification record."""
    rows = read_csv(ROOT / "docs/requirements/roadmap_inventory.csv")
    for row in rows:
        if row["status"] in {"Tested", "Verified complete"}:
            assert row["test_reference"].strip(), row["file_or_folder"]
            assert row["verification_result"].strip(), row["file_or_folder"]
