# DFIR Investigation Report Template

Standard structure for a final investigative report — written for a mixed audience (technical responders + executive/legal readers), which is why the executive summary and technical findings are deliberately separated rather than interleaved.

## Report Structure

```markdown
# Incident Report: [Case Name/ID]

**Classification:** [Confidential / Internal / etc.]
**Report Date:** [Date]
**Investigator(s):** [Name(s)]
**Case Reference:** [Case tracking ID]

## Executive Summary
2-4 sentences: what happened, what was the impact, is it resolved.
Written for a non-technical reader — no jargon, no acronyms without
expansion. This is the section leadership and legal will actually read.

## Scope and Objectives
- What prompted the investigation
- What was in scope (systems, timeframe, data types)
- What was explicitly out of scope, if relevant

## Timeline of Events
Chronological summary of key events — pull from the merged super-timeline
(see tooling/timeline-correlation/) but present only the events that matter
to the narrative, not the raw data dump. Every entry should answer "why does
this matter to the story."

| Timestamp (UTC) | Event | Source |
|---|---|---|
| | | |

## Technical Findings
Detailed technical analysis — this is where full detail belongs, unlike the
executive summary. Organize by phase (initial access, execution, persistence,
lateral movement, exfiltration/impact) rather than chronologically if the
incident is complex; map findings to MITRE ATT&CK technique IDs where
applicable.

## Evidence Summary
Reference the case export from tooling/case-tracker/ — list evidence items,
their SHA-256 hashes, and a one-line description of what each contributed to
the investigation. Full chain-of-custody detail lives in the case tracker
export, not duplicated here — reference it.

## Indicators of Compromise (IOCs)
Table of IOCs identified, pulled from the case tracker's IOC log. Format for
direct import into detection tooling where possible (CSV/STIX if your
downstream tooling consumes it).

## Root Cause
What allowed this to happen — the specific vulnerability, misconfiguration,
or gap. Avoid vague causes ("lack of security awareness") in favor of
specific, actionable ones ("no MFA enforced on the VPN, which was the sole
authentication factor exploited").

## Remediation Actions Taken
What was done during the response (containment, eradication steps) — past
tense, factual, tied to timestamps where possible.

## Recommendations
Forward-looking, prioritized. Separate "must do before closing this
incident" from "should do to prevent recurrence" from "nice to have."
Vague recommendations ("improve security posture") are not actionable —
every recommendation should be specific enough that someone could pick it
up and start work without asking a clarifying question first.

## Appendices
- Full technical logs / raw evidence references
- Tools and methodology used
- Analyst notes not essential to the main narrative but useful for future reference
```

## Writing Guidance

- **Executive summary gets written last, even though it appears first.** You don't know what actually mattered until the investigation is done.
- **Every claim should be traceable to evidence.** If a statement in the report can't be backed by a specific log entry, evidence item, or IOC in the case tracker, either find the backing evidence or soften the claim to "suspected" / "consistent with."
- **Avoid speculation about attacker identity/attribution** unless genuinely warranted and defensible — most internal DFIR reports don't need it, and unfounded attribution claims create legal and reputational risk disproportionate to their investigative value.

---
*Part of the [digital-forensics-dfir-toolkit](../README.md) repository.*
