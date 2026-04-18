# Design Explanation

## Data Ingestion Approach
- Fetches articles from public HR/tech RSS feeds using `feedparser`
- Falls back to curated sample articles to guarantee testable output
- Article text (title + summary) is cleaned and lowercased before analysis

## Scoring Logic
- Each matched ATS/HR keyword adds 20 points to the score
- Each matched tool name (Workday, Lever, etc.) adds 10 points
- Score is capped at 100
- Example: 3 keywords + 1 tool = 3×20 + 1×10 = 70 points

## Modernization Stage Detection
- "planning"      → article contains: evaluating, considering, planning
- "implementing"  → article contains: implementing, deploying, rolling out
- "completed"     → article contains: completed, launched, upgraded
- "unknown"       → none of the above words found

## Assumptions
- Company name is estimated from the first two words of the article title
- Only title + summary are analyzed (not full article body) to keep it fast
- Sample articles are included to demonstrate the detector works reliably

## Limitations
- Company name extraction is basic — not 100% accurate
- RSS feeds may not always return HR-specific content
- No deduplication of signals from multiple sources
- Score is keyword-count based, not semantic