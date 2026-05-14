# component-onboarding

The component-onboarding pipeline automates Konflux CI/build onboarding for ODH and RHOAI components. It tracks an issue through 16 lifecycle phases: ticket creation, YAML validation, Quay repo setup, Konflux release data, ODH/RHOAI Konflux Central PRs, operator integration, bundle integration, delivery repo, product listing, auto-merge setup, Renovate enablement, Tekton onboarder workflow, Dockerfile labels, and final review/completion. Source: `opendatahub-io/aiops-infra` (branch: `review`), skill at `.claude/skills/create-component-onboarding-jira`. The authoritative label-to-step mapping is in `.claude/skills/common/scripts/sync_state_from_jira.py` (`LABEL_MAP` dict).

**Projects with labels today**: RHOAIENG, RHODS, MTV

## Labels (50 total)

| Label | Stage | Meaning |
|-------|-------|---------|
| `component-onboarding` | Created | Onboarding ticket created |
| `yaml-attached` | Created | `component_onboarding_details.yaml` attached to ticket |
| `validation-successful` | Validated | YAML passed schema + Dockerfile validation |
| `validation-failed` | Failed | Validation failed (schema, branch, or Dockerfile digests) |
| `quay-repo-created` | In Progress | Quay repo already exists (fast-path) |
| `quay-mr-raised` | In Progress | GitLab MR raised to create Quay repo |
| `quay-mr-merged` | In Progress | Quay repo MR merged |
| `konflux-component-created` | In Progress | Konflux Component already exists on cluster (fast-path) |
| `krd-mr-raised` | In Progress | GitLab MR raised for Konflux release data |
| `krd-mr-merged` | In Progress | Konflux release data MR merged |
| `okc-changes-done` | In Progress | ODH Konflux Central PipelineRuns already exist (fast-path) |
| `okc-pr-raised` | In Progress | GitHub PR raised for ODH Konflux Central |
| `okc-pr-merged` | In Progress | ODH Konflux Central PR merged |
| `rkc-changes-done` | In Progress | RHOAI Konflux Central push PipelineRun exists (fast-path) |
| `rkc-pr-raised` | In Progress | GitHub PR raised for RHOAI Konflux Central push pipeline |
| `rkc-pr-merged` | In Progress | RHOAI Konflux Central push PR merged |
| `rkc-pull-changes-done` | In Progress | RHOAI pull PipelineRun exists (fast-path) |
| `rkc-pull-pr-raised` | In Progress | GitHub PR raised for RHOAI pull pipeline |
| `rkc-pull-pr-merged` | In Progress | RHOAI pull pipeline PR merged |
| `operator-changes-not-needed` | In Progress | Component is not an operator (no integration needed) |
| `odh-operator-pr-raised` | In Progress | Component already in ODH operator manifests (fast-path) |
| `operator-pr-raised` | In Progress | GitHub PR raised for operator integration |
| `operator-pr-merged` | In Progress | Operator integration PR merged |
| `bundle-changes-done` | In Progress | Bundle patch entries already exist (fast-path) |
| `bundle-pr-raised` | In Progress | GitHub PR raised for bundle integration |
| `bundle-pr-merged` | In Progress | Bundle PR merged |
| `delivery-repo-exists` | In Progress | Delivery repo entry already exists (fast-path) |
| `delivery-repo-mr-raised` | In Progress | GitLab MR raised for delivery repo |
| `delivery-repo-mr-merged` | In Progress | Delivery repo MR merged |
| `delivery-repo-created` | In Progress | Delivery repo created (alias for done) |
| `product-listing-exists` | In Progress | Product listing already exists (fast-path) |
| `product-listing-mr-raised` | In Progress | GitLab MR raised for product listing |
| `product-listing-mr-merged` | In Progress | Product listing MR merged |
| `product-listing-created` | In Progress | Product listing created (alias for done) |
| `auto-merge-setup-done` | In Progress | Auto-merge config already exists (fast-path) |
| `auto-merge-pr-raised` | In Progress | GitHub PR raised for auto-merge setup |
| `auto-merge-pr-merged` | In Progress | Auto-merge PR merged |
| `renovate-changes-done` | In Progress | Renovate entry already exists (fast-path) |
| `renovate-pr-raised` | In Progress | GitHub PR raised for Renovate enablement |
| `renovate-pr-merged` | In Progress | Renovate PR merged |
| `renovate-sync-triggered` | In Progress | Renovate config sync workflow dispatched |
| `renovate-sync-done` | In Progress | Renovate sync completed successfully |
| `renovate-sync-failed` | Failed | Renovate sync workflow failed |
| `tekton-pr-raised` | In Progress | Tekton PR raised by onboarder workflow |
| `tekton-pr-merged` | In Progress | Tekton PR merged |
| `onboarder-workflow-triggered` | In Progress | ODH Konflux onboarder workflow triggered |
| `dockerfile-labels-present` | In Progress | All RHOAI OCI labels already present (fast-path) |
| `dockerfile-labels-pr-raised` | In Progress | GitHub PR raised for Dockerfile labels |
| `onboarding-in-review` | In Review | All PRs/MRs raised, pending merge review |
| `component-onboarding-completed` | Completed | All onboarding steps done, ticket resolved |

## Stage Groupings

| Group | Labels |
|-------|--------|
| Created | `component-onboarding`, `yaml-attached` |
| Validated | `validation-successful` |
| In Progress | All `*-raised`, `*-merged`, `*-done`, `*-exists`, `*-created`, `*-triggered`, `*-not-needed`, `*-present`, `renovate-sync-done` labels |
| In Review | `onboarding-in-review` |
| Completed | `component-onboarding-completed` |
| Failed | `validation-failed`, `renovate-sync-failed` |

## Deduplication Priority (highest wins)

1. `component-onboarding-completed`
2. `onboarding-in-review`
3. `validation-failed`, `renovate-sync-failed`
4. All `*-merged` labels (quay, krd, okc, rkc, rkc-pull, operator, bundle, delivery-repo, product-listing, auto-merge, renovate, tekton)
5. `renovate-sync-done`
6. All `*-raised` labels
7. `renovate-sync-triggered`, `onboarder-workflow-triggered`
8. All fast-path labels (`*-created`, `*-exists`, `*-done`, `*-not-needed`, `*-present`)
9. `validation-successful`
10. `yaml-attached`
11. `component-onboarding`

## Rate Formula

**Completion rate**: `completed / total * 100`

## Attention Labels

`validation-failed`, `renovate-sync-failed`

## Recent Activity Labels

`component-onboarding-completed`
