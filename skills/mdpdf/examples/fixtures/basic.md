---
title: "mdpdf smoke test"
subtitle: "Portable Markdown to PDF"
author: "mdpdf"
pdf_template: "pro"
toc: true
---

# Overview

This document verifies the generic mdpdf export path.

> [!note] Portable default
> The output can be generated without a vault path or a brand profile.

## Table

| Item | Count | Cost |
| --- | ---: | ---: |
| Alpha | 2 | 120 |
| Beta | 3 | 180 |
| Total | 5 | 300 |

<!-- pdf: pagebreak -->

## Mermaid Source

This fixture intentionally avoids a Mermaid block so smoke tests can run without Node.js.
