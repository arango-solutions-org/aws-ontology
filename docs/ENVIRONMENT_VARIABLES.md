# Environment Variables

Every variable the project's tools and tests read. Nothing else is consulted.

## ArangoDB import (`tools/import_to_arangodb.py`)

| Variable | Purpose | Default |
|----------|---------|---------|
| `ARANGO_PASSWORD` | Password for the ArangoDB user. **Required** unless `--password` is given; there is no built-in default. | — |
| `ARANGO_HOST` | ArangoDB endpoint | `http://localhost:8529` |
| `ARANGO_USERNAME` | ArangoDB user | `root` |
| `ARANGO_DATABASE` | Target database (created if missing) | `aws_ontology` |

Command-line flags (`--password`, `--host`, `--username`, `--database`) override these.

```bash
export ARANGO_PASSWORD='choose-a-strong-password'
export ARANGO_HOST='https://my-arango.example.com:8529'
python tools/import_to_arangodb.py --test-queries
```

Keep credentials out of the repository: use your shell profile, a secrets manager, or an
untracked `.env` file (`.env` is already in `.gitignore`).

## Ontology coverage monitor (`tools/propose_ontology_updates.py`)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key used to triage AWS "What's New" items. In GitHub Actions this comes from the `OPENAI_API_KEY` repository secret. |
| `OPENAI_MODEL` | Optional. OpenAI model to use (default `gpt-5.5`). In GitHub Actions this comes from the `OPENAI_MODEL` repository variable. |
| `ANTHROPIC_API_KEY` | Claude API key; an alternative to `OPENAI_API_KEY`, used instead of it when both are set. In GitHub Actions this comes from the `ANTHROPIC_API_KEY` repository secret. |
| `GITHUB_OUTPUT` | Set automatically by GitHub Actions; the tool writes `findings` / `proposal_path` outputs there. |

Install the tool's dependencies with `uv sync --group monitor`. To run it locally with the key
in `.env`: `uv run --group monitor --env-file .env python tools/propose_ontology_updates.py`.

## Tests

| Variable | Purpose |
|----------|---------|
| `REQUIRE_REASONER=1` | Fail (instead of skip) the HermiT consistency test when no Java runtime is available. Set in CI. |
| `ARANGO_TEST_HOST` | Enables `tests/test_arangodb_import.py` against this ArangoDB endpoint (uses `ARANGO_PASSWORD`). The test creates and drops its own uniquely named databases. Set in CI. |

```bash
# Full local run, including the live-ArangoDB integration test
docker run -d --rm --name arango-test -e ARANGO_ROOT_PASSWORD=test-only \
  -p 127.0.0.1:8529:8529 arangodb:3.12
ARANGO_TEST_HOST=http://127.0.0.1:8529 ARANGO_PASSWORD=test-only REQUIRE_REASONER=1 uv run pytest
docker stop arango-test
```

## Scheduled monitoring (`automation/`)

`automation/schedule_monitoring.py` is configured through a JSON file
(`--config automation/config.json`; create a sample with `make schedule-setup`), not through
environment variables. Keep SMTP credentials in that file out of version control.
