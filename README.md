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