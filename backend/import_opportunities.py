"""
Import analyzed opportunities into OppGrid database
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine, Base
from app.models.opportunity import Opportunity
from app.models.user import User

def import_opportunities(json_file: str):
    """Import opportunities from analyzed JSON file"""
    
    with open(json_file, 'r') as f:
        opportunities = json.load(f)
    
    if not opportunities:
        print("No opportunities to import")
        return
    
    db = SessionLocal()
    
    try:
        demo_user = db.query(User).filter(User.email == "demo@example.com").first()
        author_id = demo_user.id if demo_user else None
        
        imported = 0
        skipped = 0
        
        for opp in opportunities:
            title = opp.get("title", "")[:200]
            if not title or title == "Untitled Opportunity":
                skipped += 1
                continue
            
            existing = db.query(Opportunity).filter(Opportunity.title == title).first()
            if existing:
                print(f"Skipping duplicate: {title[:50]}...")
                skipped += 1
                continue
            
            new_opp = Opportunity(
                title=title,
                description=opp.get("description", "")[:2000],
                category=opp.get("category", "Technology"),
                subcategory="Reddit Discovery",
                severity=3,
                validation_count=opp.get("upvotes", 0),
                growth_rate=round(opp.get("confidence_score", 0.7) * 20, 1),
                market_size="$10M-$50M",
                geographic_scope="online",
                author_id=author_id,
                is_anonymous=True if not author_id else False,
                completion_status="open",
                status="active",
                source_url=opp.get("source_url", ""),
            )
            
            db.add(new_opp)
            imported += 1
            print(f"Imported: {title[:60]}...")
        
        db.commit()
        print(f"\n{'='*50}")
        print(f"Import complete: {imported} imported, {skipped} skipped")
        print(f"{'='*50}")
        
    except Exception as e:
        db.rollback()
        print(f"Error importing: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    json_file = sys.argv[1] if len(sys.argv) > 1 else "analyzed_opportunities.json"
    import_opportunities(json_file)
