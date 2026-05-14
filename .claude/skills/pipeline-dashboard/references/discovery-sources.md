# Dynamic Label Discovery

Before querying Jira, discover the current label sets from the pipeline source repos. This ensures new labels added upstream are automatically picked up.

## Source Repos

| Pipeline | Discovery Source | What to Read |
|----------|----------------|--------------|
| rfe-creator | `opendatahub-io/skills-registry` → `jwforres/rfe-creator` | `registry.yaml` gives the source repo; then read `scripts/submit.py` for `FEASIBILITY_LABELS` and `.claude/skills/rfe.submit/SKILL.md` for the full labeling scheme table |
| jira-autofix | `opendatahub-io/autofix-skills` | Read `AGENTS.md` for verdict-to-label overview; read skill `SKILL.md` files for verdict values; the outer-layer label mapping is in `verdict.py` in `jira-autofix` / `ai-agentic-lib` on GitLab |
| strat-creator | `opendatahub-io/skills-registry` → `jwforres/rfe-creator` | strat-creator skills are packaged inside the rfe-creator plugin; check for `strat-creator-*` label definitions |
| test-plan | `opendatahub-io/odh-test-gen` | Read `skills/test-plan-create/SKILL.md` for label definitions (Steps 3.6 and 4.5); look for any labels matching `test-plan-*` |
| doc-pipeline | `gitlab.com/redhat/rhel-ai/agentic-ci/doc-pipeline` → `tarilabs/doc-creator` | Read `scripts/jira_ai1st_doc_start_trigger.py` for `LABEL_START`/`LABEL_INVOKED` and `scripts/mr_ai1st_jira_contrib.py` for `JIRA_LABEL`; look for any labels matching `ai1st-doc-*` |
| component-onboarding | `opendatahub-io/aiops-infra` (branch: `review`) | Read `.claude/skills/common/scripts/sync_state_from_jira.py` for `LABEL_MAP` (authoritative mapping of all 50 labels); check all skill dirs for `--add-label` calls |

## Discovery Steps

```bash
# 1. Fetch the skills registry
curl -sL "https://raw.githubusercontent.com/opendatahub-io/skills-registry/main/registry.yaml" \
  -o /tmp/skills-registry.yaml

# 2. rfe-creator labels
curl -sL "https://raw.githubusercontent.com/jwforres/rfe-creator/main/scripts/submit.py" \
  -o /tmp/rfe-submit.py
curl -sL "https://raw.githubusercontent.com/jwforres/rfe-creator/main/.claude/skills/rfe.submit/SKILL.md" \
  -o /tmp/rfe-submit-skill.md

# 3. autofix-skills metadata
curl -sL "https://raw.githubusercontent.com/opendatahub-io/autofix-skills/main/AGENTS.md" \
  -o /tmp/autofix-agents.md

# 4. test-plan labels
curl -sL "https://raw.githubusercontent.com/opendatahub-io/odh-test-gen/main/skills/test-plan-create/SKILL.md" \
  -o /tmp/test-plan-create-skill.md

# 5. doc-pipeline labels
curl -sL "https://raw.githubusercontent.com/tarilabs/doc-creator/main/scripts/jira_ai1st_doc_start_trigger.py" \
  -o /tmp/doc-trigger.py
curl -sL "https://raw.githubusercontent.com/tarilabs/doc-creator/main/scripts/mr_ai1st_jira_contrib.py" \
  -o /tmp/doc-contrib.py

# 6. component-onboarding labels
curl -sL "https://raw.githubusercontent.com/opendatahub-io/aiops-infra/review/.claude/skills/common/scripts/sync_state_from_jira.py" \
  -o /tmp/onboarding-sync-state.py
curl -sL "https://raw.githubusercontent.com/opendatahub-io/aiops-infra/review/.claude/skills/create-component-onboarding-jira/SKILL.md" \
  -o /tmp/onboarding-create-skill.md
```

## What to Extract

- **rfe-creator**: Parse the "Labeling Scheme" table from `rfe.submit/SKILL.md` and `FEASIBILITY_LABELS` dict from `submit.py`. Look for any labels matching `rfe-creator-*`.
- **strat-creator**: Search the rfe-creator repo for labels matching `strat-creator-*` or `strat-epics-*`.
- **jira-autofix**: Parse verdict values from the autofix-skills `SKILL.md` files. Cross-reference with the known label mapping.
- **test-plan**: Parse the label stamping steps from `test-plan-create/SKILL.md`. Look for any labels matching `test-plan-*`.
- **doc-pipeline**: Parse `LABEL_START` and `LABEL_INVOKED` constants from `jira_ai1st_doc_start_trigger.py` and `JIRA_LABEL` from `mr_ai1st_jira_contrib.py`. Look for any labels matching `ai1st-doc-*`.
- **component-onboarding**: Parse `LABEL_MAP` dict from `sync_state_from_jira.py`. Also check each skill's `SKILL.md` for `--add-label` calls. 50 labels across 16 lifecycle phases.

## Merge with Defaults

Compare discovered labels against the fallback defaults in `pipeline-tracker/references/{pipeline}.md`. If new labels are found:
1. Add them to the query list
2. Note them in the dashboard output as "New labels detected"
3. Log a suggestion to update the reference files

If discovery fails (network error, repo moved), fall back to the static label lists in the reference files and continue with a warning.
