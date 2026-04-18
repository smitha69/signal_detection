# main.py
import requests
import feedparser
import json
import os
from bs4 import BeautifulSoup
from utils import clean_text
from signals.ats_detector import detect

# ── Better RSS Feeds for HR/ATS news ──────────────────────
RSS_FEEDS = [
    "https://feeds.feedburner.com/ERE-Recruiting-Intelligence",
    "https://www.ere.net/feed/",
    "https://www.hr-brew.com/rss",
    "https://www.hrdive.com/feeds/news/",
    "https://www.shrm.org/rss/pages/rss.aspx",
]

# ── Sample/fallback articles (always processed) ───────────
# These simulate real-world articles for testing your detector
SAMPLE_ARTICLES = [
    {
        "title": "Acme Corp begins Workday ATS migration for 5000 employees",
        "url": "https://example.com/acme-workday",
        "summary": "Acme Corp announced a major HR transformation initiative, migrating from legacy systems to Workday. The hiring platform upgrade is part of a broader recruitment automation strategy to modernize their talent management system."
    },
    {
        "title": "TechStart deploys SuccessFactors for recruitment automation",
        "url": "https://example.com/techstart-successfactors",
        "summary": "TechStart is implementing SAP SuccessFactors as part of its ATS migration. The company is rolling out hiring workflow automation across all departments, replacing their old applicant tracking system."
    },
    {
        "title": "GlobalBank evaluating ATS migration and HR tech stack upgrade",
        "url": "https://example.com/globalbank-ats",
        "summary": "GlobalBank is currently evaluating options for ATS migration and HR transformation. They are considering Workday and Greenhouse for their new hiring platform upgrade and recruitment automation needs."
    },
    {
        "title": "RetailChain completes Lever hiring platform upgrade",
        "url": "https://example.com/retailchain-lever",
        "summary": "RetailChain has completed its transition to Lever, a modern applicant tracking system. The HR tech modernization project included full recruitment automation and workflow redesign."
    },
    {
        "title": "FinanceCo planning SuccessFactors and iCIMS evaluation",
        "url": "https://example.com/finco-icims",
        "summary": "FinanceCo is planning a major HR transformation by evaluating iCIMS and SuccessFactors. The hiring platform upgrade will support their growing recruitment needs."
    }
]

OUTPUT_FILE = "outputs/signals.json"

# ── Step 1: Fetch articles from RSS feeds ─────────────────
def fetch_articles():
    articles = []
    for feed_url in RSS_FEEDS:
        print(f"Fetching: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "source": "rss"
                })
            print(f"  Got {len(feed.entries)} articles")
        except Exception as e:
            print(f"  Error: {e}")

    # Always add sample articles for guaranteed results
    print(f"\nAdding {len(SAMPLE_ARTICLES)} sample/test articles...")
    for a in SAMPLE_ARTICLES:
        a["source"] = "sample"
        articles.append(a)

    print(f"Total articles to check: {len(articles)}\n")
    return articles

# ── Step 2: Extract company name from title ───────────────
def extract_company(title):
    """Simple company extractor — takes first word(s) before a verb"""
    words = title.split()
    # Return first 2 words as company name guess
    return " ".join(words[:2]) if len(words) >= 2 else "Unknown"

# ── Step 3: Run detection on each article ─────────────────
def run_detection(articles):
    signals = []
    for article in articles:
        title = article.get("title", "")
        summary = article.get("summary", "")
        url = article.get("url", "")
        source = article.get("source", "rss")

        # Combine title + summary as the text to analyze
        text = title + " " + summary
        company = extract_company(title)

        result = detect(company, text, url)
        if result:
            result["data_source"] = source  # mark if real or sample
            print(f"  ✓ SIGNAL FOUND in: {title[:55]}...")
            print(f"    Company: {company} | Score: {result['signal_score']} | Stage: {result['modernization_stage']}")
            print(f"    Keywords: {result['matched_keywords']}")
            print()
            signals.append(result)
        else:
            print(f"  - No signal: {title[:55]}...")

    return signals

# ── Step 4: Save results to JSON ──────────────────────────
def save_results(signals):
    os.makedirs("outputs", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(signals, f, indent=2)
    print(f"\n{'='*40}")
    print(f"Done! {len(signals)} signal(s) saved to {OUTPUT_FILE}")
    print(f"{'='*40}")

    # Print a summary table
    if signals:
        print(f"\n{'COMPANY':<20} {'SCORE':<8} {'STAGE':<15} {'SOURCE'}")
        print("-" * 60)
        for s in signals:
            print(f"{s['company']:<20} {s['signal_score']:<8} {s['modernization_stage']:<15} {s.get('data_source','')}")

# ── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 40)
    print("   ATS / HR Tech Signal Detector")
    print("=" * 40 + "\n")
    articles = fetch_articles()
    print("--- Scanning articles ---\n")
    signals = run_detection(articles)
    save_results(signals)