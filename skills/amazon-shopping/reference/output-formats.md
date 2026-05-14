# Amazon Shopping Output Formats

## Standard Recommendation Format

```markdown
## Amazon Shortlist - [Product Category]

### 1. [Product Name] - $XX.XX
**Rating**: X.X/5 (X,XXX reviews)
**Amazon**: https://www.amazon.com/dp/[ASIN]

**Why this**: [How it matches user criteria]

**Key specs**: [2-3 most relevant specs]

**Considerations**: [Trade-offs or warnings]

---

### 2. [Product Name] - $XX.XX
**Rating**: X.X/5 (X,XXX reviews)
**Amazon**: https://www.amazon.com/dp/[ASIN]
...
```

## Summary Table Format

```markdown
| Component | Product | Price | Rating | ASIN |
|-----------|---------|-------|--------|------|
| Item 1 | Product Name | $XX.XX | X.X/5 | B0XXXXX |
| Item 2 | Product Name | $XX.XX | X.X/5 | B0XXXXX |
```

## Usage Notes

- Always use clean URL format: `https://www.amazon.com/dp/[ASIN]`
- Extract ASIN from actual `/url:` lines in snapshot
- Verify ASIN is exactly 10 alphanumeric characters
- Make links prominent and easy to copy
