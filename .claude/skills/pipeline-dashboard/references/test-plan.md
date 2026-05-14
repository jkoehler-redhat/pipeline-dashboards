# test-plan

The test-plan pipeline auto-generates test plans from Jira strategies, creates test cases, and scores them against a quality rubric. Source: `opendatahub-io/odh-test-gen` (distributed as the `test-plan` plugin via `opendatahub-io/skills-registry`). Label definitions in `skills/test-plan-create/SKILL.md` (Steps 3.6 and 4.5).

**Projects with labels today**: RHAISTRAT, RHOAIENG, RHAIRFE

## Labels (4 total)

| Label | Stage | Meaning |
|-------|-------|---------|
| `test-plan-auto-created` | Created | AI-generated test plan exists for this issue |
| `test-plan-rubric-pass` | Quality (pass) | Test plan passed quality rubric |
| `test-plan-rubric-fail` | Quality (fail) | Test plan failed quality rubric |
| `test-plan-auto-revised` | Revised | Test plan was auto-revised by the bot |

## Stage Groupings

| Group | Labels |
|-------|--------|
| Created | `test-plan-auto-created` |
| Quality Passed | `test-plan-rubric-pass` |
| Quality Failed | `test-plan-rubric-fail` |
| Auto-Revised | `test-plan-auto-revised` |

## Deduplication Priority (highest wins)

1. `test-plan-rubric-pass`
2. `test-plan-rubric-fail`
3. `test-plan-auto-revised`
4. `test-plan-auto-created`

## Rate Formula

**Quality rate**: `rubric-pass / (rubric-pass + rubric-fail) * 100`

## Attention Labels

`test-plan-rubric-fail`

## Recent Activity Labels

`test-plan-auto-created`, `test-plan-rubric-pass`, `test-plan-auto-revised`
