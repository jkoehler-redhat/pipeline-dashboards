---
name: pipeline-dashboard
description: Generate and publish a combined HTML dashboard for all bot pipelines (jira-autofix, rfe-creator, strat-creator, test-plan, doc-pipeline, component-onboarding) to the GitHub Pages site. Use this skill whenever the user wants to update the dashboard, refresh the GitHub Pages site, publish pipeline status, generate the HTML report, or asks about the pipeline website, even if they don't explicitly say 'dashboard'.
---

# Pipeline Dashboard Skill

Generate a self-contained HTML page covering all bot pipelines, collect live data from Jira, and push `index.html` to `jkoehler-redhat/pipeline-dashboards` for GitHub Pages hosting.

## When to Use

- User asks to "update the dashboard", "refresh the pipeline page", "publish pipeline status"
- User invokes `/pipeline-dashboard`
- Periodic refresh to keep the GitHub Pages site current

## Interactive Prompt

```
Question: "Generate and push the combined pipeline dashboard?"
Options:
  1. Yes, generate and push [default]
  2. Generate locally only (don't push)
```

No pipeline selection — always all pipelines. No time range — always all time.

---

## Pipeline Registry

Read `${CLAUDE_SKILL_DIR}/references/pipeline-registry.md` for the full registry table including hero metrics, card pills, attention labels, and source links for each pipeline.

Six pipelines: jira-autofix, rfe-creator, strat-creator, test-plan, doc-pipeline, component-onboarding.

---

## Pipeline Definitions

Each pipeline's labels, stage groupings, deduplication priority, rate formulas, and attention labels are in `${CLAUDE_SKILL_DIR}/references/`:

| Pipeline | Reference | Labels |
|----------|-----------|--------|
| jira-autofix | `${CLAUDE_SKILL_DIR}/references/jira-autofix.md` | 9 |
| rfe-creator | `${CLAUDE_SKILL_DIR}/references/rfe-creator.md` | 10 |
| strat-creator | `${CLAUDE_SKILL_DIR}/references/strat-creator.md` | 6 |
| test-plan | `${CLAUDE_SKILL_DIR}/references/test-plan.md` | 4 |
| doc-pipeline | `${CLAUDE_SKILL_DIR}/references/doc-pipeline.md` | 3 |
| component-onboarding | `${CLAUDE_SKILL_DIR}/references/component-onboarding.md` | 50 |

---

## Dynamic Label Discovery

Read `${CLAUDE_SKILL_DIR}/references/discovery-sources.md` for source repos, discovery steps, and extraction instructions. Run discovery before querying Jira to pick up new labels added upstream.

If discovery fails, fall back to the static label lists in the pipeline reference files above.

---

## Data Collection

### Authentication

```bash
source /tmp/ai-first-status/.env
# Provides: JIRA_EMAIL, JIRA_TOKEN
```

### Query Approach

Use Jira REST API v3 via curl or Python. **Do NOT use MCP tools** — the REST API supports 100 results per page and is faster for bulk label queries.

A ready-to-run script is available at `${CLAUDE_SKILL_DIR}/scripts/collect_and_generate.py`. It queries all labels in parallel, deduplicates, and generates the HTML. Run it with `JIRA_EMAIL` and `JIRA_TOKEN` environment variables set.

If running manually instead of the script:
1. **Discover labels** — Run dynamic label discovery (see references)
2. **Query all labels** for all pipelines in parallel
3. **Deduplicate** each pipeline using the priority ordering from the pipeline reference files
4. **Build per-project breakdowns** for each pipeline
5. **Collect attention items** — count + JQL link for each pipeline's attention labels
6. **Calculate hero metrics** per the Pipeline Registry table

### Pagination

The v3 API uses cursor-based pagination (`nextPageToken` / `isLast`), not `startAt`. If any query returns 100 results, paginate until `isLast: true`.

---

## HTML Output

Read `${CLAUDE_SKILL_DIR}/references/html-template.md` for the CSS and page layout template.

The HTML must be self-contained — no external stylesheets or JavaScript. Attention items render as a count + clickable JQL link to Jira, not an inline table.

---

## Publishing

### Step 1: Clone or Update Repo

```bash
if [ -d /tmp/pipeline-dashboards ]; then
  cd /tmp/pipeline-dashboards && git pull origin main
else
  gh repo clone jkoehler-redhat/pipeline-dashboards /tmp/pipeline-dashboards
fi
```

### Step 2: Write HTML

Write the generated HTML to `/tmp/pipeline-dashboards/index.html`.

### Step 3: Commit and Push

```bash
cd /tmp/pipeline-dashboards
git add index.html
git commit -m "Update dashboard {YYYY-MM-DD}"
git push origin main
```

Skip if the user chose "Generate locally only".

### Step 4: Confirm

Report the live URL: `https://jkoehler-redhat.github.io/pipeline-dashboards/`

---

## Quality Checks

- [ ] All six pipelines present in the output
- [ ] Summary card hero metrics match corresponding pipeline summary tables
- [ ] By-project totals match pipeline summary totals for each pipeline
- [ ] All Jira links use `https://redhat.atlassian.net/browse/{KEY}` format with `target="_blank"`
- [ ] HTML is self-contained — no external stylesheet or JS references
- [ ] Special characters in summaries are HTML-escaped
- [ ] Git push succeeded (or skipped per user request)
- [ ] Attention items show count + clickable JQL link (not inline table)
- [ ] Section nav links match pipeline anchor IDs

---

## Adding a New Pipeline

1. **Register labels** — Create `${CLAUDE_SKILL_DIR}/references/{pipeline}.md` with labels, stages, dedup priority
2. **Add to registry** — Add a row to `${CLAUDE_SKILL_DIR}/references/pipeline-registry.md` (hero metric, pills, attention labels, anchor)
3. **Add discovery** — Add a row to `${CLAUDE_SKILL_DIR}/references/discovery-sources.md` (source repo, files to read)
4. **Update script** — Add the pipeline definition to `${CLAUDE_SKILL_DIR}/scripts/collect_and_generate.py`
5. **Update nav** — The section nav and card grid auto-scale

---

## Troubleshooting

### Jira auth fails
Verify `/tmp/ai-first-status/.env` exists. Test: `source /tmp/ai-first-status/.env && curl -s -u "$JIRA_EMAIL:$JIRA_TOKEN" "https://redhat.atlassian.net/rest/api/3/myself"`

### Git push fails
Check: `gh auth status` and `gh repo view jkoehler-redhat/pipeline-dashboards`

### Jira returns total: -1
Do not rely on the `total` field. Count returned issues and paginate if results hit 100.
