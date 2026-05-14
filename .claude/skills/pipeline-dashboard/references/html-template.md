# HTML Template

## CSS (use verbatim)

```css
* { box-sizing: border-box; }
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
.section-nav a:hover { background: #ddf4ff; }
```

## Page Layout

```html
<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Bot Pipeline Dashboard — All Pipelines</title>
<style>{CSS above}</style>
</head><body>

<h1>Bot Pipeline Dashboard</h1>
<p><strong>Generated</strong>: {YYYY-MM-DD} | <strong>Scope</strong>: All RHAI/RHOAI projects | <strong>Time range</strong>: All time</p>

<!-- Section nav: one link per pipeline -->
<div class="section-nav">
  <a href="#autofix">jira-autofix</a>
  <a href="#rfe">rfe-creator</a>
  <a href="#strat">strat-creator</a>
  <a href="#testplan">test-plan</a>
  <a href="#docpipeline">doc-pipeline</a>
  <a href="#onboarding">component-onboarding</a>
</div>

<!-- Summary cards: one card per pipeline -->
<div class="cards">
  <!-- Per pipeline: h3 name, .big hero metric, .sub hero sub-text, .sub total+projects, pills -->
</div>

<hr>

<!-- Per-pipeline sections -->
<h2 id="{anchor}">{pipeline name} Pipeline</h2>
<!-- Optional: source link for pipelines that have one -->

<h3>Pipeline Summary</h3>
<!-- Table: Metric/Count, rows from stage groupings + rate formula -->

<h3>Label Distribution</h3>
<!-- Table: Label/Count/%, one row per label, labels in <code> tags -->

<h3>By Project</h3>
<!-- Table: columns from stage groupings, one row per project -->

<h3>{Attention Title}</h3>
<!-- Count + clickable JQL link, NOT inline table -->
<!-- JQL: labels in ("label-1","label-2") AND project not in (TP) ORDER BY updated DESC -->
<!-- Link: https://redhat.atlassian.net/issues/?jql={URL_ENCODED_JQL} -->

</body></html>
```

## HTML Safety

Escape `&`, `<`, `>` in Jira summaries to prevent broken HTML.

## Link Format

All Jira links: `<a href="https://redhat.atlassian.net/browse/{KEY}" target="_blank">{KEY}</a>`
