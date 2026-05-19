---
name: recodex-intelligence
description: >-
  Query RecodeX (recodex.ai) for real-time startup funding news, original
  reports, and flash news in Chinese. Use when the user asks about startup
  fundraising, venture capital deals, investor activity, specific companies,
  or wants to browse startups by sector (AI, fintech, biotech, cybersecurity,
  etc.). Supports searching by keyword, category, company name, funding round,
  and date range. Acts as an AI-native intelligence feed for venture capital
  and startup ecosystem research.
---

# RecodeX Intelligence

Real-time startup funding intelligence from [recodex.ai](https://recodex.ai) — a Chinese-language venture capital and startup news platform covering global fundraising rounds, original deep-dive reports, and 7x24 flash news.

## Overview

RecodeX publishes daily:
- **原创报道 (Original Reports)**: Deep-dive analyses of startup funding rounds with structured metadata (company, amount, round, investors, website)
- **7x24 快讯 (Flash News)**: Real-time financial and tech news feed

This skill provides CLI commands to query this content programmatically, returning structured JSON that agents can directly understand and act upon.

## Quick Start

Get the latest 5 startup funding reports:
```bash
uv run /Users/will/.gemini/config/plugins/recodex/skills/recodex-intelligence/scripts/recodex_cli.py latest --type startup --limit 5 --output latest.json
```

Search for a specific company:
```bash
uv run /Users/will/.gemini/config/plugins/recodex/skills/recodex-intelligence/scripts/recodex_cli.py company --name "Ocean" --output ocean.json
```

## Utility Scripts

The main CLI script is located at:
```
/Users/will/.gemini/config/plugins/recodex/skills/recodex-intelligence/scripts/recodex_cli.py
```

All commands use `uv run` and write output to JSON files via `--output`.

### `latest` — Get the latest content

Fetches the most recent startup reports or flash news.

```bash
# Latest 10 startup reports
uv run .../recodex_cli.py latest --type startup --limit 10 --output latest_startups.json

# Latest 20 flash news items
uv run .../recodex_cli.py latest --type flash --limit 20 --output latest_flash.json

# Latest 15 items of all types
uv run .../recodex_cli.py latest --type all --limit 15 --output latest_all.json
```

**Arguments:**
- `--type` (required): `startup`, `flash`, or `all`
- `--limit` (required): Number of results (max 100)
- `--output` (required): Output JSON file path

### `search` — Keyword search

Search across titles and content. Works for company names, investor names, technologies, etc.

```bash
# Search for AI security startups
uv run .../recodex_cli.py search --query "AI 安全" --type startup --limit 10 --output results.json

# Search for a16z investments
uv run .../recodex_cli.py search --query "a16z" --type startup --limit 20 --output a16z.json

# Search flash news for crypto
uv run .../recodex_cli.py search --query "比特币" --type flash --limit 10 --output btc.json
```

**Arguments:**
- `--query` (required): Search keywords
- `--type` (required): `startup`, `flash`, or `all`
- `--limit` (required): Number of results
- `--output` (required): Output JSON file path

### `category` — Browse by sector

List available categories or fetch articles from a specific sector.

```bash
# List all categories with article counts
uv run .../recodex_cli.py category --list --output categories.json

# Get AI sector reports
uv run .../recodex_cli.py category --name "AI人工智能" --limit 10 --output ai.json

# Get fintech reports
uv run .../recodex_cli.py category --name "金融科技" --limit 10 --output fintech.json
```

**Available categories:** AI人工智能, 前沿科技, 金融科技, 医疗健康, 企业SaaS, 生物科技, 消费品牌, 气候科技, 硬件/芯片, 网络安全, 加密货币, Web3, 机器人, 娱乐游戏, 太空科技, 风险投资

**Arguments:**
- `--list`: List all categories (no other args needed)
- `--name` (required if not --list): Category name in Chinese
- `--limit` (required if not --list): Number of results
- `--output` (required): Output JSON file path

### `company` — Lookup a specific company

Exact-match search by company name in the structured metadata.

```bash
uv run .../recodex_cli.py company --name "Ocean" --output ocean.json
uv run .../recodex_cli.py company --name "Exhibitly" --output exhibitly.json
```

**Arguments:**
- `--name` (required): Company name (English, as stored in metadata)
- `--output` (required): Output JSON file path

### `trending` — Time-based content

Get all content from a specific time period.

```bash
# Today's content
uv run .../recodex_cli.py trending --period today --output today.json

# This week's content
uv run .../recodex_cli.py trending --period week --output week.json

# Custom date range
uv run .../recodex_cli.py trending --after 2026-05-15 --before 2026-05-20 --output range.json
```

**Arguments:**
- `--period`: `today` or `week` (convenience shortcuts)
- `--after` / `--before`: Custom ISO date range (YYYY-MM-DD)
- `--output` (required): Output JSON file path

### `funding` — Filter by funding details

Search by funding round type or amount keywords.

```bash
# All seed rounds
uv run .../recodex_cli.py funding --round "Seed" --limit 20 --output seeds.json

# All Series A
uv run .../recodex_cli.py funding --round "A" --limit 20 --output series_a.json

# Search by amount keyword
uv run .../recodex_cli.py funding --amount-keyword "1亿" --limit 10 --output big.json
```

**Arguments:**
- `--round`: Funding round type (Seed, Pre-Seed, A, B, C, etc.)
- `--amount-keyword`: Keyword to match in funding amount field
- `--limit` (required): Number of results
- `--output` (required): Output JSON file path

## Output Format

### Startup Report

```json
{
  "id": 240978,
  "title": "Ocean 获 2800 万美元融资：用自主 AI 代理重构企业邮件安全防线",
  "url": "https://recodex.ai/startup/cybersecurity/240978.html",
  "date": "2026-05-20T04:55:18",
  "type": "startup",
  "category": "网络安全",
  "company_name": "Ocean",
  "funding_round": "Seed",
  "funding_amount": "$2800万",
  "investors": "Lightspeed Venture Partners (领投)...",
  "website": "https://www.ocean.security",
  "excerpt": "一家名为 Ocean 的网络安全初创公司..."
}
```

### Flash News

```json
{
  "id": 240991,
  "title": "SCHMID集团发布2025财年第四季度财报...",
  "url": "https://recodex.ai/news/stocks/240991.html",
  "date": "2026-05-20T05:06:20",
  "type": "flash_news",
  "source_name": "seekingalpha.com",
  "source_url": "https://seekingalpha.com/article/..."
}
```

## Rate Limiting

The skill enforces a default rate limit of **1 request per second** to be respectful to the recodex.ai server. This is implemented via `time.monotonic()` based throttling in the CLI script.

## Common Mistakes

1. **Category names must be in Chinese**: Use `AI人工智能` not `ai` or `AI`. Run `category --list` first to see available names.
2. **Company names are in English**: The `company` command matches against the English company name stored in metadata (e.g., `Ocean`, not `海洋`).
3. **Always specify `--limit`**: There is no default limit. You must explicitly set how many results you want to avoid accidentally fetching hundreds of articles.
