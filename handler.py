import os
import sys
import json

os.environ["PYTHONIOENCODING"] = "utf-8"

from signals.ats_detector import detect

SAMPLE_ARTICLES = [
    {
        "title": "Acme Corp begins Workday ATS migration",
        "url": "https://example.com/acme-workday",
        "summary": "Acme Corp announced HR transformation migrating to Workday. The hiring platform upgrade is part of recruitment automation to modernize their talent management system."
    },
    {
        "title": "TechStart deploys SuccessFactors recruitment automation",
        "url": "https://example.com/techstart",
        "summary": "TechStart is implementing SuccessFactors as part of ATS migration. Rolling out hiring workflow automation replacing their old applicant tracking system."
    },
    {
        "title": "GlobalBank evaluating ATS migration HR tech upgrade",
        "url": "https://example.com/globalbank",
        "summary": "GlobalBank evaluating ATS migration and HR transformation. Considering Workday for hiring platform upgrade and recruitment automation."
    },
    {
        "title": "RetailChain completes Lever hiring platform upgrade",
        "url": "https://example.com/retailchain",
        "summary": "RetailChain completed transition to Lever applicant tracking system. HR tech modernization included recruitment automation and workflow redesign."
    },
    {
        "title": "FinanceCo planning SuccessFactors iCIMS evaluation",
        "url": "https://example.com/finco",
        "summary": "FinanceCo planning HR transformation evaluating iCIMS and SuccessFactors. Hiring platform upgrade will support growing recruitment needs."
    }
]


def run_detection():
    signals = []
    for article in SAMPLE_ARTICLES:
        text = article["title"] + " " + article["summary"]
        words = article["title"].split()
        company = " ".join(words[:2]) if len(words) >= 2 else "Unknown"
        result = detect(company, text, article["url"])
        if result:
            result["data_source"] = "sample"
            signals.append(result)
    return signals


def detect_signals(event, context):
    try:
        signals = run_detection()
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/signals.json", "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=2, ensure_ascii=True)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "Detection complete",
                "total_signals": len(signals),
                "signals": signals
            }, ensure_ascii=True, indent=2)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}, ensure_ascii=True)
        }


def get_signals(event, context):
    try:
        if not os.path.exists("outputs/signals.json"):
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "No signals yet. Call /detect first."})
            }
        with open("outputs/signals.json", "r", encoding="utf-8") as f:
            signals = json.load(f)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "total_signals": len(signals),
                "signals": signals
            }, ensure_ascii=True, indent=2)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}, ensure_ascii=True)
        }


def health_check(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "running",
            "service": "ATS Signal Detector",
            "version": "1.0.0"
        }, ensure_ascii=True)
    }