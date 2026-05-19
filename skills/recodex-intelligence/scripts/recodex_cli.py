#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
RecodeX Intelligence CLI — Query recodex.ai for startup funding intelligence.

Usage:
    uv run recodex_cli.py latest --type startup --limit 10 --output latest.json
    uv run recodex_cli.py search --query "AI 安全" --type startup --limit 10 --output results.json
    uv run recodex_cli.py category --list --output categories.json
    uv run recodex_cli.py company --name "Ocean" --output ocean.json
    uv run recodex_cli.py trending --period today --output today.json
    uv run recodex_cli.py funding --round "Seed" --limit 20 --output seeds.json
"""

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from html.parser import HTMLParser

BASE_URL = "https://recodex.ai/wp-json/wp/v2"
MIN_REQUEST_INTERVAL = 1.0  # seconds between requests
_last_request_time = 0.0


class HTMLTextExtractor(HTMLParser):
    """Strip HTML tags and extract plain text."""
    def __init__(self):
        super().__init__()
        self._text = []
    def handle_data(self, data):
        self._text.append(data)
    def get_text(self):
        return ''.join(self._text).strip()


def html_to_text(html_str):
    """Convert HTML string to plain text."""
    if not html_str:
        return ""
    extractor = HTMLTextExtractor()
    extractor.feed(html_str)
    text = extractor.get_text()
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _request(url, max_retries=3):
    """Make an HTTP GET request with rate limiting and retry logic."""
    global _last_request_time

    # Rate limiting
    now = time.monotonic()
    elapsed = now - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)

    headers = {
        "User-Agent": "RecodeX-Intelligence-Skill/1.0",
        "Accept": "application/json",
    }

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            _last_request_time = time.monotonic()
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode("utf-8")
                total = resp.headers.get("X-WP-Total")
                total_pages = resp.headers.get("X-WP-TotalPages")
                return json.loads(data), {
                    "total": int(total) if total else None,
                    "total_pages": int(total_pages) if total_pages else None,
                }
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 2 ** (attempt + 1)
                print(f"Rate limited (429). Retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            elif e.code >= 500:
                wait = 2 ** attempt
                print(f"Server error ({e.code}). Retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            else:
                body = e.read().decode("utf-8", errors="replace") if e.fp else ""
                print(f"HTTP {e.code} for {url}: {body[:500]}", file=sys.stderr)
                sys.exit(1)
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"Connection error: {e.reason}. Retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"Failed after {max_retries} attempts: {e.reason}", file=sys.stderr)
                sys.exit(1)

    print("Max retries exceeded.", file=sys.stderr)
    sys.exit(1)


def _fetch_categories_map():
    """Fetch and return a dict mapping category name -> category id."""
    url = f"{BASE_URL}/startup_category?per_page=100"
    data, _ = _request(url)
    return {item["name"]: item["id"] for item in data}


def _format_startup(post):
    """Format a startup post into a clean dict."""
    meta = post.get("meta", {})
    content_html = post.get("content", {}).get("rendered", "")
    excerpt_html = post.get("excerpt", {}).get("rendered", "")

    # Get plain text excerpt (first 500 chars of content if no excerpt)
    excerpt = html_to_text(excerpt_html)
    if not excerpt:
        excerpt = html_to_text(content_html)[:500]
    if len(excerpt) > 500:
        excerpt = excerpt[:500] + "..."

    return {
        "id": post["id"],
        "title": html_to_text(post.get("title", {}).get("rendered", "")),
        "url": post.get("link", ""),
        "date": post.get("date", ""),
        "type": "startup",
        "company_name": meta.get("_startup_company_name", ""),
        "funding_round": meta.get("_startup_funding_round", ""),
        "funding_amount": meta.get("_startup_funding_amount", ""),
        "investors": meta.get("_startup_investors", ""),
        "website": meta.get("_startup_website", ""),
        "excerpt": excerpt,
    }


def _format_flash(post):
    """Format a flash news post into a clean dict."""
    meta = post.get("meta", {})
    return {
        "id": post["id"],
        "title": html_to_text(post.get("title", {}).get("rendered", "")),
        "url": post.get("link", ""),
        "date": post.get("date", ""),
        "type": "flash_news",
        "content": html_to_text(post.get("content", {}).get("rendered", "")),
        "source_name": meta.get("_flash_source_name", ""),
        "source_url": meta.get("_flash_source_url", ""),
    }


def _fetch_paginated(endpoint, params, limit, formatter):
    """Fetch results with pagination up to limit."""
    results = []
    page = 1
    per_page = min(limit, 100)
    params["per_page"] = per_page

    while len(results) < limit:
        params["page"] = page
        query = urllib.parse.urlencode(params, safe="%")
        url = f"{BASE_URL}/{endpoint}?{query}"
        data, meta = _request(url)

        if not data:
            break

        for post in data:
            if len(results) >= limit:
                break
            results.append(formatter(post))

        total_pages = meta.get("total_pages") or 1
        if page >= total_pages:
            break
        page += 1

    return results, meta


def _write_output(data, output_path, meta_info=None):
    """Write results to a JSON file."""
    output = {
        "source": "recodex.ai",
        "query_time": datetime.utcnow().isoformat() + "Z",
        "total_available": meta_info.get("total") if meta_info else None,
        "count": len(data),
        "results": data,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Success! {len(data)} results written to: {output_path}")


# ── Subcommand handlers ──────────────────────────────────────────────


def cmd_latest(args):
    """Fetch the latest content."""
    results = []
    meta = {}

    if args.type in ("startup", "all"):
        startup_results, startup_meta = _fetch_paginated(
            "startup", {"orderby": "date", "order": "desc"}, args.limit, _format_startup
        )
        results.extend(startup_results)
        meta = startup_meta

    if args.type in ("flash", "all"):
        remaining = args.limit - len(results) if args.type == "all" else args.limit
        if remaining > 0:
            flash_results, flash_meta = _fetch_paginated(
                "flash_news", {"orderby": "date", "order": "desc"}, remaining, _format_flash
            )
            results.extend(flash_results)
            if not meta.get("total"):
                meta = flash_meta

    # Sort by date if mixed
    if args.type == "all":
        results.sort(key=lambda x: x.get("date", ""), reverse=True)
        results = results[:args.limit]

    _write_output(results, args.output, meta)


def cmd_search(args):
    """Search by keyword."""
    results = []
    meta = {}

    if args.type in ("startup", "all"):
        startup_results, startup_meta = _fetch_paginated(
            "startup", {"search": args.query, "orderby": "relevance", "order": "desc"},
            args.limit, _format_startup
        )
        results.extend(startup_results)
        meta = startup_meta

    if args.type in ("flash", "all"):
        remaining = args.limit - len(results) if args.type == "all" else args.limit
        if remaining > 0:
            flash_results, flash_meta = _fetch_paginated(
                "flash_news", {"search": args.query, "orderby": "relevance", "order": "desc"},
                remaining, _format_flash
            )
            results.extend(flash_results)

    _write_output(results, args.output, meta)


def cmd_category(args):
    """Browse by category."""
    if args.list:
        url = f"{BASE_URL}/startup_category?per_page=100"
        data, _ = _request(url)
        categories = [
            {"name": c["name"], "slug": c["slug"], "count": c["count"], "url": c["link"]}
            for c in sorted(data, key=lambda x: x["count"], reverse=True)
        ]
        output = {
            "source": "recodex.ai",
            "query_time": datetime.utcnow().isoformat() + "Z",
            "count": len(categories),
            "categories": categories,
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Success! {len(categories)} categories written to: {args.output}")
        return

    if not args.name:
        print("Error: --name is required when not using --list", file=sys.stderr)
        sys.exit(1)
    if not args.limit:
        print("Error: --limit is required when not using --list", file=sys.stderr)
        sys.exit(1)

    # Find category ID by name
    cat_map = _fetch_categories_map()
    cat_id = cat_map.get(args.name)
    if not cat_id:
        print(f"Error: Category '{args.name}' not found.", file=sys.stderr)
        print(f"Available categories: {', '.join(sorted(cat_map.keys()))}", file=sys.stderr)
        sys.exit(1)

    results, meta = _fetch_paginated(
        "startup", {"startup_category": cat_id, "orderby": "date", "order": "desc"},
        args.limit, _format_startup
    )
    _write_output(results, args.output, meta)


def cmd_company(args):
    """Lookup a specific company by name."""
    # Search by company name in content/title
    results, meta = _fetch_paginated(
        "startup", {"search": args.name, "orderby": "date", "order": "desc"},
        50, _format_startup
    )

    # Filter to exact company name match in metadata
    exact = [r for r in results if r["company_name"].lower() == args.name.lower()]

    # If no exact match, try partial
    if not exact:
        exact = [r for r in results if args.name.lower() in r["company_name"].lower()]

    if not exact:
        print(f"No reports found for company: {args.name}", file=sys.stderr)
        # Still write empty result
        _write_output([], args.output)
        return

    _write_output(exact, args.output, meta)


def cmd_trending(args):
    """Get content from a time period."""
    now = datetime.utcnow()

    if args.period == "today":
        after = now.replace(hour=0, minute=0, second=0).isoformat()
    elif args.period == "week":
        after = (now - timedelta(days=7)).isoformat()
    elif args.after:
        after = args.after + "T00:00:00"
    else:
        print("Error: Specify --period (today/week) or --after/--before", file=sys.stderr)
        sys.exit(1)

    before = None
    if args.before:
        before = args.before + "T23:59:59"

    params = {"after": after, "orderby": "date", "order": "desc"}
    if before:
        params["before"] = before

    # Fetch startups
    startup_results, s_meta = _fetch_paginated("startup", dict(params), 100, _format_startup)

    # Fetch flash news
    flash_results, f_meta = _fetch_paginated("flash_news", dict(params), 100, _format_flash)

    all_results = startup_results + flash_results
    all_results.sort(key=lambda x: x.get("date", ""), reverse=True)

    total_meta = {"total": (s_meta.get("total") or 0) + (f_meta.get("total") or 0)}
    _write_output(all_results, args.output, total_meta)


def cmd_funding(args):
    """Filter by funding round or amount."""
    # Fetch a large batch of startups
    all_results, meta = _fetch_paginated(
        "startup", {"orderby": "date", "order": "desc"},
        min(args.limit * 5, 100),  # Fetch more to filter from
        _format_startup
    )

    filtered = all_results

    if args.round:
        round_lower = args.round.lower()
        filtered = [
            r for r in filtered
            if round_lower in r.get("funding_round", "").lower()
        ]

    if args.amount_keyword:
        filtered = [
            r for r in filtered
            if args.amount_keyword in r.get("funding_amount", "")
        ]

    filtered = filtered[:args.limit]
    _write_output(filtered, args.output, meta)


# ── CLI setup ─────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="RecodeX Intelligence — Query recodex.ai for startup funding intelligence"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # latest
    p_latest = subparsers.add_parser("latest", help="Get the latest content")
    p_latest.add_argument("--type", required=True, choices=["startup", "flash", "all"])
    p_latest.add_argument("--limit", required=True, type=int)
    p_latest.add_argument("--output", required=True)

    # search
    p_search = subparsers.add_parser("search", help="Search by keyword")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--type", required=True, choices=["startup", "flash", "all"])
    p_search.add_argument("--limit", required=True, type=int)
    p_search.add_argument("--output", required=True)

    # category
    p_cat = subparsers.add_parser("category", help="Browse by sector category")
    p_cat.add_argument("--list", action="store_true", help="List all categories")
    p_cat.add_argument("--name", help="Category name in Chinese")
    p_cat.add_argument("--limit", type=int)
    p_cat.add_argument("--output", required=True)

    # company
    p_company = subparsers.add_parser("company", help="Lookup a specific company")
    p_company.add_argument("--name", required=True)
    p_company.add_argument("--output", required=True)

    # trending
    p_trend = subparsers.add_parser("trending", help="Get content from a time period")
    p_trend.add_argument("--period", choices=["today", "week"])
    p_trend.add_argument("--after", help="Start date (YYYY-MM-DD)")
    p_trend.add_argument("--before", help="End date (YYYY-MM-DD)")
    p_trend.add_argument("--output", required=True)

    # funding
    p_fund = subparsers.add_parser("funding", help="Filter by funding details")
    p_fund.add_argument("--round", help="Funding round (Seed, Pre-Seed, A, B, etc.)")
    p_fund.add_argument("--amount-keyword", help="Keyword to match in funding amount")
    p_fund.add_argument("--limit", required=True, type=int)
    p_fund.add_argument("--output", required=True)

    args = parser.parse_args()

    commands = {
        "latest": cmd_latest,
        "search": cmd_search,
        "category": cmd_category,
        "company": cmd_company,
        "trending": cmd_trending,
        "funding": cmd_funding,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
