"""
Seed script for Google Scraping Framework
Populates locations and keyword groups from the Keyword Matrix
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.database import SessionLocal
from app.models.google_scraping import LocationCatalog, KeywordGroup

def seed_locations(db):
    """Seed location catalog with major US cities and metros"""
    locations = [
        {"name": "San Francisco, CA", "location_type": "city", "latitude": 37.7749, "longitude": -122.4194, "radius_km": 10.0},
        {"name": "Austin, TX", "location_type": "city", "latitude": 30.2672, "longitude": -97.7431, "radius_km": 15.0},
        {"name": "New York City, NY", "location_type": "city", "latitude": 40.7128, "longitude": -74.0060, "radius_km": 10.0},
        {"name": "Los Angeles, CA", "location_type": "city", "latitude": 34.0522, "longitude": -118.2437, "radius_km": 20.0},
        {"name": "Chicago, IL", "location_type": "city", "latitude": 41.8781, "longitude": -87.6298, "radius_km": 15.0},
        {"name": "Seattle, WA", "location_type": "city", "latitude": 47.6062, "longitude": -122.3321, "radius_km": 12.0},
        {"name": "Denver, CO", "location_type": "city", "latitude": 39.7392, "longitude": -104.9903, "radius_km": 15.0},
        {"name": "Boston, MA", "location_type": "city", "latitude": 42.3601, "longitude": -71.0589, "radius_km": 10.0},
        {"name": "Miami, FL", "location_type": "city", "latitude": 25.7617, "longitude": -80.1918, "radius_km": 15.0},
        {"name": "Atlanta, GA", "location_type": "city", "latitude": 33.7490, "longitude": -84.3880, "radius_km": 15.0},
        {"name": "Portland, OR", "location_type": "city", "latitude": 45.5152, "longitude": -122.6784, "radius_km": 12.0},
        {"name": "Phoenix, AZ", "location_type": "city", "latitude": 33.4484, "longitude": -112.0740, "radius_km": 20.0},
        {"name": "San Diego, CA", "location_type": "city", "latitude": 32.7157, "longitude": -117.1611, "radius_km": 15.0},
        {"name": "Dallas, TX", "location_type": "city", "latitude": 32.7767, "longitude": -96.7970, "radius_km": 20.0},
        {"name": "Houston, TX", "location_type": "city", "latitude": 29.7604, "longitude": -95.3698, "radius_km": 25.0},
        {"name": "Bay Area, CA", "location_type": "metro", "latitude": 37.5585, "longitude": -122.2711, "radius_km": 50.0},
        {"name": "Silicon Valley, CA", "location_type": "metro", "latitude": 37.3875, "longitude": -122.0575, "radius_km": 30.0},
        {"name": "Brooklyn, NY", "location_type": "neighborhood", "latitude": 40.6782, "longitude": -73.9442, "radius_km": 8.0},
        {"name": "Manhattan, NY", "location_type": "neighborhood", "latitude": 40.7831, "longitude": -73.9712, "radius_km": 5.0},
        {"name": "The Mission, SF", "location_type": "neighborhood", "latitude": 37.7599, "longitude": -122.4148, "radius_km": 2.0},
    ]
    
    added = 0
    city_ids = {}
    
    for loc_data in locations:
        existing = db.query(LocationCatalog).filter(
            LocationCatalog.normalized_name == loc_data["name"].lower().strip()
        ).first()
        
        if not existing:
            location = LocationCatalog(
                name=loc_data["name"],
                normalized_name=loc_data["name"].lower().strip(),
                location_type=loc_data["location_type"],
                latitude=loc_data["latitude"],
                longitude=loc_data["longitude"],
                radius_km=loc_data["radius_km"],
                is_active=True
            )
            db.add(location)
            db.flush()
            city_ids[loc_data["name"]] = location.id
            added += 1
        else:
            city_ids[loc_data["name"]] = existing.id
    
    db.commit()
    print(f"Added {added} new locations")
    return city_ids


def seed_zip_codes(db, city_ids):
    """Seed zip codes for major cities for diversified coverage"""
    zip_codes_by_city = {
        "Austin, TX": [
            {"zip": "78701", "name": "Downtown Austin", "lat": 30.2672, "lng": -97.7431},
            {"zip": "78702", "name": "East Austin", "lat": 30.2621, "lng": -97.7189},
            {"zip": "78703", "name": "Tarrytown/Clarksville", "lat": 30.2969, "lng": -97.7700},
            {"zip": "78704", "name": "South Austin/Zilker", "lat": 30.2451, "lng": -97.7693},
            {"zip": "78705", "name": "UT Campus/Hyde Park", "lat": 30.2950, "lng": -97.7385},
            {"zip": "78731", "name": "Northwest Hills", "lat": 30.3569, "lng": -97.7619},
            {"zip": "78745", "name": "South Austin", "lat": 30.2090, "lng": -97.7990},
            {"zip": "78746", "name": "West Lake Hills", "lat": 30.2969, "lng": -97.8153},
            {"zip": "78757", "name": "North Austin/Crestview", "lat": 30.3569, "lng": -97.7337},
            {"zip": "78759", "name": "Arboretum/Great Hills", "lat": 30.4020, "lng": -97.7540},
        ],
        "San Francisco, CA": [
            {"zip": "94102", "name": "Tenderloin/Civic Center", "lat": 37.7813, "lng": -122.4167},
            {"zip": "94103", "name": "SoMa", "lat": 37.7726, "lng": -122.4099},
            {"zip": "94107", "name": "Potrero Hill/Dogpatch", "lat": 37.7621, "lng": -122.3971},
            {"zip": "94108", "name": "Chinatown/Nob Hill", "lat": 37.7929, "lng": -122.4076},
            {"zip": "94109", "name": "Russian Hill/Polk Gulch", "lat": 37.7929, "lng": -122.4213},
            {"zip": "94110", "name": "Mission District", "lat": 37.7486, "lng": -122.4154},
            {"zip": "94114", "name": "Castro/Noe Valley", "lat": 37.7579, "lng": -122.4341},
            {"zip": "94115", "name": "Pacific Heights/Japantown", "lat": 37.7869, "lng": -122.4375},
            {"zip": "94116", "name": "Sunset District", "lat": 37.7449, "lng": -122.4860},
            {"zip": "94117", "name": "Haight-Ashbury", "lat": 37.7708, "lng": -122.4428},
        ],
        "New York City, NY": [
            {"zip": "10001", "name": "Chelsea/Midtown South", "lat": 40.7484, "lng": -73.9967},
            {"zip": "10002", "name": "Lower East Side", "lat": 40.7157, "lng": -73.9863},
            {"zip": "10003", "name": "East Village/Greenwich", "lat": 40.7317, "lng": -73.9892},
            {"zip": "10010", "name": "Gramercy/Flatiron", "lat": 40.7390, "lng": -73.9826},
            {"zip": "10011", "name": "Chelsea/West Village", "lat": 40.7418, "lng": -74.0002},
            {"zip": "10013", "name": "Tribeca", "lat": 40.7195, "lng": -74.0089},
            {"zip": "10014", "name": "West Village", "lat": 40.7340, "lng": -74.0054},
            {"zip": "10016", "name": "Murray Hill", "lat": 40.7459, "lng": -73.9780},
            {"zip": "10019", "name": "Hell's Kitchen/Midtown West", "lat": 40.7654, "lng": -73.9879},
            {"zip": "10036", "name": "Times Square/Theater District", "lat": 40.7590, "lng": -73.9890},
        ],
        "Los Angeles, CA": [
            {"zip": "90012", "name": "Downtown LA/Chinatown", "lat": 34.0622, "lng": -118.2437},
            {"zip": "90013", "name": "Downtown LA/Arts District", "lat": 34.0453, "lng": -118.2378},
            {"zip": "90015", "name": "South Park/Staples Center", "lat": 34.0357, "lng": -118.2612},
            {"zip": "90028", "name": "Hollywood", "lat": 34.1016, "lng": -118.3267},
            {"zip": "90036", "name": "Miracle Mile/Park La Brea", "lat": 34.0697, "lng": -118.3476},
            {"zip": "90046", "name": "West Hollywood Hills", "lat": 34.1136, "lng": -118.3666},
            {"zip": "90048", "name": "Beverly Grove", "lat": 34.0741, "lng": -118.3744},
            {"zip": "90049", "name": "Brentwood", "lat": 34.0614, "lng": -118.4744},
            {"zip": "90067", "name": "Century City", "lat": 34.0575, "lng": -118.4172},
            {"zip": "90210", "name": "Beverly Hills", "lat": 34.0901, "lng": -118.4065},
        ],
        "Chicago, IL": [
            {"zip": "60601", "name": "The Loop", "lat": 41.8862, "lng": -87.6186},
            {"zip": "60602", "name": "Loop/Financial District", "lat": 41.8819, "lng": -87.6291},
            {"zip": "60605", "name": "South Loop/Museum Campus", "lat": 41.8545, "lng": -87.6180},
            {"zip": "60607", "name": "West Loop/Greektown", "lat": 41.8732, "lng": -87.6506},
            {"zip": "60610", "name": "Old Town/Gold Coast", "lat": 41.9069, "lng": -87.6389},
            {"zip": "60611", "name": "Streeterville/Magnificent Mile", "lat": 41.8929, "lng": -87.6174},
            {"zip": "60614", "name": "Lincoln Park", "lat": 41.9216, "lng": -87.6541},
            {"zip": "60618", "name": "North Center/Roscoe Village", "lat": 41.9469, "lng": -87.7025},
            {"zip": "60622", "name": "Wicker Park/Bucktown", "lat": 41.9013, "lng": -87.6777},
            {"zip": "60647", "name": "Logan Square", "lat": 41.9229, "lng": -87.7052},
        ],
        "Seattle, WA": [
            {"zip": "98101", "name": "Downtown Seattle", "lat": 47.6097, "lng": -122.3331},
            {"zip": "98102", "name": "Capitol Hill/Eastlake", "lat": 47.6322, "lng": -122.3209},
            {"zip": "98103", "name": "Fremont/Wallingford", "lat": 47.6711, "lng": -122.3425},
            {"zip": "98104", "name": "Pioneer Square/ID", "lat": 47.6016, "lng": -122.3307},
            {"zip": "98105", "name": "University District", "lat": 47.6614, "lng": -122.2976},
            {"zip": "98107", "name": "Ballard", "lat": 47.6705, "lng": -122.3778},
            {"zip": "98109", "name": "Queen Anne/South Lake Union", "lat": 47.6294, "lng": -122.3477},
            {"zip": "98112", "name": "Madison Park/Montlake", "lat": 47.6348, "lng": -122.2940},
            {"zip": "98115", "name": "Ravenna/Bryant", "lat": 47.6854, "lng": -122.2940},
            {"zip": "98122", "name": "Central District", "lat": 47.6061, "lng": -122.3060},
        ],
        "Denver, CO": [
            {"zip": "80202", "name": "Downtown Denver/LoDo", "lat": 39.7507, "lng": -105.0004},
            {"zip": "80203", "name": "Capitol Hill", "lat": 39.7288, "lng": -104.9802},
            {"zip": "80204", "name": "Lincoln Park/West Colfax", "lat": 39.7370, "lng": -105.0237},
            {"zip": "80205", "name": "Five Points/RiNo", "lat": 39.7622, "lng": -104.9669},
            {"zip": "80206", "name": "Cherry Creek/Country Club", "lat": 39.7186, "lng": -104.9533},
            {"zip": "80209", "name": "Washington Park", "lat": 39.6977, "lng": -104.9691},
            {"zip": "80210", "name": "University/Platt Park", "lat": 39.6786, "lng": -104.9651},
            {"zip": "80211", "name": "Highland/Sunnyside", "lat": 39.7622, "lng": -105.0137},
            {"zip": "80218", "name": "Uptown/City Park West", "lat": 39.7439, "lng": -104.9691},
            {"zip": "80220", "name": "Park Hill/Montclair", "lat": 39.7439, "lng": -104.9143},
        ],
        "Miami, FL": [
            {"zip": "33125", "name": "Little Havana", "lat": 25.7706, "lng": -80.2289},
            {"zip": "33127", "name": "Wynwood/Design District", "lat": 25.8057, "lng": -80.1989},
            {"zip": "33128", "name": "Downtown Miami", "lat": 25.7717, "lng": -80.1918},
            {"zip": "33129", "name": "Brickell", "lat": 25.7505, "lng": -80.2078},
            {"zip": "33130", "name": "Downtown/Overtown", "lat": 25.7706, "lng": -80.2078},
            {"zip": "33131", "name": "Brickell Key", "lat": 25.7617, "lng": -80.1889},
            {"zip": "33132", "name": "Edgewater/Arts District", "lat": 25.7856, "lng": -80.1889},
            {"zip": "33133", "name": "Coconut Grove", "lat": 25.7253, "lng": -80.2467},
            {"zip": "33137", "name": "Upper East Side", "lat": 25.8206, "lng": -80.1789},
            {"zip": "33139", "name": "South Beach", "lat": 25.7837, "lng": -80.1318},
        ],
        "Boston, MA": [
            {"zip": "02108", "name": "Beacon Hill", "lat": 42.3588, "lng": -71.0650},
            {"zip": "02109", "name": "North End/Waterfront", "lat": 42.3647, "lng": -71.0542},
            {"zip": "02110", "name": "Financial District", "lat": 42.3570, "lng": -71.0545},
            {"zip": "02111", "name": "Chinatown/Leather District", "lat": 42.3509, "lng": -71.0619},
            {"zip": "02114", "name": "West End/Beacon Hill", "lat": 42.3627, "lng": -71.0686},
            {"zip": "02115", "name": "Fenway/Back Bay", "lat": 42.3422, "lng": -71.0938},
            {"zip": "02116", "name": "Back Bay/South End", "lat": 42.3509, "lng": -71.0749},
            {"zip": "02118", "name": "South End", "lat": 42.3396, "lng": -71.0724},
            {"zip": "02127", "name": "South Boston", "lat": 42.3370, "lng": -71.0449},
            {"zip": "02129", "name": "Charlestown", "lat": 42.3779, "lng": -71.0618},
        ],
        "Atlanta, GA": [
            {"zip": "30303", "name": "Downtown Atlanta", "lat": 33.7537, "lng": -84.3886},
            {"zip": "30305", "name": "Buckhead", "lat": 33.8306, "lng": -84.3880},
            {"zip": "30306", "name": "Virginia Highland", "lat": 33.7829, "lng": -84.3549},
            {"zip": "30307", "name": "Little Five Points/Inman Park", "lat": 33.7615, "lng": -84.3488},
            {"zip": "30308", "name": "Midtown", "lat": 33.7733, "lng": -84.3793},
            {"zip": "30309", "name": "Midtown/Ansley Park", "lat": 33.7945, "lng": -84.3838},
            {"zip": "30312", "name": "Grant Park/Cabbagetown", "lat": 33.7397, "lng": -84.3702},
            {"zip": "30313", "name": "Castleberry Hill/West End", "lat": 33.7515, "lng": -84.4049},
            {"zip": "30316", "name": "East Atlanta/Ormewood", "lat": 33.7265, "lng": -84.3388},
            {"zip": "30318", "name": "West Midtown/Westside", "lat": 33.7905, "lng": -84.4219},
        ],
    }
    
    added = 0
    for city_name, zips in zip_codes_by_city.items():
        parent_id = city_ids.get(city_name)
        if not parent_id:
            print(f"Warning: Parent city not found for {city_name}")
            continue
            
        for zip_data in zips:
            normalized = f"{zip_data['zip']} - {zip_data['name']}".lower()
            existing = db.query(LocationCatalog).filter(
                LocationCatalog.normalized_name == normalized
            ).first()
            
            if not existing:
                location = LocationCatalog(
                    name=f"{zip_data['zip']} - {zip_data['name']}",
                    normalized_name=normalized,
                    location_type="zip_code",
                    latitude=zip_data["lat"],
                    longitude=zip_data["lng"],
                    radius_km=3.0,
                    parent_location_id=parent_id,
                    extra_data={"zip": zip_data["zip"], "neighborhood": zip_data["name"]},
                    is_active=True
                )
                db.add(location)
                added += 1
    
    db.commit()
    print(f"Added {added} new zip codes")


def seed_keyword_groups(db):
    """Seed keyword groups from the Keyword Matrix"""
    keyword_groups = [
        {
            "name": "Transportation & Parking",
            "category": "Transportation",
            "keywords": [
                "parking", "can't find parking", "parking is expensive", "no parking spots",
                "uber", "lyft", "rideshare", "taxi", "transit", "bus", "train", "commute",
                "traffic is terrible", "public transit", "BART", "subway", "metro"
            ],
            "description": "Parking, transit, and rideshare pain points"
        },
        {
            "name": "Food & Delivery",
            "category": "Food & Beverage",
            "keywords": [
                "restaurant", "food delivery", "delivery is slow", "dining", "takeout",
                "meal prep", "lunch options", "dinner", "coffee", "food is expensive",
                "restaurant wait times", "no good food options", "doordash", "ubereats"
            ],
            "description": "Food delivery, restaurants, and dining problems"
        },
        {
            "name": "Childcare & Education",
            "category": "Childcare",
            "keywords": [
                "daycare", "childcare", "can't find daycare", "childcare is expensive",
                "babysitter", "nanny", "preschool", "school", "tutor", "kids",
                "no available slots", "long waitlist", "after school care"
            ],
            "description": "Childcare, babysitting, and education needs"
        },
        {
            "name": "Healthcare Access",
            "category": "Healthcare",
            "keywords": [
                "doctor", "dentist", "can't get appointment", "medical", "health",
                "clinic", "doctor wait times", "insurance doesn't cover", "expensive copay",
                "pharmacy", "specialist", "urgent care", "telemedicine"
            ],
            "description": "Healthcare access and appointment problems"
        },
        {
            "name": "Home Services",
            "category": "Home Services",
            "keywords": [
                "plumber", "electrician", "handyman", "can't find reliable", "contractor",
                "repair", "cleaning", "renovation", "overcharged", "no show",
                "poor quality work", "HVAC", "roofer", "landscaping"
            ],
            "description": "Home repair and maintenance service issues"
        },
        {
            "name": "Real Estate & Housing",
            "category": "Real Estate",
            "keywords": [
                "apartment", "can't find apartment", "housing", "rent", "rent is too expensive",
                "lease", "landlord", "bad landlord", "property", "moving", "roommate",
                "hidden fees", "security deposit", "eviction"
            ],
            "description": "Housing, rentals, and landlord problems"
        },
        {
            "name": "Pet Services",
            "category": "Pet Services",
            "keywords": [
                "pet", "dog", "cat", "vet", "vet is expensive", "grooming",
                "can't find pet sitter", "pet sitting", "dog walking", "boarding",
                "no available boarding", "grooming wait time", "dog park"
            ],
            "description": "Pet care, veterinary, and grooming issues"
        },
        {
            "name": "Financial Services",
            "category": "Financial",
            "keywords": [
                "bank", "bank fees are high", "credit", "loan", "mortgage",
                "insurance", "can't get approved", "investment", "payment", "budget",
                "poor customer service", "hidden charges", "overdraft"
            ],
            "description": "Banking, credit, and financial service problems"
        },
        {
            "name": "Product Discovery",
            "category": "Product Marketplace",
            "keywords": [
                "where can I buy", "can't find anywhere", "out of stock",
                "who sells", "need to buy", "terrible quality", "broke after",
                "doesn't last", "always breaking", "shop", "retail"
            ],
            "description": "Product availability and quality issues"
        },
        {
            "name": "Service Discovery",
            "category": "Service Marketplace",
            "keywords": [
                "need a good", "looking for a good", "anyone know a good",
                "urgently need", "where to find", "reliable", "never showed up",
                "terrible service", "overcharged", "cancelled last minute"
            ],
            "description": "Finding reliable service providers"
        },
        {
            "name": "Explicit Demand Signals",
            "category": "Demand Signals",
            "keywords": [
                "I wish there was", "why doesn't anyone make", "can someone please build",
                "someone needs to build", "we need a", "why is there no",
                "why doesn't anyone offer", "doesn't exist"
            ],
            "description": "Goldmine signals - explicit unmet needs"
        },
        {
            "name": "Willingness to Pay",
            "category": "Demand Signals",
            "keywords": [
                "I'd pay for", "I would pay", "shut up and take my money",
                "worth paying for", "willing to pay", "take my money"
            ],
            "description": "Strong buying intent signals"
        },
        {
            "name": "Frustration Signals",
            "category": "Pain Points",
            "keywords": [
                "so frustrating", "I can't believe we still", "it's ridiculous",
                "every single time", "always have to", "never again",
                "worst ever", "completely useless", "terrible", "horrible"
            ],
            "description": "High emotional intensity pain points"
        },
        {
            "name": "Alternative Seeking",
            "category": "Market Gaps",
            "keywords": [
                "looking for a better", "alternatives to", "sick of",
                "gave up on", "there has to be a better way",
                "this shouldn't be this hard", "no good options"
            ],
            "description": "Incumbent weakness and competitive gaps"
        },
        {
            "name": "Community Questions",
            "category": "Validation",
            "keywords": [
                "does anyone else struggle", "am I the only one",
                "how do you deal with", "what do you use for",
                "anyone found a solution", "has anyone tried"
            ],
            "description": "Community-validated shared problems"
        }
    ]
    
    added = 0
    for group_data in keyword_groups:
        existing = db.query(KeywordGroup).filter(
            KeywordGroup.name == group_data["name"]
        ).first()
        
        if not existing:
            group = KeywordGroup(
                name=group_data["name"],
                category=group_data["category"],
                keywords=group_data["keywords"],
                description=group_data.get("description"),
                is_active=True
            )
            db.add(group)
            added += 1
        else:
            existing.keywords = group_data["keywords"]
            existing.category = group_data["category"]
            existing.description = group_data.get("description")
    
    db.commit()
    print(f"Added {added} new keyword groups, updated existing")


def main():
    print("Seeding Google Scraping data...")
    db = SessionLocal()
    try:
        city_ids = seed_locations(db)
        seed_zip_codes(db, city_ids)
        seed_keyword_groups(db)
        
        loc_count = db.query(LocationCatalog).filter(LocationCatalog.is_active == True).count()
        zip_count = db.query(LocationCatalog).filter(LocationCatalog.is_active == True, LocationCatalog.location_type == "zip_code").count()
        kw_count = db.query(KeywordGroup).filter(KeywordGroup.is_active == True).count()
        
        print(f"\nTotal active locations: {loc_count}")
        print(f"  - Zip codes: {zip_count}")
        print(f"Total active keyword groups: {kw_count}")
        print("\nSeeding complete!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
