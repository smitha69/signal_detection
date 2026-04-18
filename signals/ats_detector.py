# signals/ats_detector.py
from utils import get_timestamp

# Keywords to search for
ATS_KEYWORDS = [
    "workday", "successfactors", "ats migration",
    "hr transformation", "recruitment automation",
    "hiring platform upgrade", "applicant tracking",
    "hr tech", "talent management system"
]

TOOL_NAMES = [
    "workday", "successfactors", "greenhouse",
    "lever", "bamboohr", "icims", "taleo"
]

def detect(company_name, article_text, source_url):
    """
    Looks for ATS/HR signals in article text.
    Returns a signal record if found, otherwise None.
    """
    text_lower = article_text.lower()

    # Find which keywords appear in the text
    matched_keywords = [kw for kw in ATS_KEYWORDS if kw in text_lower]
    matched_tools = [tool for tool in TOOL_NAMES if tool in text_lower]

    # Only report if at least one keyword matched
    if not matched_keywords:
        return None

    # Calculate score: each keyword adds points
    score = min(len(matched_keywords) * 20 + len(matched_tools) * 10, 100)

    # Detect modernization stage from text
    stage = "unknown"
    if any(word in text_lower for word in ["planning", "evaluating", "considering"]):
        stage = "planning"
    elif any(word in text_lower for word in ["implementing", "deploying", "rolling out"]):
        stage = "implementing"
    elif any(word in text_lower for word in ["completed", "launched", "upgraded"]):
        stage = "completed"

    # Build the result record
    return {
        "company": company_name,
        "signal_type": "ats_modernization",
        "source_url": source_url,
        "matched_keywords": matched_keywords,
        "matched_tools": matched_tools,
        "modernization_stage": stage,
        "signal_score": score,
        "detected_at": get_timestamp(),
        "reason": f"ATS/HR tech modernization signal detected with {len(matched_keywords)} keyword(s)"
    } 
