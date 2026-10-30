# ScoutMasterAPI-builder

This repository contains the ScoutMaster API, which provides a robust interface for managing and accessing various functionalities of the ScoutMaster platform. This Python repository facilitates communication with the API.

For detailed API documentation, you can visit the Swagger page [here](https://api.scoutmaster.nl/api-docs).

## Development

This repository is public. Anything committed here, including notebook
outputs, can be read by anyone, so set up the local checks once per clone:

```bash
pip install -e ".[dev]"
pre-commit install
```

From then on every `git commit`:

- runs **gitleaks** on the staged changes and stops the commit if something
  looks like a secret (client secrets, tokens, keys). `.gitleaks.toml` adds a
  rule for Cognito client secrets, which the default rules miss;
- runs **nbstripout**, which removes notebook outputs. If it changed a
  notebook, the commit stops once: review the notebook, `git add` it again and
  commit.

Never commit credentials or `.env` files; read them from the environment
(`SM_CLIENT_ID`, `SM_CLIENT_SECRET`) instead.

### Tests

```bash
pytest tests -v
```

- `tests/test_spec_coverage.py` compares the client with the live API spec:
  every endpoint has a method, no method calls an unknown path, ⚠️ Conceptual
  warnings and `lang` support match the spec. Set `SCOUTMASTER_SPEC` to test
  against another spec (file or URL), e.g.
  `https://dev-api.scoutmaster.nl/swagger-v3-full.json`.
- `tests/test_notebooks.py` fails when a notebook contains outputs.

GitHub Actions (`.github/workflows/tests.yml`) runs the tests against the
production API on every push and pull request and nightly, the spec tests
against the dev API as a non-blocking early warning, and a gitleaks scan of
new commits and current files.

### New API endpoints: generate them

When the API gains endpoints (the spec test then lists them), generate client
methods for them from the OpenAPI spec:

```bash
python scripts/generate_endpoints.py           # from the production spec
python scripts/generate_endpoints.py --dev     # from the dev spec
python scripts/generate_endpoints.py --check   # only report; exit 1 if out of date
```

The script downloads `https://api.scoutmaster.nl/swagger-v3-full.json`, finds
every operation no hand-written method covers (the same check as the spec
test, shared in `scripts/spec_coverage.py`) and writes a method for each to
`scoutmasterapi_builder/generated.py`, following the client's conventions:
path and query parameters and JSON body fields become arguments, `lang`
defaults to the client's language, list endpoints fetch all pages, file
uploads use multipart, list and GeoJSON responses go through
`output_format`, and ⚠️ Conceptual endpoints warn.

`generated.py` is rewritten on every run, so never edit it. `ScoutMasterAPI`
includes it last, so hand-written methods always win: to give an endpoint a
better method (a nicer name, validation, defaults), write it in the right
module and run the generator again; it then drops the generated one.
Endpoints the client should never wrap go in `EXCLUDED` in
`scripts/spec_coverage.py`. After generating: review the file, run
`pytest tests`, bump the version and build the wheel.

The generator only adds missing endpoints. Changes to existing endpoints (e.g.
a new query parameter) still show up in the spec test and need a hand-written
update.