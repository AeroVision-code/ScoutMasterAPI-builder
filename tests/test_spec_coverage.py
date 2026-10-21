"""Checks the client against the ScoutMaster OpenAPI spec.

Every public method is called with dummy arguments against a fake transport,
recording which (method, path, query parameters) it requests. The tests then
fail when:
  - the spec has an operation no client method calls,
  - a client method calls a path that isn't in the spec,
  - a method's ⚠️ Conceptual warning doesn't match the spec,
  - `lang` is missing where the endpoint accepts it, or sent where it doesn't.

The spec is downloaded from SPEC_URL; set SCOUTMASTER_SPEC to a local file or
another URL to override. Tests are skipped when the spec can't be loaded,
or fail instead when SCOUTMASTER_SPEC_REQUIRED is set (as in CI).

Run with:  pytest tests
"""
import inspect
import json
import os
import re
import tempfile
import warnings
from urllib.parse import parse_qs, urlsplit

import pytest
import requests

from scoutmasterapi_builder.api import ScoutMasterAPI

SPEC_URL = "https://api.scoutmaster.nl/swagger-v3-full.json"

# Spec operations the client deliberately doesn't wrap.
EXCLUDED = {
    # Browser sign-in steps and the callback the eID wallet app posts to.
    "LoginOffer", "Signup", "VerifySignup", "DeeplinkResult", "WalletCallback",
    # Managing your own account: the API only allows this for people signed in
    # through the frontend (requireOwnFrontendUser), never for an API client.
    "DeleteMe", "GetMyDeletionCheck",
}

# Dummy values for arguments that are validated before any request is made.
SPECIAL_ARGS = {
    "reason": "other", "zone_type": 1, "role": "member", "ref_type": "field",
    "layer_ids": [1], "tbase": 5, "tupper": 30, "value": 1,
    "cultivation_ids": ["c"], "peergroup_cultivation_ids": ["c"],
}
EXTRA_ARGS = {
    "field_zone_update": {"name": "n"},
    "environment_user_add": {"user_id": "u"},
}


class _FakeResponse:
    status_code = 200
    ok = True
    text = ""
    content = b"{}"

    def json(self):
        return {"data": {"upload_url": "u", "job_id": "j", "s3_key": "k"}}


@pytest.fixture(scope="module")
def spec():
    source = os.getenv("SCOUTMASTER_SPEC", SPEC_URL)
    try:
        if source.startswith("http"):
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            return response.json()
        with open(source, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:
        if os.getenv("SCOUTMASTER_SPEC_REQUIRED"):
            pytest.fail(f"Could not load spec from {source}: {e}")
        pytest.skip(f"Could not load spec from {source}: {e}")


@pytest.fixture(scope="module")
def spec_ops(spec):
    """[(HTTP method, path template, path regex, operationId, is_conceptual, query param names)]"""
    def resolve(obj):
        while isinstance(obj, dict) and "$ref" in obj:
            node = spec
            for part in obj["$ref"].lstrip("#/").split("/"):
                node = node[part]
            obj = node
        return obj

    ops = []
    for path, item in spec["paths"].items():
        for method, op in item.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue
            regex = re.compile("^" + re.sub(r"\{[^}]+\}", "[^/]+", path.lstrip("/")) + "$")
            conceptual = "Conceptual" in (op.get("summary") or "")
            query = frozenset(p["name"] for p in map(resolve, op.get("parameters", []))
                              if p.get("in") == "query")
            ops.append((method.upper(), path, regex, op["operationId"], conceptual, query))
    return ops


@pytest.fixture(scope="module")
def recorded():
    """Call every public method; return
    ({method name: [(HTTP method, path, query param names)]}, warned names)."""
    api = ScoutMasterAPI(verbose=False, output_format="json")
    api.access_token, api._token_expiry = "token", float("inf")
    calls = {}
    current = [None]

    def fake_request(method, endpoint, **kwargs):
        url = urlsplit(endpoint)
        query = set(parse_qs(url.query)) | set(kwargs.get("params") or {})
        calls.setdefault(current[0], []).append((method, url.path.rstrip("/"), frozenset(query)))
        return _FakeResponse()

    api._request = fake_request
    api.upload_file = lambda *a, **k: None

    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    tmp.close()
    warned = set()
    try:
        for name, fn in inspect.getmembers(ScoutMasterAPI, inspect.isfunction):
            if name.startswith("_") or name in ("authenticate", "set_access_token", "upload_file"):
                continue
            current[0] = name
            args = {}
            for p in list(inspect.signature(fn).parameters.values())[1:]:
                if p.default is inspect.Parameter.empty and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                    args[p.name] = tmp.name if p.name == "file_path" else SPECIAL_ARGS.get(p.name, "ID")
            args.update(EXTRA_ARGS.get(name, {}))
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                try:
                    getattr(api, name)(**args)
                except Exception:
                    # Legacy wrappers that expect structured input fail on
                    # dummy args; their endpoints are covered by other methods.
                    pass
            if any("Conceptual" in str(w.message) for w in caught):
                warned.add(name)
    finally:
        os.unlink(tmp.name)
    return calls, warned


def _match(spec_ops, method, path):
    hits = [op for op in spec_ops if op[0] == method and op[2].match(path)]
    # Prefer literal segments, e.g. users/me over users/{userId}.
    return min(hits, key=lambda op: op[1].count("{")) if hits else None


def test_every_spec_operation_has_a_method(spec_ops, recorded):
    calls, _ = recorded
    covered = {op[3] for reqs in calls.values() for m, p, _q in reqs if (op := _match(spec_ops, m, p))}
    missing = sorted(f"{op[0]} {op[1]} ({op[3]})" for op in spec_ops
                     if op[3] not in covered and op[3] not in EXCLUDED)
    assert not missing, "Spec operations without a client method:\n" + "\n".join(missing)


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
