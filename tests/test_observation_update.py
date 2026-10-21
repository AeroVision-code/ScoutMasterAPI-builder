"""observation_update() sends only the fields it is given, and None for
research_category_id clears the category instead of being left out.

Run with:  pytest tests
"""
import warnings

import pytest

from scoutmasterapi_builder.api import ScoutMasterAPI


class _FakeResponse:
    status_code = 200
    ok = True
    text = ""
    content = b"{}"

    def json(self):
        return {"data": {}}


@pytest.fixture
def sent():
    """The (HTTP method, endpoint, JSON body) of every request made."""
    api = ScoutMasterAPI(verbose=False, output_format="json")
    api.access_token, api._token_expiry = "token", float("inf")
    calls = []

    def fake_request(method, endpoint, **kwargs):
        calls.append((method, endpoint, kwargs.get("json")))
        return _FakeResponse()

    api._request = fake_request
    warnings.filterwarnings("ignore", message=r".*Conceptual ScoutMaster endpoint.*")
    return api, calls


def test_category_set(sent):
    api, calls = sent
    api.observation_update("o1", research_category_id=7)
    assert calls == [("PATCH", "observations/o1", {"research_category_id": 7})]


def test_category_cleared_with_none(sent):
    api, calls = sent
    api.observation_update("o1", research_category_id=None)
    assert calls == [("PATCH", "observations/o1", {"research_category_id": None})]


def test_category_left_out_when_not_given(sent):
    api, calls = sent
    api.observation_update("o1", reference_code="R1")
    assert calls == [("PATCH", "observations/o1", {"reference_code": "R1"})]
