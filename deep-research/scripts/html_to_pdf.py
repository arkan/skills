#!/usr/bin/env python3
"""
HTML to PDF converter for research reports.
Uses weasyprint CLI (brew install weasyprint) or Python API.
Injects print-optimized CSS for professional PDF output.

Usage:
    python html_to_pdf.py <html_file> [output_pdf]

If output_pdf is omitted, replaces .html with .pdf in the same directory.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PRINT_CSS = """
@page {
    size: A4;
    margin: 25mm 20mm 25mm 20mm;
    @bottom-center {
        content: counter(page);
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 9pt;
        color: #666666;
    }
}
@page :first {
    @bottom-center { content: none; }
}
body {
    font-size: 10pt;
    line-height: 1.6;
}
p {
    orphans: 3;
    widows: 3;
}
h2, h3, h4 {
    page-break-after: avoid;
}
table, .school-card, .key-insight, .executive-summary, .metric, .bib-entry, .finding-card {
    page-break-inside: avoid;
}
.metrics-dashboard {
    display: table;
    width: 100%;
    page-break-inside: avoid;
}
.metric {
    display: table-cell;
    width: 25%;
}
.header {
    page-break-after: avoid;
}
.bibliography {
    page-break-before: always;
}
a {
    text-decoration: none;
    color: #003d5c;
}
"""


def generate_pdf_cli(html_path: Path, pdf_path: Path) -> bool:
    """Generate PDF using weasyprint CLI (preferred — works with brew install)."""
    weasyprint_bin = shutil.which("weasyprint")
    if not weasyprint_bin:
        return False

    # Write print CSS to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".css", delete=False) as f:
        f.write(PRINT_CSS)
        css_path = f.name

    print(f"Generating PDF: {pdf_path}")
    try:
        result = subprocess.run(
            [weasyprint_bin, "-s", css_path, str(html_path), str(pdf_path)],
            capture_output=True,
            text=True,
        )
        Path(css_path).unlink(missing_ok=True)

        if result.returncode == 0:
            print(f"PDF generated: {pdf_path}")
            return True
        else:
            print(f"weasyprint error: {result.stderr}", file=sys.stderr)
            return False
    except Exception as e:
        Path(css_path).unlink(missing_ok=True)
        print(f"PDF generation failed: {e}", file=sys.stderr)
        return False


def generate_pdf_python(html_path: Path, pdf_path: Path) -> bool:
    """Generate PDF using weasyprint Python API (fallback)."""
    try:
        from weasyprint import CSS, HTML
    except ImportError:
        print("weasyprint not available as Python module.", file=sys.stderr)
        return False

    print(f"Generating PDF (Python API): {pdf_path}")
    try:
        html_doc = HTML(filename=str(html_path))
        print_stylesheet = CSS(string=PRINT_CSS)
        html_doc.write_pdf(str(pdf_path), stylesheets=[print_stylesheet])
        print(f"PDF generated: {pdf_path}")
        return True
    except Exception as e:
        print(f"PDF generation failed: {e}", file=sys.stderr)
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python html_to_pdf.py <html_file> [output_pdf]")
        sys.exit(1)

    html_path = Path(sys.argv[1])
    if not html_path.exists():
        print(f"Error: {html_path} not found")
        sys.exit(1)

    if len(sys.argv) >= 3:
        pdf_path = Path(sys.argv[2])
    else:
        pdf_path = html_path.with_suffix(".pdf")

    # Try CLI first (works with brew install), then Python API
    success = generate_pdf_cli(html_path, pdf_path)
    if not success:
        success = generate_pdf_python(html_path, pdf_path)

    if not success:
        print("\nWeasyPrint not found. Install with: brew install weasyprint", file=sys.stderr)
        sys.exit(1)

    # Auto-open on macOS
    if sys.platform == "darwin":
        subprocess.run(["open", str(pdf_path)])


if __name__ == "__main__":
    main()
