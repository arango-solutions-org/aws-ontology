# DEPRECATED — superseded by the GitHub Actions ontology monitor

This directory's scheduling daemon (`schedule_monitoring.py` + the Docker/systemd/cron
deployment mechanisms alongside it) is superseded by
[`.github/workflows/ontology-monitor.yml`](../.github/workflows/ontology-monitor.yml), which
runs on a GitHub Actions schedule, calls an LLM (OpenAI or Claude) to triage AWS "What's New" announcements against
the PRD's declared scope, and opens an issue with proposed additions — see
[`tools/propose_ontology_updates.py`](../tools/propose_ontology_updates.py).

**Known bugs, left unfixed since this code is being replaced, not maintained:**
- `schedule_monitoring.py`'s `schedule.every().month` / `schedule.every(3).months` calls crash —
  the `schedule` library has no monthly unit.
- Its `strftime('%Y_Q%q')` uses `%q`, which is not a valid strftime directive.

**Requires:** an `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` repository secret (Settings → Secrets and variables →
Actions) to enable the new workflow. Without it, the workflow fails loudly on each scheduled run
rather than silently doing nothing.

This directory is kept for reference but should not be relied on. If you're setting up AWS
change monitoring for this repo, use the GitHub Actions workflow instead.
