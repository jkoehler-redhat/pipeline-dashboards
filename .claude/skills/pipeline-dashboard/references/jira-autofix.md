# jira-autofix

The jira-autofix pipeline is a bot that picks up Jira tickets, creates MRs/PRs, and iterates through CI and review feedback. Issues move through labels as the bot processes them. Source: `opendatahub-io/autofix-skills` (inner layer); `gitlab.com/redhat/rhel-ai/agentic-ci/jira-autofix` (outer layer — `verdict.py`). Verdict values in skill `SKILL.md` files map to `jira-autofix-*` labels via `verdict.py`.

**Projects with labels today**: TP, RHOAIENG, AIPCC, INFERENG, RHAIENG, RHAIFIRST

## Labels (9 total)

| Label | Stage | Meaning |
|-------|-------|---------|
| `jira-autofix` | Queue | Ticket ready for bot pickup |
| `jira-autofix-pending` | Active | Bot currently processing |
| `jira-autofix-review` | Active | MR/PR created, iterating on review feedback |
| `jira-autofix-ci-failing` | Active | Pipeline broken on MR/PR; bot will retry |
| `jira-autofix-merged` | Terminal (success) | MR/PR merged |
| `jira-autofix-rejected` | Terminal (failure) | MR/PR closed without merge |
| `jira-autofix-max-retries` | Terminal (failure) | Bot hit iteration limit, needs human takeover |
| `jira-autofix-researched` | Terminal (neutral) | Research findings posted; no MR created |
| `jira-autofix-blocked` | Stuck | Bot needs more info; remove label to retry |

## Stage Groupings

| Group | Labels |
|-------|--------|
| Queue | `jira-autofix` |
| Active | `jira-autofix-pending`, `jira-autofix-review`, `jira-autofix-ci-failing` |
| Completed | `jira-autofix-merged` |
| Failed | `jira-autofix-rejected`, `jira-autofix-max-retries` |
| Researched | `jira-autofix-researched` |
| Blocked | `jira-autofix-blocked` |

## Deduplication Priority (highest wins)

1. `jira-autofix-merged`
2. `jira-autofix-rejected`
3. `jira-autofix-max-retries`
4. `jira-autofix-researched`
5. `jira-autofix-blocked`
6. `jira-autofix-ci-failing`
7. `jira-autofix-review`
8. `jira-autofix-pending`
9. `jira-autofix`

## Rate Formula

**Success rate**: `merged / (merged + rejected + max-retries) * 100`

Researched is excluded — it is a valid outcome for spike/research tickets, not a failure.

## Attention Labels

`jira-autofix-blocked`, `jira-autofix-max-retries`

## Recent Activity Labels

`jira-autofix-merged`, `jira-autofix-rejected`, `jira-autofix-max-retries`
