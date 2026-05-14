#!/usr/bin/env python3
"""Collect Jira data for all 6 pipelines and generate the combined HTML dashboard."""

import json, html, os, re, base64, urllib.request, urllib.parse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

# ── Jira credentials ─────────────────────────────────────────────
email = os.environ["JIRA_EMAIL"]
token = os.environ["JIRA_TOKEN"]
auth = base64.b64encode(f"{email}:{token}".encode()).decode()
BASE = "https://redhat.atlassian.net/rest/api/3"
FIELDS = "key,summary,status,issuetype,assignee,labels,project,created,updated,priority"

def fetch_label(label):
    import time
    jql = f'labels = "{label}"'
    all_issues = []
    token_param = None
    while True:
        params = {"jql": jql, "fields": FIELDS, "maxResults": "100"}
        if token_param:
            params["nextPageToken"] = token_param
        url = f"{BASE}/search/jql?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}", "Accept": "application/json"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read())
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                else:
                    raise
        all_issues.extend(data.get("issues", []))
        if data.get("isLast", True):
            break
        token_param = data.get("nextPageToken")
        if not token_param:
            break
    return label, all_issues

def collect_pipeline(labels):
    label_counts = {}
    all_issues = {}
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(fetch_label, l): l for l in labels}
        for f in futures:
            label, issues = f.result()
            label_counts[label] = len(issues)
            for iss in issues:
                key = iss["key"]
                if key not in all_issues:
                    all_issues[key] = {
                        "key": key,
                        "project": iss["fields"]["project"]["key"],
                        "labels": list(iss["fields"].get("labels", [])),
                        "summary": iss["fields"].get("summary", ""),
                    }
                else:
                    existing = set(all_issues[key]["labels"])
                    existing.update(iss["fields"].get("labels", []))
                    all_issues[key]["labels"] = list(existing)
    return {
        "label_counts": label_counts,
        "issues": list(all_issues.values()),
        "total_unique": len(all_issues),
    }

# ── Pipeline definitions ──────────────────────────────────────────
PIPELINES = [
    {
        "id": "jira-autofix", "name": "jira-autofix", "anchor": "autofix",
        "labels": [
            "jira-autofix", "jira-autofix-pending", "jira-autofix-review",
            "jira-autofix-ci-failing", "jira-autofix-merged", "jira-autofix-rejected",
            "jira-autofix-max-retries", "jira-autofix-researched", "jira-autofix-blocked"
        ],
        "stage_groups": [
            ("Queue", ["jira-autofix"]),
            ("Active", ["jira-autofix-pending", "jira-autofix-review", "jira-autofix-ci-failing"]),
            ("Merged", ["jira-autofix-merged"]),
            ("Failed", ["jira-autofix-rejected", "jira-autofix-max-retries"]),
            ("Researched", ["jira-autofix-researched"]),
            ("Blocked", ["jira-autofix-blocked"]),
        ],
        "dedup_priority": [
            "jira-autofix-merged", "jira-autofix-rejected", "jira-autofix-max-retries",
            "jira-autofix-researched", "jira-autofix-blocked", "jira-autofix-ci-failing",
            "jira-autofix-review", "jira-autofix-pending", "jira-autofix"
        ],
        "attention_labels": ["jira-autofix-blocked", "jira-autofix-max-retries"],
        "attention_title": "Blocked &amp; Max-Retries",
    },
    {
        "id": "rfe-creator", "name": "rfe-creator", "anchor": "rfe",
        "labels": [
            "rfe-creator-auto-created", "rfe-creator-auto-revised",
            "rfe-creator-split-original", "rfe-creator-split-result",
            "rfe-creator-needs-attention", "rfe-creator-ignore",
            "rfe-creator-autofix-rubric-pass", "rfe-creator-feasibility-pass",
            "rfe-creator-feasibility-fail", "rfe-creator-feasibility-unknown"
        ],
        "stage_groups": [
            ("Created", ["rfe-creator-auto-created"]),
            ("Refined", ["rfe-creator-auto-revised"]),
            ("Split", ["rfe-creator-split-original", "rfe-creator-split-result"]),
            ("Needs Attention", ["rfe-creator-needs-attention"]),
            ("Excluded", ["rfe-creator-ignore"]),
            ("Rubric Pass", ["rfe-creator-autofix-rubric-pass"]),
            ("Feasibility", ["rfe-creator-feasibility-pass", "rfe-creator-feasibility-fail", "rfe-creator-feasibility-unknown"]),
        ],
        "dedup_priority": [
            "rfe-creator-autofix-rubric-pass", "rfe-creator-feasibility-pass",
            "rfe-creator-feasibility-fail", "rfe-creator-feasibility-unknown",
            "rfe-creator-needs-attention", "rfe-creator-ignore",
            "rfe-creator-split-result", "rfe-creator-split-original",
            "rfe-creator-auto-revised", "rfe-creator-auto-created"
        ],
        "attention_labels": ["rfe-creator-needs-attention"],
        "attention_title": "Needs Attention",
    },
    {
        "id": "strat-creator", "name": "strat-creator", "anchor": "strat",
        "labels": [
            "strat-creator-auto-created", "strat-creator-auto-refined",
            "strat-creator-rubric-pass", "strat-creator-3.5",
            "strat-creator-needs-attention", "strat-epics-created"
        ],
        "stage_groups": [
            ("Created", ["strat-creator-auto-created"]),
            ("Refined", ["strat-creator-auto-refined"]),
            ("Rubric Pass", ["strat-creator-rubric-pass"]),
            ("Release Tagged", ["strat-creator-3.5"]),
            ("Needs Attention", ["strat-creator-needs-attention"]),
            ("Epics Created", ["strat-epics-created"]),
        ],
        "dedup_priority": [
            "strat-epics-created", "strat-creator-rubric-pass",
            "strat-creator-3.5", "strat-creator-needs-attention",
            "strat-creator-auto-refined", "strat-creator-auto-created"
        ],
        "attention_labels": ["strat-creator-needs-attention"],
        "attention_title": "Needs Attention",
    },
    {
        "id": "test-plan", "name": "test-plan", "anchor": "testplan",
        "labels": [
            "test-plan-auto-created", "test-plan-rubric-pass",
            "test-plan-rubric-fail", "test-plan-auto-revised"
        ],
        "stage_groups": [
            ("Created", ["test-plan-auto-created"]),
            ("Rubric Pass", ["test-plan-rubric-pass"]),
            ("Rubric Fail", ["test-plan-rubric-fail"]),
            ("Auto-Revised", ["test-plan-auto-revised"]),
        ],
        "dedup_priority": [
            "test-plan-rubric-pass", "test-plan-rubric-fail",
            "test-plan-auto-revised", "test-plan-auto-created"
        ],
        "attention_labels": ["test-plan-rubric-fail"],
        "attention_title": "Quality Failures",
    },
    {
        "id": "doc-pipeline", "name": "doc-pipeline", "anchor": "docpipeline",
        "labels": ["ai1st-doc-start", "ai1st-doc-invoked", "ai1st-doc-contributed"],
        "stage_groups": [
            ("Queue", ["ai1st-doc-start"]),
            ("Invoked", ["ai1st-doc-invoked"]),
            ("Contributed", ["ai1st-doc-contributed"]),
        ],
        "dedup_priority": [
            "ai1st-doc-contributed", "ai1st-doc-invoked", "ai1st-doc-start"
        ],
        "attention_labels": [],
        "attention_title": "",
    },
    {
        "id": "component-onboarding", "name": "component-onboarding", "anchor": "onboarding",
        "source_url": "https://github.com/opendatahub-io/aiops-infra/tree/review/.claude/skills/create-component-onboarding-jira",
        "labels": [
            "component-onboarding", "yaml-attached", "validation-successful", "validation-failed",
            "quay-repo-created", "quay-mr-raised", "quay-mr-merged",
            "konflux-component-created", "krd-mr-raised", "krd-mr-merged",
            "okc-changes-done", "okc-pr-raised", "okc-pr-merged",
            "rkc-changes-done", "rkc-pr-raised", "rkc-pr-merged",
            "rkc-pull-changes-done", "rkc-pull-pr-raised", "rkc-pull-pr-merged",
            "operator-changes-not-needed", "odh-operator-pr-raised", "operator-pr-raised", "operator-pr-merged",
            "bundle-changes-done", "bundle-pr-raised", "bundle-pr-merged",
            "delivery-repo-exists", "delivery-repo-mr-raised", "delivery-repo-mr-merged", "delivery-repo-created",
            "product-listing-exists", "product-listing-mr-raised", "product-listing-mr-merged", "product-listing-created",
            "auto-merge-setup-done", "auto-merge-pr-raised", "auto-merge-pr-merged",
            "renovate-changes-done", "renovate-pr-raised", "renovate-pr-merged",
            "renovate-sync-triggered", "renovate-sync-done", "renovate-sync-failed",
            "tekton-pr-raised", "tekton-pr-merged", "onboarder-workflow-triggered",
            "dockerfile-labels-present", "dockerfile-labels-pr-raised",
            "onboarding-in-review", "component-onboarding-completed",
        ],
        "stage_groups": [
            ("Created", ["component-onboarding", "yaml-attached"]),
            ("Validated", ["validation-successful"]),
            ("In Progress", [
                "quay-repo-created", "quay-mr-raised", "quay-mr-merged",
                "konflux-component-created", "krd-mr-raised", "krd-mr-merged",
                "okc-changes-done", "okc-pr-raised", "okc-pr-merged",
                "rkc-changes-done", "rkc-pr-raised", "rkc-pr-merged",
                "rkc-pull-changes-done", "rkc-pull-pr-raised", "rkc-pull-pr-merged",
                "operator-changes-not-needed", "odh-operator-pr-raised", "operator-pr-raised", "operator-pr-merged",
                "bundle-changes-done", "bundle-pr-raised", "bundle-pr-merged",
                "delivery-repo-exists", "delivery-repo-mr-raised", "delivery-repo-mr-merged", "delivery-repo-created",
                "product-listing-exists", "product-listing-mr-raised", "product-listing-mr-merged", "product-listing-created",
                "auto-merge-setup-done", "auto-merge-pr-raised", "auto-merge-pr-merged",
                "renovate-changes-done", "renovate-pr-raised", "renovate-pr-merged",
                "renovate-sync-triggered", "renovate-sync-done",
                "tekton-pr-raised", "tekton-pr-merged", "onboarder-workflow-triggered",
                "dockerfile-labels-present", "dockerfile-labels-pr-raised",
            ]),
            ("In Review", ["onboarding-in-review"]),
            ("Completed", ["component-onboarding-completed"]),
            ("Failed", ["validation-failed", "renovate-sync-failed"]),
        ],
        "dedup_priority": [
            "component-onboarding-completed",
            "onboarding-in-review",
            "validation-failed", "renovate-sync-failed",
            "quay-mr-merged", "krd-mr-merged", "okc-pr-merged", "rkc-pr-merged",
            "rkc-pull-pr-merged", "operator-pr-merged", "bundle-pr-merged",
            "delivery-repo-mr-merged", "product-listing-mr-merged",
            "auto-merge-pr-merged", "renovate-pr-merged", "tekton-pr-merged",
            "renovate-sync-done",
            "quay-mr-raised", "krd-mr-raised", "okc-pr-raised", "rkc-pr-raised",
            "rkc-pull-pr-raised", "operator-pr-raised", "bundle-pr-raised",
            "delivery-repo-mr-raised", "product-listing-mr-raised",
            "auto-merge-pr-raised", "renovate-pr-raised",
            "tekton-pr-raised", "dockerfile-labels-pr-raised",
            "renovate-sync-triggered", "onboarder-workflow-triggered",
            "quay-repo-created", "konflux-component-created",
            "okc-changes-done", "rkc-changes-done", "rkc-pull-changes-done",
            "operator-changes-not-needed", "odh-operator-pr-raised",
            "bundle-changes-done", "delivery-repo-exists", "delivery-repo-created",
            "product-listing-exists", "product-listing-created",
            "auto-merge-setup-done", "renovate-changes-done",
            "dockerfile-labels-present",
            "validation-successful",
            "yaml-attached",
            "component-onboarding",
        ],
        "attention_labels": ["validation-failed", "renovate-sync-failed"],
        "attention_title": "Validation &amp; Sync Failures",
    },
]

# ── Collect all pipeline data ─────────────────────────────────────
all_labels = set()
for p in PIPELINES:
    all_labels.update(p["labels"])

print(f"Collecting {len(all_labels)} unique labels across {len(PIPELINES)} pipelines...")

label_counts = {}
all_issues = {}

with ThreadPoolExecutor(max_workers=8) as pool:
    futures = {pool.submit(fetch_label, l): l for l in all_labels}
    done = 0
    for f in futures:
        label, issues = f.result()
        label_counts[label] = len(issues)
        done += 1
        if done % 10 == 0:
            print(f"  {done}/{len(all_labels)} labels queried...")
        for iss in issues:
            key = iss["key"]
            if key not in all_issues:
                all_issues[key] = {
                    "key": key,
                    "project": iss["fields"]["project"]["key"],
                    "labels": list(iss["fields"].get("labels", [])),
                    "summary": iss["fields"].get("summary", ""),
                }
            else:
                existing = set(all_issues[key]["labels"])
                existing.update(iss["fields"].get("labels", []))
                all_issues[key]["labels"] = list(existing)

print(f"  {len(all_labels)}/{len(all_labels)} labels queried")
print(f"Total unique issues across all pipelines: {len(all_issues)}")

# ── Deduplicate per pipeline ──────────────────────────────────────
def deduplicate(issues, dedup_priority, stage_groups, pipeline_labels):
    label_to_stage = {}
    for stage_name, stage_labels in stage_groups:
        for lbl in stage_labels:
            label_to_stage[lbl] = stage_name

    stage_counts = defaultdict(int)
    project_stages = defaultdict(lambda: defaultdict(int))
    classified = 0

    for issue in issues:
        issue_labels = set(issue.get("labels", []))
        pipeline_issue_labels = issue_labels & set(pipeline_labels)
        if not pipeline_issue_labels:
            continue
        project = issue.get("project", "")
        assigned_stage = None
        for priority_label in dedup_priority:
            if priority_label in pipeline_issue_labels:
                assigned_stage = label_to_stage.get(priority_label)
                break
        if assigned_stage:
            stage_counts[assigned_stage] += 1
            if project and project != "TP":
                project_stages[project][assigned_stage] += 1
            classified += 1

    return dict(stage_counts), dict(project_stages), classified

issues_list = list(all_issues.values())
results = {}
for pdef in PIPELINES:
    plc = {l: label_counts.get(l, 0) for l in pdef["labels"]}
    sc, ps, classified = deduplicate(
        issues_list, pdef["dedup_priority"], pdef["stage_groups"], pdef["labels"]
    )
    results[pdef["id"]] = {
        "label_counts": plc,
        "stage_counts": sc,
        "project_stages": ps,
        "total_unique": classified,
    }

# ── HTML generation ───────────────────────────────────────────────
CSS = """* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 20px; color: #24292f; line-height: 1.5; background: #fff; }
h1 { border-bottom: 2px solid #d0d7de; padding-bottom: 8px; }
h2 { border-bottom: 1px solid #d0d7de; padding-bottom: 6px; margin-top: 40px; color: #1a1a2e; }
h3 { margin-top: 24px; color: #333; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
td, th { border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; font-size: 0.92em; }
th { background: #f0f3f6; font-weight: 600; }
tr:nth-child(even) td { background: #f6f8fa; }
code { background: #f6f8fa; padding: 2px 6px; border-radius: 4px; font-size: 0.88em; }
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: none; border-top: 1px solid #d0d7de; margin: 32px 0; }
em { color: #656d76; font-size: 0.9em; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin: 20px 0; }
.card { border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; background: #f6f8fa; }
.card h3 { margin: 0 0 8px 0; font-size: 1.05em; border: none; padding: 0; }
.card .big { font-size: 2em; font-weight: 700; color: #0969da; }
.card .sub { font-size: 0.85em; color: #656d76; }
.pill { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: 600; margin: 2px 2px; }
.pill-green { background: #dafbe1; color: #116329; }
.pill-red { background: #ffebe9; color: #82071e; }
.pill-yellow { background: #fff8c5; color: #6a5300; }
.pill-blue { background: #ddf4ff; color: #0550ae; }
.section-nav { display: flex; gap: 12px; margin: 16px 0; flex-wrap: wrap; }
.section-nav a { padding: 6px 14px; background: #f0f3f6; border-radius: 6px; font-weight: 500; font-size: 0.9em; }
.section-nav a:hover { background: #ddf4ff; }"""

def esc(s):
    return html.escape(str(s)) if s else ""

def jql_link(jql):
    return f"https://redhat.atlassian.net/issues/?jql={urllib.parse.quote(jql)}"

def build_card(pdef, r):
    sc = r["stage_counts"]
    total = r["total_unique"]
    nprojects = len(r["project_stages"])
    pid = pdef["id"]

    if pid == "jira-autofix":
        merged = sc.get("Merged", 0)
        failed = sc.get("Failed", 0)
        rate = round(merged / (merged + failed) * 100, 1) if (merged + failed) > 0 else 0
        hero, sub1 = str(merged), f"PRs merged &middot; {rate}% success rate"
        pills = (f'<span class="pill pill-green">merged {merged}</span>'
                 f'<span class="pill pill-red">failed {failed}</span>'
                 f'<span class="pill pill-yellow">blocked {sc.get("Blocked", 0)}</span>')
    elif pid == "rfe-creator":
        rp, cr = sc.get("Rubric Pass", 0), sc.get("Created", 0)
        hero, sub1 = str(rp), f"rubric pass &middot; {cr} auto-created"
        pills = (f'<span class="pill pill-green">rubric pass {rp}</span>'
                 f'<span class="pill pill-blue">created {cr}</span>'
                 f'<span class="pill pill-yellow">attention {sc.get("Needs Attention", 0)}</span>')
    elif pid == "strat-creator":
        rp, cr = sc.get("Rubric Pass", 0), sc.get("Created", 0)
        hero, sub1 = str(rp), f"rubric pass &middot; {cr} auto-created"
        pills = (f'<span class="pill pill-green">rubric pass {rp}</span>'
                 f'<span class="pill pill-blue">created {cr}</span>'
                 f'<span class="pill pill-yellow">attention {sc.get("Needs Attention", 0)}</span>')
    elif pid == "test-plan":
        rp, cr = sc.get("Rubric Pass", 0), sc.get("Created", 0)
        rf = sc.get("Rubric Fail", 0)
        hero, sub1 = str(rp), f"rubric pass &middot; {cr} auto-created"
        pills = (f'<span class="pill pill-green">rubric pass {rp}</span>'
                 f'<span class="pill pill-red">rubric fail {rf}</span>'
                 f'<span class="pill pill-blue">auto-revised {sc.get("Auto-Revised", 0)}</span>')
    elif pid == "doc-pipeline":
        contrib = sc.get("Contributed", 0)
        invoked = sc.get("Invoked", 0)
        hero, sub1 = str(contrib), f"docs contributed &middot; {invoked} invoked"
        pills = (f'<span class="pill pill-green">contributed {contrib}</span>'
                 f'<span class="pill pill-blue">invoked {invoked}</span>'
                 f'<span class="pill pill-yellow">queued {sc.get("Queue", 0)}</span>')
    elif pid == "component-onboarding":
        completed = sc.get("Completed", 0)
        review = sc.get("In Review", 0)
        failed = sc.get("Failed", 0)
        hero, sub1 = str(completed), f"completed &middot; {review} in review"
        pills = (f'<span class="pill pill-green">completed {completed}</span>'
                 f'<span class="pill pill-blue">in review {review}</span>'
                 f'<span class="pill pill-red">failed {failed}</span>')
    else:
        hero, sub1, pills = str(total), "", ""

    return f"""<div class="card">
<h3>{esc(pdef["name"])}</h3>
<div class="big">{hero}</div>
<div class="sub">{sub1}</div>
<div class="sub">{total} total issues &middot; {nprojects} projects</div>
<div style="margin-top:8px">{pills}</div>
</div>"""

def build_section(pdef, r):
    sc = r["stage_counts"]
    lc = r["label_counts"]
    ps = r["project_stages"]
    total = r["total_unique"]
    pid = pdef["id"]
    stage_groups = pdef["stage_groups"]
    group_names = [g[0] for g in stage_groups]

    lines = [f'<h2 id="{pdef["anchor"]}">{esc(pdef["name"])} Pipeline</h2>']

    source_url = pdef.get("source_url")
    if source_url:
        lines.append(f'<p><em>Source: <a href="{esc(source_url)}" target="_blank">{esc(source_url)}</a></em></p>')

    # Pipeline Summary
    lines.append('<h3>Pipeline Summary</h3>')
    lines.append('<table><tr><th>Metric</th><th>Count</th></tr>')
    lines.append(f'<tr><td>Total issues</td><td>{total}</td></tr>')
    for gn in group_names:
        lines.append(f'<tr><td>{esc(gn)}</td><td>{sc.get(gn, 0)}</td></tr>')
    if pid == "jira-autofix":
        m, f_ = sc.get("Merged", 0), sc.get("Failed", 0)
        rate = round(m / (m + f_) * 100, 1) if (m + f_) > 0 else 0
        lines.append(f'<tr><td><strong>Success rate</strong></td><td><strong>{rate}%</strong></td></tr>')
    elif pid == "test-plan":
        rp, rf = sc.get("Rubric Pass", 0), sc.get("Rubric Fail", 0)
        rate = round(rp / (rp + rf) * 100, 1) if (rp + rf) > 0 else 0
        lines.append(f'<tr><td><strong>Quality rate</strong></td><td><strong>{rate}%</strong></td></tr>')
    elif pid == "component-onboarding":
        comp = sc.get("Completed", 0)
        rate = round(comp / total * 100, 1) if total > 0 else 0
        lines.append(f'<tr><td><strong>Completion rate</strong></td><td><strong>{rate}%</strong></td></tr>')
    lines.append('</table>')

    # Label Distribution
    lines.append('<h3>Label Distribution</h3>')
    lines.append('<table><tr><th>Label</th><th>Count</th><th>% of Total</th></tr>')
    label_sum = sum(lc.get(l, 0) for l in pdef["labels"])
    for label in pdef["labels"]:
        cnt = lc.get(label, 0)
        pct = round(cnt / label_sum * 100, 1) if label_sum > 0 else 0
        lines.append(f'<tr><td><code>{esc(label)}</code></td><td>{cnt}</td><td>{pct}%</td></tr>')
    lines.append('</table>')
    lines.append('<p><em>Note: Issues may carry multiple labels; label counts may sum to more than total issues.</em></p>')

    # By Project
    lines.append('<h3>By Project</h3>')
    hdr = '<tr><th>Project</th>' + ''.join(f'<th>{esc(g)}</th>' for g in group_names) + '<th>Total</th></tr>'
    lines.append(f'<table>{hdr}')
    sorted_projects = sorted(ps.keys())
    totals_row = defaultdict(int)
    grand = 0
    for proj in sorted_projects:
        stages = ps[proj]
        rt = sum(stages.get(g, 0) for g in group_names)
        grand += rt
        cells = ''.join(f'<td>{stages.get(g, 0)}</td>' for g in group_names)
        lines.append(f'<tr><td>{esc(proj)}</td>{cells}<td>{rt}</td></tr>')
        for g in group_names:
            totals_row[g] += stages.get(g, 0)
    tcells = ''.join(f'<td><strong>{totals_row[g]}</strong></td>' for g in group_names)
    lines.append(f'<tr><td><strong>Total</strong></td>{tcells}<td><strong>{grand}</strong></td></tr>')
    lines.append('</table>')

    # Attention Items
    att = pdef["attention_labels"]
    if att:
        att_count = sum(lc.get(l, 0) for l in att)
        att_str = ", ".join(f'"{l}"' for l in att)
        jql = f'labels in ({att_str}) AND project not in (TP) ORDER BY updated DESC'
        link = jql_link(jql)
        lines.append(f'<h3>{pdef["attention_title"]}</h3>')
        lines.append(f'<p><a href="{esc(link)}" target="_blank">{att_count} issue{"s" if att_count != 1 else ""} requiring attention</a></p>')

    return '\n'.join(lines)

# ── Assemble page ─────────────────────────────────────────────────
parts = [f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Bot Pipeline Dashboard — All Pipelines</title>
<style>{CSS}</style>
</head><body>

<h1>Bot Pipeline Dashboard</h1>
<p><strong>Generated</strong>: {today} | <strong>Scope</strong>: All RHAI/RHOAI projects | <strong>Time range</strong>: All time</p>

<div class="section-nav">"""]

for p in PIPELINES:
    parts.append(f'<a href="#{p["anchor"]}">{p["name"]}</a>')

parts.append('</div>\n<div class="cards">')

for p in PIPELINES:
    parts.append(build_card(p, results[p["id"]]))

parts.append('</div>\n<hr>')

for p in PIPELINES:
    parts.append(build_section(p, results[p["id"]]))

parts.append('\n</body></html>')

html_out = '\n'.join(parts)

with open("/tmp/pipeline-dashboards/index.html", "w") as f:
    f.write(html_out)
with open(f"/Users/jaykoehler/aicp-status/docs/pipelines/{today}_all_pipelines.html", "w") as f:
    f.write(html_out)

print(f"\nDashboard written ({len(html_out)} bytes)")
print(f"  /tmp/pipeline-dashboards/index.html")
print(f"  docs/pipelines/{today}_all_pipelines.html")
print()
for p in PIPELINES:
    r = results[p["id"]]
    print(f'{p["name"]}: {r["total_unique"]} issues, {len(r["project_stages"])} projects')
    for g, _ in p["stage_groups"]:
        if r["stage_counts"].get(g, 0) > 0:
            print(f'  {g}: {r["stage_counts"][g]}')
