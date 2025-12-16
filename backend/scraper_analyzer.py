"""
Reddit Scraper Data Analyzer
Extracts business opportunities from scraped Reddit data using NLP pattern matching
"""

import json
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime

PROBLEM_SIGNALS = {
    "I wish there was": 1.0,
    "Why doesn't anyone make": 1.0,
    "Can someone please build": 1.0,
    "I'd pay for a solution": 0.95,
    "I would pay for": 0.95,
    "shut up and take my money": 0.95,
    "someone needs to make": 0.90,
    "why isn't there": 0.90,
    "there should be": 0.85,
    "So frustrating that": 0.85,
    "I can't believe we still": 0.85,
    "every single time": 0.80,
    "sick and tired of": 0.80,
    "fed up with": 0.80,
    "Does anyone else struggle": 0.75,
    "Am I the only one who": 0.75,
    "How do you deal with": 0.70,
    "is there a better way": 0.70,
    "there has to be a better": 0.70,
    "gave up on": 0.60,
    "just me": 0.55,
    "anyone else": 0.55,
    "is there an app": 0.80,
    "is there a service": 0.80,
    "looking for a solution": 0.75,
    "need help with": 0.50,
}

INTENSITY_MULTIPLIERS = {
    "!!!": 1.2,
    "!!": 1.15,
    "always": 1.1,
    "constantly": 1.1,
    "every single": 1.15,
    "never": 1.1,
    "impossible": 1.15,
    "nightmare": 1.2,
    "horrible": 1.1,
    "terrible": 1.1,
    "awful": 1.1,
}

TIER_1_SUBREDDITS = [
    "somebodymakethis",
    "mildlyinfuriating", 
    "crappydesign",
    "doesanybodyelse",
    "lightbulb",
    "crazyideas",
]

TIER_2_SUBREDDITS = [
    "entrepreneur",
    "smallbusiness",
    "startups",
    "sideproject",
    "consulting",
    "freelance",
    "business",
    "saas",
]

CATEGORY_KEYWORDS = {
    "Money & Finance": ["money", "finance", "bank", "invest", "budget", "tax", "invoice", "payment", "subscription"],
    "Health & Wellness": ["health", "fitness", "gym", "doctor", "medical", "mental health", "therapy", "diet", "nutrition"],
    "Technology": ["app", "software", "tech", "computer", "phone", "device", "automation", "ai", "tool"],
    "Work & Productivity": ["work", "productivity", "remote", "office", "meeting", "project", "task", "time"],
    "Home & Living": ["home", "house", "apartment", "rent", "furniture", "clean", "repair", "maintenance"],
    "Transportation": ["car", "drive", "parking", "commute", "transit", "uber", "travel", "flight"],
    "Shopping & Services": ["shop", "buy", "order", "delivery", "shipping", "ecommerce", "retail"],
    "Education & Learning": ["learn", "course", "education", "school", "tutor", "study", "training"],
    "Entertainment & Social": ["event", "social", "friends", "party", "restaurant", "dating"],
}


def calculate_pattern_score(text: str) -> Tuple[float, List[str]]:
    """Calculate pattern match score and return matched phrases"""
    text_lower = text.lower()
    max_score = 0.0
    matched_phrases = []
    
    for phrase, score in PROBLEM_SIGNALS.items():
        if phrase.lower() in text_lower:
            matched_phrases.append(phrase)
            if score > max_score:
                max_score = score
    
    return max_score, matched_phrases


def calculate_intensity_multiplier(text: str) -> float:
    """Calculate intensity multiplier based on markers"""
    multiplier = 1.0
    text_lower = text.lower()
    
    for marker, mult in INTENSITY_MULTIPLIERS.items():
        if marker.lower() in text_lower:
            multiplier = max(multiplier, mult)
    
    return multiplier


def get_subreddit_tier_bonus(subreddit: str) -> float:
    """Get bonus score based on subreddit tier"""
    sub_lower = subreddit.lower()
    
    if sub_lower in TIER_1_SUBREDDITS:
        return 0.15
    elif sub_lower in TIER_2_SUBREDDITS:
        return 0.05
    return 0.0


def get_engagement_bonus(upvotes: int, comments: int) -> float:
    """Get bonus based on community engagement"""
    bonus = 0.0
    if upvotes > 100:
        bonus += 0.10
    elif upvotes > 50:
        bonus += 0.07
    elif upvotes > 10:
        bonus += 0.05
    
    if comments > 50:
        bonus += 0.05
    elif comments > 20:
        bonus += 0.03
    
    return bonus


def detect_category(text: str) -> str:
    """Detect category based on keywords"""
    text_lower = text.lower()
    category_scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            category_scores[category] = score
    
    if category_scores:
        return max(category_scores, key=category_scores.get)
    return "Technology"


def analyze_post(post: Dict) -> Optional[Dict]:
    """Analyze a single post and return opportunity data if score >= 0.70"""
    title = post.get("title", "") or ""
    body = post.get("body", "") or ""
    full_text = f"{title} {body}"
    
    if len(full_text.strip()) < 20:
        return None
    
    subreddit = post.get("parsedCommunityName", "") or ""
    upvotes = post.get("upVotes", 0) or 0
    comments = post.get("commentsCount", 0) or 0
    
    base_score, matched_phrases = calculate_pattern_score(full_text)
    
    if base_score == 0:
        return None
    
    intensity_mult = calculate_intensity_multiplier(full_text)
    score = base_score * intensity_mult
    
    score += get_subreddit_tier_bonus(subreddit)
    score += get_engagement_bonus(upvotes, comments)
    
    score = min(score, 1.0)
    
    if score < 0.70:
        return None
    
    category = detect_category(full_text)
    
    description = body[:500] if body else title
    if len(body) > 500:
        description = body[:497] + "..."
    
    return {
        "title": title[:200] if title else "Untitled Opportunity",
        "description": description,
        "category": category,
        "source_url": post.get("postUrl", ""),
        "source_subreddit": subreddit,
        "confidence_score": round(score, 2),
        "matched_phrases": matched_phrases,
        "upvotes": upvotes,
        "comments": comments,
        "scraped_at": post.get("crawledAt", ""),
    }


def analyze_scraped_data(file_path: str) -> List[Dict]:
    """Analyze scraped data file and extract opportunities"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    opportunities = []
    
    for post in data:
        result = analyze_post(post)
        if result:
            opportunities.append(result)
    
    opportunities.sort(key=lambda x: x["confidence_score"], reverse=True)
    
    return opportunities


def print_analysis_report(opportunities: List[Dict], total_posts: int):
    """Print analysis report"""
    print(f"\n{'='*60}")
    print("REDDIT SCRAPER ANALYSIS REPORT")
    print(f"{'='*60}")
    print(f"Total posts analyzed: {total_posts}")
    print(f"Valid opportunities found: {len(opportunities)}")
    print(f"Conversion rate: {len(opportunities)/total_posts*100:.1f}%")
    
    print(f"\n{'='*60}")
    print("TOP OPPORTUNITIES (Score >= 0.70)")
    print(f"{'='*60}")
    
    for i, opp in enumerate(opportunities[:20], 1):
        print(f"\n{i}. [{opp['confidence_score']:.2f}] {opp['title'][:80]}")
        print(f"   Category: {opp['category']}")
        print(f"   Subreddit: r/{opp['source_subreddit']}")
        print(f"   Matched: {', '.join(opp['matched_phrases'])}")
        print(f"   Engagement: {opp['upvotes']} upvotes, {opp['comments']} comments")


if __name__ == "__main__":
    import sys
    
    file_path = sys.argv[1] if len(sys.argv) > 1 else "attached_assets/dataset_reddit-scraper-pro_2025-12-14_15-48-01-721_1765727833977.json"
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    opportunities = analyze_scraped_data(file_path)
    print_analysis_report(opportunities, len(data))
    
    output_file = "analyzed_opportunities.json"
    with open(output_file, 'w') as f:
        json.dump(opportunities, f, indent=2)
    print(f"\nResults saved to: {output_file}")
