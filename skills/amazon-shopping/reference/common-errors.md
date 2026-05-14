# Common Amazon Shopping Errors

## CRITICAL: ASIN-Product Mismatch

**Symptom**: Recommended product link goes to completely different product

**Example**: Recommending TRUE METRIX glucose meter but link goes to OneTouch lancets

**Root Cause**: Extracting ASINs separately from product names, causing mismatched pairs

**Solution**:
1. **Read the accessibility tree carefully** - pair each product heading with the link in the **same container element** using UIDs and hierarchy
2. **Verify each ASIN before presenting**:
   ```
   navigate_page url="https://www.amazon.com/dp/[ASIN]"
   take_snapshot  # Confirm title matches product being recommended
   ```
3. **If verification fails, find correct ASIN** - do NOT present mismatched data

**Prevention**: Never extract all ASINs from a page independently - this includes ASINs for ads, sponsored products, and unrelated items

## CRITICAL: Price Inaccuracy

**Symptom**: Prices shown in recommendations don't match actual product page prices

**Example**: Recommending a product at ~$20 but actual price is $35

**Root Cause**: Extracting prices from search results pages instead of actual product pages. Search results may show:
- Different prices for variants/sizes
- Outdated pricing
- Prices from third-party sellers
- Promotion prices that have expired

**Solution**:
1. **ALWAYS verify price on the actual product page**:
   ```
   navigate_page url="https://www.amazon.com/dp/[ASIN]"
   take_snapshot
   ```
2. **Look for product-page pricing text** such as `"Buy new: $XX.XX"`, `"One-time purchase: $XX.XX"`, or the main price block in the snapshot
3. **Never trust search result prices** - they're often misleading

**Prevention**: Make price verification mandatory alongside ASIN verification before presenting any recommendation

## CAPTCHA Detection

**Symptom**: Snapshot shows "enter characters" or "prove you are human"

**Solution**:
1. Wait 60 seconds
2. `navigate_page` back to `https://www.amazon.com`
3. If persistent, inform user Amazon is rate-limiting

## Rate Limiting

**Symptom**: "try again later", 403 error, or empty results

**Solution**:
1. Wait 2-3 minutes before retry
2. Avoid rapid successive searches
3. Consider rotating search terms

## No Results Found

**Symptom**: Fewer than 3 products in snapshot

**Solution**:
1. Broaden search terms (use category names)
2. Try alternative search phrasing
3. Navigate by category instead

## Slow Page Load

**Symptom**: Incomplete snapshot or missing product data

**Solution**:
1. Use `wait_for` with visible text you expect on the page, such as the search term, `"results"`, a product brand, or `"Add to Cart"`
2. Do not wait on CSS selectors or product containers; this tool only supports visible text
3. Retake `take_snapshot` after the text appears, or after a short delay if the page is still loading
