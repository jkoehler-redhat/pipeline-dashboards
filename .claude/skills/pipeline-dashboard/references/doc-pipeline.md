# doc-pipeline

The doc-pipeline auto-generates documentation contributions from Jira issues. It picks up RHOAIENG/RHAISTRAT issues tagged for documentation, triggers a GitLab CI pipeline that runs Claude-based doc generation, creates MRs against the OpenShift AI documentation repo, and links the results back to Jira. Source: `gitlab.com/redhat/rhel-ai/agentic-ci/doc-pipeline` (CI harness) → `tarilabs/doc-creator` (GitHub, scripts and label definitions). Label constants in `scripts/jira_ai1st_doc_start_trigger.py` (`LABEL_START`, `LABEL_INVOKED`) and `scripts/mr_ai1st_jira_contrib.py` (`JIRA_LABEL`).

**Projects with labels today**: RHOAIENG, RHAISTRAT

## Labels (3 total)

| Label | Stage | Meaning |
|-------|-------|---------|
| `ai1st-doc-start` | Queue | Issue tagged for doc generation; bot will pick up |
| `ai1st-doc-invoked` | Active | Doc pipeline triggered; label swapped from `ai1st-doc-start` |
| `ai1st-doc-contributed` | Terminal (success) | Documentation MR created and linked back to Jira |

## Stage Groupings

| Group | Labels |
|-------|--------|
| Queue | `ai1st-doc-start` |
| Invoked | `ai1st-doc-invoked` |
| Contributed | `ai1st-doc-contributed` |

## Deduplication Priority (highest wins)

1. `ai1st-doc-contributed`
2. `ai1st-doc-invoked`
3. `ai1st-doc-start`

## Attention Labels

*(none)*

## Recent Activity Labels

`ai1st-doc-contributed`
