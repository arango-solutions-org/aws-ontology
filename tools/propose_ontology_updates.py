#!/usr/bin/env python3
"""
Agentic ontology-update monitor.

Checks the AWS "What's New" feed for services/features the ontology doesn't
cover yet, using an LLM (Claude or OpenAI) to triage against the PRD's declared scope. Writes a
dated proposal document (never touches ontology/aws.ttl directly — proposed
classes are drafts for a human, or a future interactive session, to verify
and integrate with the same rigor as every other addition in this repo: real
ARN formats, domain/range checks, SHACL validation, tests).

Requires ANTHROPIC_API_KEY (Claude) or OPENAI_API_KEY (OpenAI; model from OPENAI_MODEL,
default gpt-5.5). If both are set, Claude is used. Designed to run from .github/workflows/
ontology-monitor.yml on a schedule; exits 0 with no output file when nothing
new is found, so the workflow only opens an issue when there's something to review.

Usage:
    python tools/propose_ontology_updates.py --days 8
    python tools/propose_ontology_updates.py --days 8 --output-dir docs/proposals
    uv run --group monitor --env-file .env python tools/propose_ontology_updates.py  # key in .env
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.monitor_aws_changes import AWSChangeMonitor  # noqa: E402
from utils.logging_config import setup_tool_logging  # noqa: E402

FINDINGS_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "service_name": {"type": "string"},
                    "is_new": {
                        "type": "boolean",
                        "description": "True only if this is a service or major feature area not "
                        "already listed in 'covered' or 'roadmap' below.",
                    },
                    "rationale": {"type": "string"},
                    "candidate_classes": {"type": "array", "items": {"type": "string"}},
                    "candidate_properties": {"type": "array", "items": {"type": "string"}},
                    "example_arn_format": {
                        "type": ["string", "null"],
                        "description": "A real AWS ARN format for this service, or null if the "
                        "service genuinely has no ARN-addressable resources.",
                    },
                    "source_link": {"type": "string"},
                },
                "required": [
                    "service_name",
                    "is_new",
                    "rationale",
                    "candidate_classes",
                    "candidate_properties",
                    "example_arn_format",
                    "source_link",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["findings"],
    "additionalProperties": False,
}


def extract_prd_scope(prd_text: str) -> tuple[str, str]:
    """Pull the §3 Scope and Future scope bullet lists out of the PRD as plain text."""
    scope_match = re.search(r"## 3\. Scope\s*\n(.*?)(?=### Future scope|## 4\.)", prd_text, re.S)
    roadmap_match = re.search(r"### Future scope.*?\n(.*?)(?=## 4\.)", prd_text, re.S)
    covered = scope_match.group(1).strip() if scope_match else ""
    roadmap = roadmap_match.group(1).strip() if roadmap_match else ""
    return covered, roadmap


def build_prompt(changes: list[dict], covered: str, roadmap: str) -> str:
    items = "\n".join(f"- {c['title']}: {c['description'][:300]} ({c['link']})" for c in changes)
    return f"""You are triaging AWS "What's New" announcements against an existing OWL ontology's coverage.

ALREADY COVERED (do not flag these as new):
{covered}

ON THE ROADMAP (already known gaps, not new discoveries):
{roadmap}

RECENT AWS ANNOUNCEMENTS:
{items}

For each announcement that represents a genuinely NEW AWS service or major feature area not
already listed above, propose ontology additions: a service_name, why it's new (rationale),
candidate OWL class names (PascalCase, matching this ontology's naming convention), candidate
object/datatype property names (camelCase), and a real AWS ARN format for the service if one
exists (arn:aws:... — set to null if the service has no ARN-addressable resources, e.g. it's a
sub-object or a purely account-level setting). Minor feature updates to already-covered services
are NOT new — set is_new to false for those, or omit them entirely. Be conservative: only flag
something as_new if you're confident it's a distinct service, not a feature of an existing one."""


def call_claude(prompt: str) -> dict:
    import anthropic

    client = anthropic.Anthropic()
    # fallbacks="default": if a safety classifier declines, the API re-runs the request on a
    # suitable fallback model within the same call instead of stopping with a refusal.
    response = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={
            "effort": "medium",
            "format": {"type": "json_schema", "schema": FINDINGS_SCHEMA},
        },
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude declined the request: {response.stop_details}")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def call_openai(prompt: str) -> dict:
    from openai import OpenAI

    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL") or "gpt-5.5",
        max_output_tokens=16000,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "findings",
                "schema": FINDINGS_SCHEMA,
                "strict": True,
            }
        },
    )
    for item in response.output:
        for part in getattr(item, "content", None) or []:
            if part.type == "refusal":
                raise RuntimeError(f"OpenAI declined the request: {part.refusal}")
    if response.status != "completed":
        raise RuntimeError(f"OpenAI response {response.status}: {response.incomplete_details}")
    return json.loads(response.output_text)


def call_llm(prompt: str) -> dict:
    """Use Claude when ANTHROPIC_API_KEY is set, otherwise OpenAI."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return call_claude(prompt)
    return call_openai(prompt)


def write_proposal(findings: list[dict], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = output_dir / f"{date_str}-monitor-findings.md"

    lines = [
        f"# Ontology Coverage Proposal — {date_str}",
        "",
        'Generated by `tools/propose_ontology_updates.py` from the AWS "What\'s New" feed.',
        "These are draft proposals only — no ontology files were modified. Each candidate class",
        "and property needs the same verification as every other addition in this repo: check the",
        "ARN format is real, confirm domain/range, add example instances, run the test suite and",
        "SHACL validation before merging into `ontology/aws.ttl`.",
        "",
    ]
    for f in findings:
        lines.append(f"## {f['service_name']}")
        lines.append("")
        lines.append(f"**Why it's new:** {f['rationale']}")
        lines.append("")
        lines.append(f"**Source:** {f['source_link']}")
        lines.append("")
        if f["candidate_classes"]:
            lines.append(
                "**Candidate classes:** " + ", ".join(f"`{c}`" for c in f["candidate_classes"])
            )
        if f["candidate_properties"]:
            lines.append(
                "**Candidate properties:** "
                + ", ".join(f"`{p}`" for p in f["candidate_properties"])
            )
        arn = f["example_arn_format"]
        lines.append(
            f"**Example ARN format:** {'`' + arn + '`' if arn else 'None (verify before assuming)'}"
        )
        lines.append("")

    out_path.write_text("\n".join(lines))
    return out_path


def set_github_output(name: str, value: str) -> None:
    gh_output = os.getenv("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as fh:
            fh.write(f"{name}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Propose ontology updates from AWS feed changes")
    parser.add_argument("--days", type=int, default=8, help="Lookback window in days")
    parser.add_argument(
        "--output-dir", default="docs/proposals", help="Directory for the proposal document"
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_tool_logging("propose_ontology_updates", args.verbose)

    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")):
        logging.error("Neither ANTHROPIC_API_KEY nor OPENAI_API_KEY is set")
        return 1

    monitor = AWSChangeMonitor()
    changes = monitor.monitor_whats_new(days=args.days)
    if not changes:
        logging.info("No AWS announcements in the lookback window")
        set_github_output("findings", "false")
        return 0

    prd_text = (project_root / "docs" / "PRD.md").read_text()
    covered, roadmap = extract_prd_scope(prd_text)

    prompt = build_prompt(changes, covered, roadmap)
    result = call_llm(prompt)
    new_findings = [f for f in result["findings"] if f["is_new"]]

    if not new_findings:
        logging.info("No new-service findings among %d announcements", len(changes))
        set_github_output("findings", "false")
        return 0

    out_path = write_proposal(new_findings, project_root / args.output_dir)
    logging.info("Wrote %d finding(s) to %s", len(new_findings), out_path)
    set_github_output("findings", "true")
    set_github_output("proposal_path", str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
