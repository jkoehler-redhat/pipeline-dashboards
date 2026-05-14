# Pipeline Registry

Each pipeline is one row. Stage groupings, deduplication priority, and rate formulas are documented in `pipeline-tracker/references/{pipeline}.md`.

## Dashboard Cards

| Pipeline | Hero Metric | Card Sub-text | Card Pills | Anchor |
|----------|-------------|---------------|------------|--------|
| jira-autofix | merged count | "PRs merged · {N}% success rate" | merged (green), failed (red), blocked (yellow) | `#autofix` |
| rfe-creator | rubric pass count | "rubric pass · {N} auto-created" | rubric pass (green), created (blue), attention (yellow) | `#rfe` |
| strat-creator | rubric pass count | "rubric pass · {N} auto-created" | rubric pass (green), created (blue), attention (yellow) | `#strat` |
| test-plan | rubric pass count | "rubric pass · {N} auto-created" | rubric pass (green), rubric fail (red), auto-revised (blue) | `#testplan` |
| doc-pipeline | contributed count | "docs contributed · {N} invoked" | contributed (green), invoked (blue), queued (yellow) | `#docpipeline` |
| component-onboarding | completed count | "completed · {N} in review" | completed (green), in review (blue), failed (red) | `#onboarding` |

## Attention Labels

| Pipeline | Attention Labels | Section Title |
|----------|-----------------|---------------|
| jira-autofix | `jira-autofix-blocked`, `jira-autofix-max-retries` | Blocked & Max-Retries |
| rfe-creator | `rfe-creator-needs-attention` | Needs Attention |
| strat-creator | `strat-creator-needs-attention` | Needs Attention |
| test-plan | `test-plan-rubric-fail` | Quality Failures |
| doc-pipeline | *(none)* | |
| component-onboarding | `validation-failed`, `renovate-sync-failed` | Validation & Sync Failures |

## Source Links

| Pipeline | Source URL |
|----------|-----------|
| component-onboarding | `https://github.com/opendatahub-io/aiops-infra/tree/review/.claude/skills/create-component-onboarding-jira` |
