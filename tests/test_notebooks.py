"""Notebooks must be committed without outputs.

Outputs of real API calls end up in a public repo otherwise: credentials
printed while authenticating, presigned S3 links, user emails, field
addresses. Clear them before committing, e.g.:

    jupyter nbconvert --clear-output --inplace examples/**/*.ipynb

or once per clone, strip them automatically on every commit:

    pip install nbstripout && nbstripout --install
"""
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
NOTEBOOKS = sorted(p for p in REPO.rglob("*.ipynb")
                   if not any(part.startswith(".") for part in p.relative_to(REPO).parts))


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: str(p.relative_to(REPO)))
def test_notebook_has_no_outputs(path):
    nb = json.loads(path.read_text(encoding="utf-8"))
    with_output = [i for i, cell in enumerate(nb.get("cells", []))
                   if cell.get("cell_type") == "code" and cell.get("outputs")]
    assert not with_output, (
        f"{path.relative_to(REPO)} has outputs in cell(s) {with_output}; "
        "clear them before committing (see tests/test_notebooks.py)."
    )
