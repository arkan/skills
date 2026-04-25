---
name: amazon-shopping
version: "1.1.0"
description: Search Amazon, extract product data, and present ranked recommendations. Use when user asks to shop on Amazon, find products, compare items, or research purchases. Prioritizes review count over rating.
allowed-tools: "mcp__chrome-devtools__*"
---

# Amazon Shopping

Search Amazon and recommend products based on user preferences.

---

## MANDATORY STEP 0 - SELECT AMAZON DOMAIN

**Before anything else, determine which Amazon regional site to use.** Prices, availability, currency, and shipping all depend on the domain — searching the wrong one wastes the whole interaction.

### Detection rules (skip the question if any apply)

If the user's request **already specifies** the marketplace, use it directly without asking:
- Explicit domain mentioned: "amazon.fr", "amazon.de", "amazon.co.uk", etc.
- Country named: "Amazon France", "on the German Amazon", "UK Amazon"
- Currency hint: prices in €, £, ¥, C$, etc.
- Parameter passed by the caller (e.g. `domain=amazon.it`)

Map these to the corresponding domain from the supported list below and proceed.

### When to ask

If the request is ambiguous (e.g. "find me headphones on Amazon", "shop for a coffee maker"), use `AskUserQuestion` with this **closed list** of supported domains:

| Label | Domain |
|-------|--------|
| United States (.com) | `amazon.com` |
| France (.fr) | `amazon.fr` |
| Germany (.de) | `amazon.de` |
| United Kingdom (.co.uk) | `amazon.co.uk` |
| Italy (.it) | `amazon.it` |
| Spain (.es) | `amazon.es` |
| Canada (.ca) | `amazon.ca` |
| Japan (.co.jp) | `amazon.co.jp` |
| Australia (.com.au) | `amazon.com.au` |
| Mexico (.com.mx) | `amazon.com.mx` |
| Brazil (.com.br) | `amazon.com.br` |
| India (.in) | `amazon.in` |
| Netherlands (.nl) | `amazon.nl` |

Store the chosen domain as `<AMAZON_DOMAIN>` and use it for **all** subsequent URLs in this session (search, product pages, output links).

---

## MANDATORY STEP 1 - REQUIREMENTS GATHERING

**YOU MUST ASK CLARIFYING QUESTIONS BEFORE ANY BROWSER AUTOMATION.**

DO NOT proceed to search until you understand:
- **Budget**: Price range they're comfortable with (in the local currency of `<AMAZON_DOMAIN>`)
- **Usage**: Who/what it's for (personal, gift, professional)
- **Deal-breakers**: Features they must have or avoid

Use `AskUserQuestion` to gather this information. Only after receiving answers should you proceed to Step 2.

**Example questions for any product:**
- Budget range (under $25, $25-50, $50-100, $100+)
- Primary use case (personal, gift, professional)
- Key preferences (brand, features, quality vs value)

---

## Quick Start (After Requirements Gathered)

1. ~~**Gather requirements**: Ask about budget, usage, deal-breakers~~ → **DONE in mandatory step above**
2. **Search Amazon**: Navigate to search results and capture snapshot
3. **Extract data**: Identify products with ASINs, prices, ratings, review counts
4. **Verify**: Visit product pages to confirm accuracy
5. **Present recommendations**: Ranked by user's criteria

## Prerequisites

- Chrome DevTools MCP server connected
- Internet access to Amazon.com

## Search Workflow

### Step 1: Navigate to Amazon Search Results

Go directly to the search URL (simplest approach):

```
navigate_page type="url" url="https://www.<AMAZON_DOMAIN>/s?k=<encoded search query>"
```

**Alternative** - Interactive search (if direct URL doesn't work):
1. Navigate to `https://www.<AMAZON_DOMAIN>`
2. `take_snapshot` to find the search box UID
3. `fill` the search box with your query
4. `click` the search button or `press_key` with key="Enter"

### Step 2: Capture Results

```
take_snapshot
```

The snapshot returns the full accessibility tree with UIDs for every element. Each element includes its role, name, and URL where applicable.

### Step 3: Extract Products WITH Their ASINs

**CRITICAL: Extract product names AND their ASINs from THE SAME container element to prevent mismatches.**

In the accessibility tree, each product is typically a `listitem` containing:
- A `heading` with the product name
- A `link` with the ASIN in the URL (e.g., `/dp/B0XXXXXXXXX`)

Read the snapshot and pair each heading with the link **in the same container**. Use the UID hierarchy and indentation to identify which elements belong to the same product.

**WRONG - Causes ASIN/Product Mismatches:**
- Extracting all ASINs separately and pairing them with product names
- Amazon pages contain ASINs for ads, sponsored products, and footer links that will mix with real results

### Step 4: MANDATORY Product Page Verification

**For EVERY product before presenting it to the user, you MUST verify by visiting its actual product page.**

For each product:
1. `navigate_page` to `https://www.<AMAZON_DOMAIN>/dp/<ASIN>`
2. `take_snapshot` to read the page content
3. Verify:
   - **Title matches** the product you're recommending
   - **Price** is current from the product page (for example `Buy new: $XX.XX`, `One-time purchase: $XX.XX`, or the main price block)
   - **Rating** and **review count** are present

**MANDATORY VERIFICATION RULES:**
- If ASIN redirects to different product → DISCARD
- If page title doesn't match expected product → DISCARD
- If price cannot be found → DISCARD
- Only present VERIFIED products with a checkmark

**NEVER extract prices from search results pages** - they often don't match actual product page prices due to variants, promotions, or different sellers.

See [reference/asin-extraction.md](reference/asin-extraction.md) for detailed patterns.

## Common Issues

| Issue | Solution |
|-------|----------|
| CAPTCHA | Wait 60s, retry from `<AMAZON_DOMAIN>` |
| Rate limited | Wait 2-3 min |
| No results | Broaden search |
| Slow page load | Use `wait_for` with expected visible text, then retake `take_snapshot` |

See [reference/common-errors.md](reference/common-errors.md) for complete troubleshooting.

## Output Format

**ALL presented products MUST be verified on their actual product pages.**

```markdown
## Amazon Shortlist - [Category] (<AMAZON_DOMAIN>)

### 1. [Product] - [LOCAL_CURRENCY][PRICE] (verified)
**ASIN**: [ASIN]
**Rating**: X.X/5 (X,XXX reviews)
**<AMAZON_DOMAIN>**: https://www.<AMAZON_DOMAIN>/dp/[ASIN]
**Why this**: [Reason]
**Key specs**: [Specs]
```

**Do NOT present unverified products.** The verified marker confirms that:
1. The ASIN link goes to the actual product (not a redirect)
2. The price is current from the product page
3. The title matches what was recommended

See [reference/output-formats.md](reference/output-formats.md) for templates.

## Ranking Priority

When ratings are similar (within 0.5), prioritize review count.

Example: 4.0 with 10,000 reviews > 5.0 with 100 reviews
