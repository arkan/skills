---
name: exa
description: >
  Search the web, extract content from URLs, and get AI-powered answers using the Exa API via curl.
  Use this skill whenever you need real-time web information: researching a topic, finding documentation,
  looking up people or companies, reading news, fetching page content, or answering questions with citations.
  Also use when the user says /exa, "search the web", "look this up", "find articles about",
  "what's the latest on", or any query that requires up-to-date web knowledge beyond your training data.
---

# Exa Web Search Skill

Search the web, extract page content, and get cited answers — all via `curl` against the Exa API.

## Authentication

The API key is read from the environment variable `EXA_API_KEY`. Every curl call uses:
```
-H "x-api-key: $EXA_API_KEY"
```

If `EXA_API_KEY` is not set, stop and tell the user to set it:
```bash
export EXA_API_KEY="their-key-here"
```

## How to Use This Skill

When you need web information, pick the right endpoint and search type for the task, build the curl command, execute it, then parse and present the results clearly to the user. Always attribute sources with URLs.

## Endpoints

### 1. `/search` — Find and optionally retrieve content

The primary endpoint. Finds relevant pages and optionally returns their content.

```bash
curl -s -X POST 'https://api.exa.ai/search' \
  -H "x-api-key: $EXA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "your search query here",
  "type": "auto",
  "num_results": 5,
  "contents": {
    "highlights": { "max_characters": 4000 }
  }
}'
```

### 2. `/contents` — Extract content from known URLs

Use when you already have URLs and need their content. Content options (`text` or `highlights`) go at the top level (not nested in `contents`).

```bash
curl -s -X POST 'https://api.exa.ai/contents' \
  -H "x-api-key: $EXA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
  "urls": ["https://example.com/article"],
  "highlights": { "max_characters": 4000 }
}'
```

### 3. `/answer` — Q&A with citations

Get a direct answer to a question, backed by web sources.

```bash
curl -s -X POST 'https://api.exa.ai/answer' \
  -H "x-api-key: $EXA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "What is the current status of Project X?",
  "text": true
}'
```

## Search Types

Pick the type based on the user's need:

| Type | When to use | Speed |
|------|-------------|-------|
| `auto` | **Default choice.** Balanced relevance and speed | ~2s |
| `fast` | Quick lookups, autocomplete-style queries | <1s |
| `deep` | Research, enrichment, thorough results. Supports `outputSchema` | 4-12s |
| `deep-reasoning` | Complex multi-step reasoning across many sources. Supports `outputSchema` | 10-30s |

Default to `auto` unless the user needs depth or structured output.

## Content Options

Choose ONE per `/search` request (nested inside `"contents"`):

| Option | Config | When to use |
|--------|--------|-------------|
| Highlights | `"highlights": {"max_characters": 4000}` | **Default.** Summaries, Q&A, general research — token-efficient |
| Text | `"text": {"max_characters": 10000}` | Full articles, code, documentation — higher token cost |

For `/contents` endpoint, these go at the **top level** (not inside `contents`).

**Default to highlights** to keep token usage low. Use text only when the user needs full content (code examples, complete documentation, etc.).

## Structured Outputs (Deep Search Only)

When `type` is `deep` or `deep-reasoning`, you can request structured JSON via `outputSchema`. Exa returns web-grounded data with field-level citations.

```bash
curl -s -X POST 'https://api.exa.ai/search' \
  -H "x-api-key: $EXA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "AI startups in healthcare France",
  "type": "deep",
  "outputSchema": {
    "type": "object",
    "required": ["companies"],
    "properties": {
      "companies": {
        "type": "array",
        "description": "Companies found",
        "items": {
          "type": "object",
          "required": ["name"],
          "properties": {
            "name": { "type": "string" },
            "description": { "type": "string" }
          }
        }
      }
    }
  },
  "contents": { "highlights": { "max_characters": 4000 } }
}'
```

Response shape:
- `output.content` — structured JSON matching your schema
- `output.grounding` — field-level citations with URLs and confidence

## Category Filters

Optional. Search dedicated indexes for specific content types:

| Category | Query style | Notes |
|----------|-------------|-------|
| `"people"` | Role/expertise description, singular form | No date/text filters |
| `"company"` | Industry/attributes, singular form | Returns company objects |
| `"news"` | Topic/event | Use `maxAgeHours: 24` for breaking news |
| `"research paper"` | Technical topic | Includes arxiv, paperswithcode |

```json
{ "category": "company", "query": "fintech startup payments Europe" }
```

Categories can be restrictive — try without one first if results are sparse.

## Domain Filtering

Usually not needed. Use only when targeting specific sources:

```json
{
  "includeDomains": ["arxiv.org", "github.com"],
  "excludeDomains": ["pinterest.com"]
}
```

## Content Freshness

`maxAgeHours` controls cache vs livecrawl:

| Value | Behavior |
|-------|----------|
| *(omit)* | **Recommended default.** Cache with livecrawl fallback |
| `24` | Livecrawl if cache > 24h old |
| `0` | Always livecrawl (real-time data) |
| `-1` | Cache only (fastest, for static/historical content) |

## Decision Tree

```
User needs web info
├─ Already has URLs? → /contents
├─ Wants a direct answer with citations? → /answer
└─ Needs to find pages?
   └─ /search
      ├─ Quick lookup → type: "fast"
      ├─ General search → type: "auto" (default)
      ├─ Deep research or structured data → type: "deep"
      └─ Complex multi-step reasoning → type: "deep-reasoning"
```

## Common Parameter Mistakes — AVOID

- `useAutoprompt` → **deprecated**, do not use
- `includeUrls` / `excludeUrls` → **do not exist**. Use `includeDomains` / `excludeDomains`
- `stream: true` → **not supported**
- `text`/`highlights` at top level of `/search` → **must be inside `contents`**
- `text`/`highlights` inside `contents` on `/contents` → **must be at top level**
- `livecrawl` → **deprecated**. Use `maxAgeHours` instead
- `numSentences`, `highlightsPerUrl` → **deprecated**. Use `max_characters`

## Output Formatting

After executing a search, present results to the user:
1. Summarize key findings in clear, concise French
2. Include source URLs for attribution
3. If using structured outputs, present the data in a readable format (table, list)
4. Flag low-confidence results if grounding data shows it

Always pipe curl through `jq` when available for readable output:
```bash
curl -s ... | jq .
```
