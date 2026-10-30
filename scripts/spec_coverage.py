"""Compare the client with the ScoutMaster OpenAPI spec.

Shared by tests/test_spec_coverage.py and scripts/generate_endpoints.py, so the
test and the generator agree on which spec operations the client covers.

Coverage is measured by behaviour, not by names: every public method is called
with dummy arguments against a fake transport, and the (HTTP method, path,
query parameters) it requests are matched against the spec's operations.
"""
import inspect
import json
import os
import re
import tempfile
import warnings
from collections import namedtuple
from urllib.parse import parse_qs, urlsplit

import requests

SPEC_URLS = {
    "prod": "https://api.scoutmaster.nl/swagger-v3-full.json",
    "dev": "https://dev-api.scoutmaster.nl/swagger-v3-full.json",
}
SPEC_URL = SPEC_URLS["prod"]

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
# Public methods that don't call the API.
NOT_ENDPOINTS = {"authenticate", "set_access_token", "upload_file"}

HTTP_METHODS = ("get", "post", "put", "patch", "delete")

# One spec operation. Fields 0-5 keep the tuple layout the tests index into.
Operation = namedtuple(
    "Operation", "method path regex operation_id conceptual query definition")


def load_spec(source=SPEC_URL):
    """Load an OpenAPI spec from a URL or a local file."""
    if source.startswith(("http://", "https://")):
        response = requests.get(source, timeout=30)
        response.raise_for_status()
        return response.json()
    with open(source, encoding="utf-8") as fh:
        return json.load(fh)


def resolve(spec, obj):
    """Follow `$ref`s (e.g. '#/components/schemas/UUID') to the object they point to."""
    while isinstance(obj, dict) and "$ref" in obj:
        node = spec
        for part in obj["$ref"].lstrip("#/").split("/"):
            node = node[part]
        obj = node
    return obj


def spec_operations(spec):
    """All operations in the spec, as Operation tuples."""
    ops = []
    for path, item in spec["paths"].items():
        for method, op in item.items():
            if method not in HTTP_METHODS:
                continue
            regex = re.compile("^" + re.sub(r"\{[^}]+\}", "[^/]+", path.lstrip("/")) + "$")
            conceptual = "Conceptual" in (op.get("summary") or "")
            query = frozenset(p["name"] for p in (resolve(spec, p) for p in op.get("parameters", []))
                              if p.get("in") == "query")
            ops.append(Operation(method.upper(), path, regex, op["operationId"], conceptual, query, op))
    return ops


class _FakeResponse:
    status_code = 200
    ok = True
    text = ""
    content = b"{}"

    def json(self):
        return {"data": {"upload_url": "u", "job_id": "j", "s3_key": "k"}}


def record_calls(client_cls):
    """Call every public method of `client_cls` against a fake transport.

    Returns:
        tuple: ({method name: [(HTTP method, path, query param names)]},
        names of the methods that emitted a Conceptual warning).
    """
    api = client_cls(verbose=False, output_format="json")
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
        for name, fn in inspect.getmembers(client_cls, inspect.isfunction):
            if name.startswith("_") or name in NOT_ENDPOINTS:
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


def match(ops, method, path):
    """The spec operation a request goes to, or None."""
    hits = [op for op in ops if op.method == method and op.regex.match(path)]
    # Prefer literal segments, e.g. users/me over users/{userId}.
    return min(hits, key=lambda op: op.path.count("{")) if hits else None


def missing_operations(ops, calls):
    """Spec operations no recorded call reaches, except the EXCLUDED ones."""
    covered = {op.operation_id for reqs in calls.values()
               for m, p, _q in reqs if (op := match(ops, m, p))}
    return [op for op in ops if op.operation_id not in covered and op.operation_id not in EXCLUDED]
