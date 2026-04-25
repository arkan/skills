# ASIN Extraction Reference

## What is an ASIN?

Amazon Standard Identification Number - 10 alphanumeric characters that uniquely identify products.

## URL Patterns

| Format | Example | Extraction |
|--------|---------|------------|
| `/dp/B0XXXXXXXXX` | `/dp/B08XW2X5KH/ref=...` | Extract after `/dp/` until `/` or `?` |
| `/gp/product/B0XXXXXXXXX` | `/gp/product/B08XW2X5KH` | Extract after `/product/` until `/` or `?` |
| `amzn.to/XXXXX` | Shortened redirect | Follow redirect, then extract ASIN |

## CRITICAL FAILURE MODE TO AVOID

**NEVER extract ASINs separately from product names. This WILL cause mismatches.**

**Why this fails**: Amazon pages contain ASINs for ads, "sponsored" products, footer links, and unrelated items. These get mixed with actual product results, causing wrong ASIN-to-product associations.

**Example failure**: ASIN B08PVZKVL4 (OneTouch lancets) was incorrectly paired with a TRUE METRIX glucose meter recommendation.

## Correct Extraction Method

Read the accessibility tree snapshot and pair product names with ASINs **from the same container element**.

Each product in the search results is typically a `listitem` containing:
- A `heading` element with the product name
- A `link` element with the ASIN in its URL

Use the UID hierarchy to identify which heading and link belong to the same product container. This guarantees correct pairing because the ASIN is always extracted from the link that is a child of the same listitem as the heading.

## Verification

ASIN must be:
- Exactly 10 characters
- Alphanumeric only (A-Z, 0-9)
- Present in link URLs in the snapshot
- **Extracted TOGETHER with product name** from the same container
- **Verified by navigating to the actual product page before presenting**

**ALWAYS verify before presenting**:
```
navigate_page url="https://www.amazon.com/dp/[ASIN]"
take_snapshot  # Confirm the product title matches what you're recommending
```

**NEVER fabricate ASINs**. If extraction fails, re-search or visit product page directly.
