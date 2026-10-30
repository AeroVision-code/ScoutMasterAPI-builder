"""Checks the client against the ScoutMaster OpenAPI spec.

Every public method is called with dummy arguments against a fake transport,
recording which (method, path, query parameters) it requests. The tests then
fail when:
  - the spec has an operation no client method calls,
  - a client method calls a path that isn't in the spec,
  - a method's ⚠️ Conceptual warning doesn't match the spec,
  - `lang` is missing where the endpoint accepts it, or sent where it doesn't.

The recording and matching live in scripts/spec_coverage.py, shared with
scripts/generate_endpoints.py (which writes methods for missing operations).

The spec is downloaded from SPEC_URL; set SCOUTMASTER_SPEC to a local file or
another URL to override. Tests are skipped when the spec can't be loaded,
or fail instead when SCOUTMASTER_SPEC_REQUIRED is set (as in CI).

Run with:  pytest tests
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import spec_coverage as sc  # noqa: E402

from scoutmasterapi_builder.api import ScoutMasterAPI  # noqa: E402


@pytest.fixture(scope="module")
def spec():
    source = os.getenv("SCOUTMASTER_SPEC", sc.SPEC_URL)
    try:
        return sc.load_spec(source)
    except Exception as e:
        if os.getenv("SCOUTMASTER_SPEC_REQUIRED"):
            pytest.fail(f"Could not load spec from {source}: {e}")
        pytest.skip(f"Could not load spec from {source}: {e}")


@pytest.fixture(scope="module")
def spec_ops(spec):
    """[(HTTP method, path template, path regex, operationId, is_conceptual, query param names, ...)]"""
    return sc.spec_operations(spec)


@pytest.fixture(scope="module")
def recorded():
    """({method name: [(HTTP method, path, query param names)]}, warned names)"""
    return sc.record_calls(ScoutMasterAPI)


def _match(spec_ops, method, path):
    return sc.match(spec_ops, method, path)


def test_every_spec_operation_has_a_method(spec_ops, recorded):
    calls, _ = recorded
    missing = sorted(f"{op[0]} {op[1]} ({op[3]})" for op in sc.missing_operations(spec_ops, calls))
    assert not missing, (
        "Spec operations without a client method:\n" + "\n".join(missing)
        + "\n\nGenerate methods for them with:  python scripts/generate_endpoints.py"
    )


def test_no_calls_outside_spec(spec_ops, recorded):
    calls, _ = recorded
    unknown = sorted(f"{name}: {m} {p}" for name, reqs in calls.items()
                     for m, p, _q in reqs if not _match(spec_ops, m, p))
    assert not unknown, "Client calls that aren't in the spec:\n" + "\n".join(unknown)


def test_conceptual_warnings_match_spec(spec_ops, recorded):
    calls, warned = recorded
    wrong = []
    for name, reqs in sorted(calls.items()):
        matched = [op for m, p, _q in reqs if (op := _match(spec_ops, m, p))]
        if not matched:
            continue
        should_warn = any(op[4] for op in matched)
        if should_warn != (name in warned):
            wrong.append(f"{name}: warns={name in warned}, spec conceptual={should_warn}")
    assert not wrong, "Conceptual markers out of sync with the spec:\n" + "\n".join(wrong)


def test_lang_sent_exactly_where_supported(spec_ops, recorded):
    """Every request to an endpoint with a `lang` query parameter sends the
    client's language; no other request sends one."""
    calls, _ = recorded
    wrong = []
    for name, reqs in sorted(calls.items()):
        for m, p, query in reqs:
            op = _match(spec_ops, m, p)
            if not op:
                continue
            supported, sent = "lang" in op[5], "lang" in query
            if supported != sent:
                wrong.append(f"{name}: {m} {op[1]} {'misses' if supported else 'sends unsupported'} lang")
    assert not wrong, "lang query parameter out of sync with the spec:\n" + "\n".join(wrong)
