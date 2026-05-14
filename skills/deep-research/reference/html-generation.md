# HTML Generation: McKinsey Style Report

## Design Principles

- Sharp corners (NO border-radius)
- Muted corporate colors (navy #003d5c, gray #f8f9fa)
- Ultra-compact layout
- Info-first structure
- 14px base font, compact spacing
- No decorative gradients or colors
- NO EMOJIS in final HTML

---

## Generation Steps

### Step 1: Read McKinsey Template
Load template from: `./templates/mckinsey_report_template.html`

### Step 2: Extract Key Metrics
Extract 3-4 key quantitative findings for dashboard display at top.

### Step 3: Convert MD to HTML

Use Python script:
```bash
cd ~/.claude/skills/deep-research
python scripts/md_to_html.py [markdown_report_path]
```

**Script outputs two parts:**
- **Part A ({{CONTENT}}):** All sections except Bibliography
- **Part B ({{BIBLIOGRAPHY}}):** Bibliography section only

**Script handles all conversion:**
- Headers: `##` -> `<div class="section"><h2 class="section-title">`
- Headers: `###` -> `<h3 class="subsection-title">`
- Lists: Markdown bullets -> `<ul><li>` with nesting
- Tables: Markdown tables -> `<table>` with thead/tbody
- Paragraphs: Text wrapped in `<p>` tags
- Bold/italic: `**text**` -> `<strong>`, `*text*` -> `<em>`
- Citations: [N] automatically converted to `<a>` links pointing to the source URL (opens in new tab). The script parses the bibliography to build a citation-URL map, then replaces each `[N]` with a clickable link. Citations without a matching bibliography entry remain as `<span>`.

### Step 4: Add Citation Tooltips (Optional — usually not needed since citations are already linked)

Attribution Gradients - wrap each [N] citation:
```html
<span class="citation">[N]
  <span class="citation-tooltip">
    <div class="tooltip-title">[Source Title]</div>
    <div class="tooltip-source">[Author/Publisher]</div>
    <div class="tooltip-claim">
      <div class="tooltip-claim-label">Supports Claim:</div>
      [Extract sentence with this citation]
    </div>
  </span>
</span>
```
NOTE: This step is optional for speed. Basic [N] citations are sufficient.

### Step 5: Replace Template Placeholders

| Placeholder | Content |
|-------------|---------|
| {{TITLE}} | Report title (from first ## heading) |
| {{DATE}} | Generation date (YYYY-MM-DD) |
| {{SOURCE_COUNT}} | Number of unique sources |
| {{METRICS_DASHBOARD}} | Metrics HTML from step 2 |
| {{CONTENT}} | HTML from Part A |
| {{BIBLIOGRAPHY}} | HTML from Part B |

### Step 6: Verify HTML

```bash
python scripts/verify_html.py --html [html_path] --md [md_path]
```
- Pass: Proceed to open
- Fail: Fix errors and re-run

### Step 7: Open in Browser
```bash
open [html_path]
```

### Step 8: Generate PDF (AUTOMATIC)

**IMPORTANT: Always run this step after generating the HTML report.**

Use the `html_to_pdf.py` script which auto-installs WeasyPrint if needed and injects print-optimized CSS:

```bash
cd ~/.claude/skills/deep-research
python scripts/html_to_pdf.py [html_path]
```

The script:
- Auto-installs WeasyPrint via pip if not present
- Injects print CSS (page breaks, orphan/widow control, A4 sizing, page numbers)
- Generates PDF in the same directory as the HTML (`.html` → `.pdf`)
- Auto-opens the PDF on macOS

**Custom output path:**
```bash
python scripts/html_to_pdf.py [html_path] [custom_output.pdf]
```

**If the script fails** (e.g. WeasyPrint dependency issues), fall back to:
1. Manual install: `pip install weasyprint`
2. Direct command: `weasyprint [html_path] [pdf_path]`
3. Or use the generating-pdf skill via Task tool

### WeasyPrint CSS Reference

For manual HTML optimization, see `./reference/weasyprint_guidelines.md`. Key rules:
- `page-break-inside: avoid` on tables, boxes, cards
- `page-break-after: avoid` on headings
- `orphans: 3; widows: 3` on paragraphs
- Use `display: table` not Flexbox/Grid for critical layouts
- Font sizes in pt (10pt body, 8pt citations)
