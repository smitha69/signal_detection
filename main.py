# -*- coding: utf-8 -*-
import sys
import io
import requests
import feedparser
import json
import os
from bs4 import BeautifulSoup
from utils import clean_text
from signals.ats_detector import detect

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── RSS Feeds (fast timeout) ──────────────────────────────
RSS_FEEDS = [
    "https://www.hrdive.com/feeds/news/",
]

# ── Sample articles (always processed instantly) ──────────
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

# ── Fetch articles ─────────────────────────────────────────
def fetch_articles():
    articles = []

    for feed_url in RSS_FEEDS:
        print(f"Fetching: {feed_url}")
        try:
            # Short timeout so it never hangs
            feed = feedparser.parse(feed_url, request_headers={
                'Connection': 'close'
            })
            count = 0
            for entry in feed.entries[:5]:
                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", ""),
                    "source": "rss"
                })
                count += 1
            print(f"  Got {count} articles")
        except Exception as e:
            print(f"  Skipped: {e}")

    # Always add sample articles
    for a in SAMPLE_ARTICLES:
        articles.append({
            "title": a["title"],
            "url": a["url"],
            "summary": a["summary"],
            "source": "sample"
        })

    print(f"Total articles: {len(articles)}")
    return articles

# ── Extract company name ───────────────────────────────────
def extract_company(title):
    words = title.split()
    return " ".join(words[:2]) if len(words) >= 2 else "Unknown"

# ── Run detection ──────────────────────────────────────────
def run_detection(articles):
    signals = []
    for article in articles:
        title = article.get("title", "")
        summary = article.get("summary", "")
        url = article.get("url", "")
        source = article.get("source", "rss")

        text = title + " " + summary
        company = extract_company(title)

        result = detect(company, text, url)
        if result:
            result["data_source"] = source
            print(f"  >> SIGNAL FOUND: {title[:50]}...")
            print(f"     Score: {result['signal_score']} | Stage: {result['modernization_stage']}")
            signals.append(result)
        else:
            print(f"  - No signal: {title[:50]}...")

    return signals

# ── Save results ───────────────────────────────────────────
def save_results(signals):
    os.makedirs("outputs", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=2, ensure_ascii=True)
    print(f"Done! {len(signals)} signal(s) saved.")

# ── CLI runner ────────────────────────────────