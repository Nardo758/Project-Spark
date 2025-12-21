#!/usr/bin/env python3
"""
Import Twitter data from Apify dataset into OppGrid webhook pipeline.

Usage:
    python import_apify_twitter.py <dataset_id> [--limit N]
    
Example:
    python import_apify_twitter.py currsmULGRPQmcaYR --limit 100
"""

import argparse
import requests
import time
import os

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:8000/api/v1/webhooks/twitter")
APIFY_API_URL = "https://api.apify.com/v2/datasets/{dataset_id}/items"


def fetch_apify_dataset(dataset_id: str, limit: int = 1000) -> list:
    """Fetch items from Apify dataset."""
    url = APIFY_API_URL.format(dataset_id=dataset_id)
    params = {"format": "json", "clean": "true", "limit": limit}
    
    print(f"Fetching from Apify dataset: {dataset_id}")
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    items = response.json()
    print(f"Fetched {len(items)} items from Apify")
    return items


def push_to_webhook(items: list, batch_size: int = 50) -> dict:
    """Push items to webhook endpoint."""
    stats = {"accepted": 0, "duplicates": 0, "errors": 0}
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        batch_payload = {
            "items": [
                {
                    "id": str(item.get("id", "")),
                    "text": item.get("text", ""),
                    "url": item.get("url", ""),
                    "twitterUrl": item.get("twitterUrl", ""),
                    "retweetCount": item.get("retweetCount", 0),
                    "replyCount": item.get("replyCount", 0),
                    "likeCount": item.get("likeCount", 0),
                    "quoteCount": item.get("quoteCount", 0),
                    "createdAt": item.get("createdAt", ""),
                    "bookmarkCount": item.get("bookmarkCount", 0),
                    "isRetweet": item.get("isRetweet", False),
                    "isQuote": item.get("isQuote", False),
                }
                for item in batch
            ]
        }
        
        try:
            response = requests.post(
                WEBHOOK_URL.replace("/twitter", "/twitter/batch"),
                json=batch_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                stats["accepted"] += result.get("accepted", 0)
                stats["duplicates"] += result.get("duplicates", 0)
                stats["errors"] += result.get("errors", 0)
                print(f"Batch {i//batch_size + 1}: {result.get('accepted', 0)} accepted, {result.get('duplicates', 0)} duplicates")
            else:
                print(f"Batch {i//batch_size + 1} failed: {response.status_code}")
                stats["errors"] += len(batch)
                
        except Exception as e:
            print(f"Batch {i//batch_size + 1} error: {e}")
            stats["errors"] += len(batch)
        
        time.sleep(0.1)
    
    return stats


def push_single_items(items: list) -> dict:
    """Push items one by one (fallback if batch not available)."""
    stats = {"accepted": 0, "duplicates": 0, "errors": 0}
    
    for i, item in enumerate(items):
        payload = {
            "data": {
                "id": str(item.get("id", "")),
                "text": item.get("text", ""),
                "url": item.get("url", ""),
                "twitterUrl": item.get("twitterUrl", ""),
                "retweetCount": item.get("retweetCount", 0),
                "replyCount": item.get("replyCount", 0),
                "likeCount": item.get("likeCount", 0),
                "quoteCount": item.get("quoteCount", 0),
                "createdAt": item.get("createdAt", ""),
            }
        }
        
        try:
            response = requests.post(
                WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "")
                if status == "accepted":
                    stats["accepted"] += 1
                elif status == "duplicate":
                    stats["duplicates"] += 1
                else:
                    stats["errors"] += 1
            else:
                stats["errors"] += 1
                
            if (i + 1) % 50 == 0:
                print(f"Progress: {i + 1}/{len(items)} - Accepted: {stats['accepted']}, Duplicates: {stats['duplicates']}")
                
        except Exception as e:
            stats["errors"] += 1
            if (i + 1) % 50 == 0:
                print(f"Error at {i + 1}: {e}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Import Twitter data from Apify")
    parser.add_argument("dataset_id", help="Apify dataset ID")
    parser.add_argument("--limit", type=int, default=1000, help="Max items to fetch")
    parser.add_argument("--batch", action="store_true", help="Use batch endpoint")
    
    args = parser.parse_args()
    
    items = fetch_apify_dataset(args.dataset_id, args.limit)
    
    if not items:
        print("No items to import")
        return
    
    print(f"\nPushing {len(items)} items to webhook...")
    
    if args.batch:
        stats = push_to_webhook(items)
    else:
        stats = push_single_items(items)
    
    print(f"\n=== Import Complete ===")
    print(f"Accepted: {stats['accepted']}")
    print(f"Duplicates: {stats['duplicates']}")
    print(f"Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
