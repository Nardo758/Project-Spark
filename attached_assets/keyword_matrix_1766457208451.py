# OppGrid Keyword Matrix
# Validates business locations and extracts business ideas from all data sources

"""
Two-dimensional validation matrix:
1. LOCATION VALIDATION - Extract and validate geographic signals
2. BUSINESS IDEA VALIDATION - Identify and score business opportunities

Each pattern includes:
- Pattern/keyword
- Confidence score (0.0 - 1.0)
- Context requirements
- Source-specific variations
"""

# ============================================================================
# LOCATION EXTRACTION MATRIX
# ============================================================================

LOCATION_KEYWORDS = {
    
    # EXPLICIT LOCATION INDICATORS (High Confidence: 0.9-1.0)
    "explicit_city_state": {
        "patterns": [
            r"\bin\s+(San Francisco|SF),?\s*CA\b",
            r"\bin\s+(New York|NYC),?\s*NY\b",
            r"\bin\s+Los Angeles,?\s*CA\b",
            r"\bin\s+Chicago,?\s*IL\b",
            r"\bin\s+Boston,?\s*MA\b",
            r"\bin\s+Seattle,?\s*WA\b",
            r"\bin\s+Denver,?\s*CO\b",
            r"\bin\s+Austin,?\s*TX\b",
            r"\bin\s+Portland,?\s*OR\b",
            r"\bin\s+Miami,?\s*FL\b",
        ],
        "confidence": 0.95,
        "extraction_method": "regex_capture",
        "examples": [
            "in San Francisco, CA",
            "parking in NYC",
            "living in Boston, MA"
        ]
    },
    
    "explicit_city_only": {
        "patterns": [
            r"\bin\s+(San Francisco|SF)\b",
            r"\bin\s+(New York|NYC|Manhattan|Brooklyn)\b",
            r"\bin\s+(Los Angeles|LA)\b",
            r"\bin\s+Chicago\b",
            r"\bin\s+Boston\b",
            r"\bin\s+the\s+(Bay Area|DMV|Tri-State)\b",
        ],
        "confidence": 0.85,
        "extraction_method": "regex_capture",
        "examples": [
            "in San Francisco",
            "parking in Chicago",
            "restaurants in Brooklyn"
        ]
    },
    
    "address_patterns": {
        "patterns": [
            r"\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)",
            r"\d+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave)",
        ],
        "confidence": 0.90,
        "extraction_method": "full_address_parse",
        "examples": [
            "123 Main Street",
            "456 Oak Avenue",
            "789 Market St"
        ]
    },
    
    "zip_code": {
        "patterns": [
            r"\b\d{5}(?:-\d{4})?\b",
        ],
        "confidence": 0.95,
        "extraction_method": "zip_lookup",
        "examples": [
            "94102",
            "10001",
            "90210-1234"
        ]
    },
    
    # NEIGHBORHOOD/AREA INDICATORS (Medium-High Confidence: 0.7-0.9)
    "neighborhood_mentions": {
        "patterns": [
            r"\bin\s+(the\s+)?(Mission|SOMA|Castro|Haight|Marina|Richmond|Sunset)\b",  # SF
            r"\bin\s+(the\s+)?(Upper East Side|UES|Williamsburg|Park Slope|Astoria)\b",  # NYC
            r"\bin\s+(the\s+)?(Hollywood|Beverly Hills|Santa Monica|Venice|Silverlake)\b",  # LA
            r"\bmy neighborhood\b",
            r"\bthis neighborhood\b",
            r"\bour area\b",
            r"\baround here\b",
        ],
        "confidence": 0.75,
        "extraction_method": "neighborhood_lookup",
        "examples": [
            "in the Mission",
            "my neighborhood",
            "around here in Williamsburg"
        ]
    },
    
    # CONTEXTUAL LOCATION (Medium Confidence: 0.6-0.75)
    "proximity_indicators": {
        "patterns": [
            r"\bnear\s+(me|my house|my apartment|downtown|the office)\b",
            r"\bclose to\s+",
            r"\bwalking distance\b",
            r"\bin my area\b",
            r"\blocally\b",
            r"\bin this city\b",
            r"\bhere in\b",
        ],
        "confidence": 0.65,
        "extraction_method": "context_dependent",
        "examples": [
            "near me",
            "walking distance from downtown",
            "locally here"
        ],
        "notes": "Requires additional context (subreddit, user location, etc.)"
    },
    
    # REGIONAL INDICATORS (Lower Confidence: 0.5-0.65)
    "regional_terms": {
        "patterns": [
            r"\bBay Area\b",
            r"\bSilicon Valley\b",
            r"\bSouth Bay\b",
            r"\bEast Coast\b",
            r"\bWest Coast\b",
            r"\bPacific Northwest\b",
            r"\bNew England\b",
            r"\bthe South\b",
        ],
        "confidence": 0.60,
        "extraction_method": "region_to_cities",
        "examples": [
            "in the Bay Area",
            "on the East Coast",
            "Silicon Valley startups"
        ],
        "notes": "Expand to multiple cities within region"
    },
}

# SOURCE-SPECIFIC LOCATION EXTRACTION
SOURCE_LOCATION_STRATEGIES = {
    
    "reddit": {
        "primary_sources": [
            "subreddit_name",  # r/sanfrancisco → San Francisco, CA
            "explicit_mentions",  # "in NYC" in post text
            "user_flair",  # City-based flair
        ],
        "subreddit_mappings": {
            "sanfrancisco": {"city": "San Francisco", "state": "CA", "confidence": 0.95},
            "nyc": {"city": "New York", "state": "NY", "confidence": 0.95},
            "losangeles": {"city": "Los Angeles", "state": "CA", "confidence": 0.95},
            "chicago": {"city": "Chicago", "state": "IL", "confidence": 0.95},
            "boston": {"city": "Boston", "state": "MA", "confidence": 0.95},
            "seattle": {"city": "Seattle", "state": "WA", "confidence": 0.95},
            "denver": {"city": "Denver", "state": "CO", "confidence": 0.95},
            "austin": {"city": "Austin", "state": "TX", "confidence": 0.95},
        },
        "fallback": "explicit_mentions",
        "confidence_boost": 0.1,  # If multiple signals agree
    },
    
    "google_reviews": {
        "primary_sources": [
            "business_address",  # Structured address field
            "place_location",  # Lat/lng from API
        ],
        "parsing": "structured_data",
        "confidence": 1.0,  # API provides verified data
    },
    
    "google_maps": {
        "primary_sources": [
            "business_address",
            "scraped_location_text",
        ],
        "parsing": "address_parser",
        "confidence": 0.95,
    },
    
    "yelp": {
        "primary_sources": [
            "business_location_object",  # API provides structured location
        ],
        "parsing": "structured_data",
        "confidence": 1.0,
    },
    
    "twitter": {
        "primary_sources": [
            "geo_place_id",  # If tweet has location enabled
            "explicit_mentions",  # "in SF" in tweet text
            "hashtags",  # #SanFrancisco
        ],
        "parsing": "multi_source",
        "confidence": 0.80,  # Twitter geo can be imprecise
    },
    
    "nextdoor": {
        "primary_sources": [
            "neighborhood_id",  # API provides exact neighborhood
            "neighborhood_polygon",  # Geographic boundary
        ],
        "parsing": "structured_data",
        "confidence": 1.0,  # Most precise location data
    },
    
    "greatschools": {
        "primary_sources": [
            "school_address",  # API provides school location
            "school_district",
        ],
        "parsing": "structured_data",
        "confidence": 1.0,
    },
    
    "google_search": {
        "primary_sources": [
            "search_query",  # "parking San Francisco" 
            "snippet_mentions",  # Location in result text
            "source_domain",  # SF.gov → San Francisco
        ],
        "parsing": "query_extraction + text_analysis",
        "confidence": 0.70,
    },
    
    "craigslist": {
        "primary_sources": [
            "city_domain",  # sfbay.craigslist.org → San Francisco, CA
            "location_field",  # Location in post metadata
            "post_text",  # Location mentions in post body
        ],
        "city_mappings": {
            "sfbay": {"city": "San Francisco", "state": "CA", "confidence": 0.95},
            "newyork": {"city": "New York", "state": "NY", "confidence": 0.95},
            "losangeles": {"city": "Los Angeles", "state": "CA", "confidence": 0.95},
            "chicago": {"city": "Chicago", "state": "IL", "confidence": 0.95},
            "boston": {"city": "Boston", "state": "MA", "confidence": 0.95},
            "seattle": {"city": "Seattle", "state": "WA", "confidence": 0.95},
            "denver": {"city": "Denver", "state": "CO", "confidence": 0.95},
            "austin": {"city": "Austin", "state": "TX", "confidence": 0.95},
            "portland": {"city": "Portland", "state": "OR", "confidence": 0.95},
            "miami": {"city": "Miami", "state": "FL", "confidence": 0.95},
        },
        "parsing": "domain_mapping + text_extraction",
        "confidence": 0.95,
    },
}

# ============================================================================
# BUSINESS IDEA EXTRACTION MATRIX
# ============================================================================

BUSINESS_IDEA_KEYWORDS = {
    
    # TIER 1: EXPLICIT DEMAND SIGNALS (Confidence: 0.90-1.0)
    # Clear statements of wanting something that doesn't exist
    
    "explicit_demand": {
        "patterns": [
            r"i wish there was",
            r"i wish someone would",
            r"i wish [a-z]+ had",
            r"why doesn't anyone make",
            r"why isn't there",
            r"why don't we have",
            r"can someone please build",
            r"someone needs to build",
            r"someone should make",
            r"there should be",
            r"we need a",
            r"where can i find",
        ],
        "confidence": 1.0,
        "category": "explicit_demand",
        "validation_level": "goldmine",  # Layer 4
        "examples": [
            "I wish there was an app that...",
            "Why doesn't anyone make a service for...",
            "Someone needs to build a platform that..."
        ],
        "business_extraction": "extract_noun_phrase_after_pattern"
    },
    
    "willingness_to_pay": {
        "patterns": [
            r"i'd pay for",
            r"i would pay for",
            r"i'd gladly pay",
            r"willing to pay",
            r"shut up and take my money",
            r"take my money",
            r"worth paying for",
            r"would subscribe to",
            r"i'd buy",
        ],
        "confidence": 0.95,
        "category": "monetization_validation",
        "validation_level": "goldmine",  # Layer 4
        "examples": [
            "I'd pay for a service that...",
            "I'd gladly pay $50/month for...",
            "Shut up and take my money if someone builds..."
        ],
        "business_extraction": "extract_service_description"
    },
    
    # TIER 2: STRONG FRUSTRATION (Confidence: 0.80-0.90)
    # Emotional intensity indicating significant problem
    
    "frustration_signals": {
        "patterns": [
            r"so frustrating that",
            r"incredibly frustrating",
            r"i can't believe we still",
            r"it's ridiculous that",
            r"it's insane that",
            r"absurd that",
            r"unacceptable that",
            r"why do we still have to",
            r"every single time",
            r"literally every time",
            r"always have to",
            r"constantly have to",
        ],
        "confidence": 0.85,
        "category": "pain_point",
        "validation_level": "validated",  # Layer 3
        "examples": [
            "So frustrating that there's no easy way to...",
            "I can't believe we still have to manually...",
            "Every single time I need to..."
        ],
        "business_extraction": "extract_problem_statement"
    },
    
    "intensity_markers": {
        "patterns": [
            r"!!!+",  # Multiple exclamation marks
            r"never again",
            r"worst [a-z]+ ever",
            r"terrible [a-z]+",
            r"horrible [a-z]+",
            r"awful [a-z]+",
            r"hate [a-z]+ so much",
            r"completely useless",
            r"total waste",
            r"absolutely awful",
        ],
        "confidence": 0.80,
        "category": "high_intensity_pain",
        "validation_level": "validated",  # Layer 3
        "examples": [
            "Worst customer service ever!!!",
            "Never again will I...",
            "Absolutely awful experience with..."
        ],
        "business_extraction": "extract_criticized_entity"
    },
    
    # TIER 3: COMMUNITY VALIDATION (Confidence: 0.70-0.80)
    # Questions indicating widespread problem
    
    "community_validation": {
        "patterns": [
            r"does anyone else struggle",
            r"does anyone else have trouble",
            r"does anyone know of",
            r"am i the only one who",
            r"anyone else find it [a-z]+ that",
            r"how do you deal with",
            r"how do you handle",
            r"what do you use for",
            r"anyone found a solution",
            r"has anyone figured out",
            r"any recommendations for",
        ],
        "confidence": 0.75,
        "category": "community_problem",
        "validation_level": "validated",  # Layer 3
        "examples": [
            "Does anyone else struggle with...",
            "How do you deal with...",
            "Anyone found a solution for..."
        ],
        "business_extraction": "extract_problem_from_question"
    },
    
    "alternative_seeking": {
        "patterns": [
            r"looking for a better",
            r"looking for an alternative",
            r"alternatives to [a-z]+",
            r"better than [a-z]+",
            r"sick of [a-z]+",
            r"fed up with [a-z]+",
            r"done with [a-z]+",
            r"gave up on [a-z]+",
            r"switching from [a-z]+",
        ],
        "confidence": 0.75,
        "category": "competitive_gap",
        "validation_level": "validated",  # Layer 3
        "examples": [
            "Looking for a better alternative to...",
            "Sick of using...",
            "Gave up on... need something better"
        ],
        "business_extraction": "extract_incumbent_and_gap"
    },
    
    # TIER 4: PROBLEM EXISTENCE (Confidence: 0.60-0.70)
    # General problem indicators needing context
    
    "problem_indicators": {
        "patterns": [
            r"there has to be a better way",
            r"this shouldn't be this hard",
            r"why is this so [a-z]+",
            r"no good options for",
            r"no easy way to",
            r"difficult to find",
            r"hard to find",
            r"impossible to",
            r"waste of time",
            r"waste of money",
            r"takes forever to",
            r"such a hassle",
        ],
        "confidence": 0.65,
        "category": "friction_point",
        "validation_level": "weak_signal",  # Layer 2
        "examples": [
            "There has to be a better way to...",
            "No good options for...",
            "Such a hassle to..."
        ],
        "business_extraction": "extract_process_with_context"
    },
    
    # CRAIGSLIST-SPECIFIC PATTERNS
    "craigslist_wanted": {
        "patterns": [
            r"\bwanted\b",
            r"\bneed\b",
            r"\blooking for\b",
            r"\bseeking\b",
            r"\bin search of\b",
            r"\bmust have\b",
            r"\bdesperately need\b",
            r"\burgent\b",
            r"\basap\b",
            r"\biso\b",  # "in search of"
        ],
        "confidence": 0.85,
        "category": "explicit_need",
        "validation_level": "validated",  # Layer 3
        "examples": [
            "Wanted: parking near BART",
            "Need a place ASAP",
            "Looking for roommate urgently"
        ],
        "business_extraction": "extract_needed_item",
        "notes": "Craigslist 'wanted' ads explicitly state unmet needs"
    },
    
    "craigslist_price_mention": {
        "patterns": [
            r"willing to pay",
            r"can pay",
            r"budget of",
            r"up to \$\d+",
            r"paying \$\d+",
            r"\$\d+/month",
            r"\$\d+/week",
        ],
        "confidence": 0.95,
        "category": "monetization_validation",
        "validation_level": "goldmine",  # Layer 4
        "examples": [
            "Willing to pay $2000/month",
            "Budget of $500",
            "Can pay up to $1500"
        ],
        "business_extraction": "extract_price_and_need"
    },
    
    # PRODUCT DEMAND PATTERNS
    "product_demand": {
        "patterns": [
            r"where can i buy",
            r"where can i find",
            r"where to buy",
            r"where to get",
            r"anyone selling",
            r"does anyone sell",
            r"who sells",
            r"where to purchase",
            r"can't find [a-z]+ anywhere",
            r"nowhere sells",
            r"out of stock everywhere",
            r"need to buy",
            r"looking to buy",
            r"want to buy",
            r"trying to find",
        ],
        "confidence": 0.90,
        "category": "product_demand",
        "validation_level": "goldmine",  # Layer 4
        "examples": [
            "Where can I buy [product] in SF?",
            "Can't find [product] anywhere",
            "Does anyone sell [product]?",
            "Out of stock everywhere"
        ],
        "business_extraction": "extract_product_name",
        "notes": "Direct product purchase intent - indicates supply gap"
    },
    
    "product_recommendations": {
        "patterns": [
            r"what's the best [a-z]+ for",
            r"best [a-z]+ in",
            r"recommend a [a-z]+",
            r"recommendations for [a-z]+",
            r"which [a-z]+ should i",
            r"good [a-z]+ for",
            r"better than [a-z]+ product",
            r"alternative to [a-z]+ product",
            r"replacement for [a-z]+",
        ],
        "confidence": 0.80,
        "category": "product_discovery",
        "validation_level": "validated",  # Layer 3
        "examples": [
            "What's the best laptop for programming?",
            "Recommend a good coffee maker",
            "Alternative to expensive gym equipment"
        ],
        "business_extraction": "extract_product_category"
    },
    
    "product_quality_issues": {
        "patterns": [
            r"[a-z]+ broke after",
            r"[a-z]+ stopped working",
            r"terrible quality",
            r"cheap [a-z]+ that breaks",
            r"poorly made",
            r"falls apart",
            r"doesn't last",
            r"constant problems with",
            r"always breaking",
        ],
        "confidence": 0.85,
        "category": "product_quality_gap",
        "validation_level": "validated",  # Layer 3
        "examples": [
            "My blender broke after 2 months",
            "Terrible quality - falls apart",
            "Phone constantly has problems"
        ],
        "business_extraction": "extract_failed_product"
    },
    
    # SERVICE DEMAND PATTERNS
    "service_demand": {
        "patterns": [
            r"need a [a-z]+ (who|that|to)",
            r"looking for a (good|reliable|affordable) [a-z]+",
            r"anyone know a good [a-z]+",
            r"recommend a [a-z]+",
            r"can anyone recommend",
            r"where to find a [a-z]+",
            r"how to find a good",
            r"searching for a [a-z]+",
            r"in need of a [a-z]+",
            r"urgently need a [a-z]+",
        ],
        "confidence": 0.90,
        "category": "service_demand",
        "validation_level": "goldmine",  # Layer 4
        "examples": [
            "Need a plumber who can come today",
            "Looking for a good accountant",
            "Anyone know a good dentist?",
            "Where to find a reliable contractor?"
        ],
        "business_extraction": "extract_service_type",
        "notes": "Active service provider search - high conversion intent"
    },
    
    "service_recommendations": {
        "patterns": [
            r"best [a-z]+ in (the )?[A-Z]",
            r"who do you use for [a-z]+",
            r"what [a-z]+ do you recommend",
            r"any recommendations for [a-z]+",
            r"good [a-z]+ near me",
            r"reliable [a-z]+ in",
        ],
        "confidence": 0.85,
        "category": "service_discovery",
        "validation_level": "validated",  # Layer 3
        "examples": [
            "Best plumber in SF?",
            "Who do you use for taxes?",
            "Good mechanic near me?"
        ],
        "business_extraction": "extract_service_type_and_location"
    },
    
    "service_quality_issues": {
        "patterns": [
            r"terrible [a-z]+ service",
            r"worst [a-z]+ ever",
            r"never showed up",
            r"cancelled last minute",
            r"poor customer service",
            r"rude [a-z]+",
            r"overcharged (by|me)",
            r"took my money",
            r"did terrible job",
            r"had to hire someone else",
            r"unprofessional [a-z]+",
        ],
        "confidence": 0.85,
        "category": "service_quality_gap",
        "validation_level": "validated",  # Layer 3
        "examples": [
            "Plumber never showed up",
            "Terrible customer service",
            "Overcharged me $500",
            "Had to hire someone else to fix it"
        ],
        "business_extraction": "extract_failed_service_provider"
    },
    
    "marketplace_gaps": {
        "patterns": [
            r"why is there no",
            r"why doesn't anyone offer",
            r"no one provides",
            r"can't find (a |any )[a-z]+ that",
            r"impossible to find",
            r"doesn't exist",
            r"nobody does this",
            r"wish [a-z]+ existed",
        ],
        "confidence": 0.95,
        "category": "marketplace_gap",
        "validation_level": "goldmine",  # Layer 4
        "examples": [
            "Why is there no delivery service for...",
            "Can't find any plumber that does same-day",
            "Why doesn't anyone offer weekend appointments?"
        ],
        "business_extraction": "extract_missing_service_feature"
    },
}

# ============================================================================
# BUSINESS CATEGORY CLASSIFICATION
# ============================================================================

BUSINESS_CATEGORIES = {
    
    "transportation": {
        "keywords": [
            "parking", "uber", "lyft", "taxi", "rideshare", "car", "vehicle",
            "transit", "bus", "train", "subway", "commute", "traffic",
            "bike", "scooter", "motorcycle", "driving", "garage"
        ],
        "signals": [
            "can't find parking",
            "parking is expensive",
            "no parking spots",
            "traffic is terrible",
            "commute takes forever"
        ],
        "opportunity_types": [
            "parking_solutions",
            "ride_sharing",
            "last_mile_transit",
            "traffic_optimization",
            "vehicle_sharing"
        ]
    },
    
    "food_beverage": {
        "keywords": [
            "restaurant", "food", "delivery", "dining", "eat", "meal", "lunch",
            "dinner", "breakfast", "coffee", "cafe", "bar", "takeout",
            "pickup", "menu", "chef", "kitchen", "catering"
        ],
        "signals": [
            "food delivery is slow",
            "restaurant wait times",
            "no good options for",
            "food is expensive",
            "limited menu"
        ],
        "opportunity_types": [
            "food_delivery",
            "meal_prep",
            "restaurant_tech",
            "dietary_specific",
            "ghost_kitchen"
        ]
    },
    
    "childcare_education": {
        "keywords": [
            "daycare", "childcare", "babysitter", "nanny", "preschool", "school",
            "tutor", "education", "kids", "children", "toddler", "infant",
            "after school", "summer camp", "teacher", "learning"
        ],
        "signals": [
            "can't find daycare",
            "childcare is expensive",
            "no available slots",
            "long waitlist",
            "need babysitter"
        ],
        "opportunity_types": [
            "childcare_platform",
            "tutoring_service",
            "babysitter_matching",
            "edu_tech",
            "parent_resources"
        ]
    },
    
    "healthcare": {
        "keywords": [
            "doctor", "dentist", "medical", "health", "clinic", "hospital",
            "appointment", "insurance", "prescription", "pharmacy", "urgent care",
            "specialist", "therapy", "mental health", "wellness"
        ],
        "signals": [
            "can't get appointment",
            "doctor wait times",
            "insurance doesn't cover",
            "expensive copay",
            "no available doctors"
        ],
        "opportunity_types": [
            "telemedicine",
            "appointment_booking",
            "price_transparency",
            "insurance_navigation",
            "specialty_care"
        ]
    },
    
    "home_services": {
        "keywords": [
            "plumber", "electrician", "handyman", "repair", "maintenance",
            "cleaning", "maid", "contractor", "renovation", "remodel",
            "pest control", "lawn", "hvac", "roofing", "painting"
        ],
        "signals": [
            "can't find reliable",
            "overcharged by",
            "no show",
            "poor quality work",
            "expensive estimate"
        ],
        "opportunity_types": [
            "home_service_platform",
            "contractor_matching",
            "price_comparison",
            "quality_verification",
            "emergency_services"
        ]
    },
    
    "fitness_wellness": {
        "keywords": [
            "gym", "fitness", "workout", "exercise", "yoga", "pilates",
            "personal trainer", "nutrition", "diet", "weight loss",
            "running", "cycling", "swimming", "sports"
        ],
        "signals": [
            "gym is too expensive",
            "crowded gym",
            "inconvenient hours",
            "need workout partner",
            "can't find trainer"
        ],
        "opportunity_types": [
            "fitness_app",
            "personal_training",
            "gym_alternative",
            "nutrition_planning",
            "workout_community"
        ]
    },
    
    "real_estate": {
        "keywords": [
            "apartment", "housing", "rent", "lease", "landlord", "property",
            "real estate", "moving", "storage", "roommate", "tenant",
            "house hunting", "mortgage", "broker"
        ],
        "signals": [
            "can't find apartment",
            "rent is too expensive",
            "bad landlord",
            "hidden fees",
            "rental scam"
        ],
        "opportunity_types": [
            "rental_platform",
            "roommate_matching",
            "moving_services",
            "tenant_rights",
            "price_transparency"
        ]
    },
    
    "pet_services": {
        "keywords": [
            "pet", "dog", "cat", "vet", "veterinary", "grooming",
            "pet sitting", "dog walking", "boarding", "pet food",
            "pet supplies", "animal hospital"
        ],
        "signals": [
            "can't find pet sitter",
            "vet is expensive",
            "no available boarding",
            "grooming wait time",
            "pet emergency"
        ],
        "opportunity_types": [
            "pet_care_platform",
            "dog_walking_service",
            "vet_booking",
            "pet_insurance",
            "emergency_pet_care"
        ]
    },
    
    "financial_services": {
        "keywords": [
            "bank", "banking", "credit", "loan", "mortgage", "insurance",
            "investment", "financial", "money", "payment", "bill", "budget",
            "savings", "debt", "taxes", "accountant"
        ],
        "signals": [
            "bank fees are high",
            "poor customer service",
            "can't get approved",
            "confusing terms",
            "hidden charges"
        ],
        "opportunity_types": [
            "fintech_solution",
            "fee_transparency",
            "budget_tool",
            "loan_marketplace",
            "insurance_comparison"
        ]
    },
    
    "professional_services": {
        "keywords": [
            "lawyer", "attorney", "legal", "consultant", "accountant",
            "notary", "resume", "career", "job", "hiring", "freelance",
            "contract", "business", "startup"
        ],
        "signals": [
            "lawyers are expensive",
            "can't find affordable",
            "need help with",
            "don't understand legal",
            "hiring is difficult"
        ],
        "opportunity_types": [
            "legal_tech",
            "freelance_platform",
            "career_services",
            "consultant_matching",
            "document_automation"
        ]
    },
    
    "product_marketplace": {
        "keywords": [
            "buy", "purchase", "product", "item", "goods", "merchandise",
            "shopping", "store", "shop", "retail", "sell", "selling",
            "inventory", "stock", "supply", "vendor", "brand", "equipment"
        ],
        "signals": [
            "can't find anywhere",
            "out of stock",
            "no one sells",
            "where to buy",
            "terrible quality",
            "breaks after",
            "doesn't last"
        ],
        "opportunity_types": [
            "niche_ecommerce",
            "specialty_retailer",
            "quality_alternative",
            "marketplace_platform",
            "direct_to_consumer",
            "rental_marketplace"
        ]
    },
    
    "service_marketplace": {
        "keywords": [
            "service", "provider", "professional", "expert", "specialist",
            "contractor", "freelancer", "consultant", "technician", "worker",
            "help", "assistance", "support", "booking", "appointment",
            "schedule", "hire", "hiring"
        ],
        "signals": [
            "can't find reliable",
            "need a good",
            "looking for professional",
            "where to find",
            "recommendations for",
            "never showed up",
            "terrible service",
            "overcharged"
        ],
        "opportunity_types": [
            "service_marketplace",
            "booking_platform",
            "quality_verification",
            "price_transparency",
            "professional_network",
            "on_demand_service"
        ]
    },
    
    "local_services": {
        "keywords": [
            "near me", "nearby", "local", "neighborhood", "area",
            "close", "walking distance", "delivery", "pickup",
            "same day", "emergency", "24/7", "available", "open"
        ],
        "signals": [
            "nothing nearby",
            "no delivery options",
            "too far away",
            "doesn't deliver here",
            "closed when I need",
            "no emergency service"
        ],
        "opportunity_types": [
            "hyperlocal_marketplace",
            "delivery_service",
            "emergency_service",
            "24_7_availability",
            "neighborhood_platform"
        ]
    },
    
    "specialty_products": {
        "keywords": [
            "organic", "vegan", "gluten free", "specialty", "niche",
            "custom", "personalized", "handmade", "artisan", "craft",
            "eco friendly", "sustainable", "ethical", "fair trade",
            "small batch", "local made"
        ],
        "signals": [
            "hard to find",
            "limited options",
            "only available online",
            "expensive shipping",
            "not available locally",
            "poor selection"
        ],
        "opportunity_types": [
            "specialty_retailer",
            "niche_marketplace",
            "subscription_box",
            "direct_from_maker",
            "local_distribution"
        ]
    },
}

# ============================================================================
# VALIDATION SCORING MATRIX
# ============================================================================

VALIDATION_CRITERIA = {
    
    # Layer 4: Goldmine (Score: 0.85-1.0)
    "goldmine_signals": [
        "explicit_demand",
        "willingness_to_pay",
        "multiple_signals_combined",
        "quantified_pain_point",  # Includes $, time, or percentage
        "community_engagement_high",  # >50 upvotes or comments
    ],
    
    # Layer 3: Validated (Score: 0.70-0.84)
    "validated_signals": [
        "frustration_signals",
        "intensity_markers",
        "community_validation",
        "alternative_seeking",
        "repeated_mentions",  # Same problem in multiple posts
    ],
    
    # Layer 2: Weak Signal (Score: 0.50-0.69)
    "weak_signals": [
        "problem_indicators",
        "single_mention",
        "no_engagement",
        "ambiguous_context",
    ],
    
    # Layer 1: Noise (Score: 0.00-0.49)
    "noise": [
        "generic_complaint",
        "no_actionable_insight",
        "off_topic",
        "spam",
    ],
}

# ============================================================================
# QUANTIFICATION BOOSTERS
# ============================================================================

QUANTIFICATION_PATTERNS = {
    "money": {
        "patterns": [
            r"\$\d+(?:,\d{3})*(?:\.\d{2})?",
            r"\d+\s*dollars?",
            r"\d+k",  # $5k
        ],
        "boost": 0.10,
        "examples": ["$50", "$1,000", "500 dollars", "$5k"]
    },
    
    "time": {
        "patterns": [
            r"\d+\s*hours?",
            r"\d+\s*minutes?",
            r"\d+\s*days?",
            r"\d+\s*weeks?",
            r"\d+\s*months?",
        ],
        "boost": 0.10,
        "examples": ["2 hours", "30 minutes", "3 weeks"]
    },
    
    "frequency": {
        "patterns": [
            r"every single time",
            r"every day",
            r"daily",
            r"weekly",
            r"constantly",
            r"always",
        ],
        "boost": 0.10,
        "examples": ["every single time", "daily struggle", "always happens"]
    },
    
    "scale": {
        "patterns": [
            r"\d+%",
            r"\d+ times",
            r"most people",
            r"everyone",
            r"all of us",
        ],
        "boost": 0.05,
        "examples": ["50% of the time", "3 times a week", "everyone struggles"]
    },
}

# ============================================================================
# SOURCE-SPECIFIC KEYWORD WEIGHTS
# ============================================================================

SOURCE_WEIGHTS = {
    "reddit": {
        "r/SomebodyMakeThis": 1.0,  # Explicit product requests
        "r/mildlyinfuriating": 0.90,  # High frustration signals
        "r/CrappyDesign": 0.85,  # Design problems
        "r/DoesAnybodyElse": 0.85,  # Community validation
        "r/Entrepreneur": 0.80,  # Business-focused
        "r/SideProject": 0.80,  # Execution-focused
        "city_subreddits": 0.75,  # Local problems
        "industry_subreddits": 0.70,  # Specific domains
    },
    
    "google_reviews": {
        "rating_1_star": 1.0,  # Strongest negative signal
        "rating_2_star": 0.85,
        "rating_3_star": 0.65,
        "rating_4_star": 0.30,  # Usually not problems
        "rating_5_star": 0.10,  # Rarely has actionable problems
    },
    
    "yelp": {
        "rating_1_star": 1.0,
        "rating_2_star": 0.85,
        "rating_3_star": 0.65,
        "useful_count_high": 0.10,  # Boost if review is marked useful
    },
    
    "twitter": {
        "engagement_high": 0.10,  # >50 likes/retweets
        "engagement_medium": 0.05,  # 10-50 likes/retweets
        "verified_user": 0.05,  # Verified accounts
        "has_location": 0.10,  # Geo-tagged tweets
    },
    
    "nextdoor": {
        "base_confidence": 1.0,  # Already hyper-local
        "category_general": 0.80,
        "category_crime_safety": 0.90,
        "category_recommendations": 0.85,
    },
    
    "greatschools": {
        "rating_low": 1.0,  # Low school ratings
        "parent_review": 0.95,  # Parent perspectives
        "teacher_review": 0.90,  # Insider knowledge
    },
    
    "craigslist": {
        "wanted_ads": 1.0,  # Explicit unmet needs
        "services_wanted": 0.95,  # Service gaps
        "housing_wanted": 0.95,  # Housing gaps
        "price_mentioned": 0.10,  # Boost if budget stated
        "urgent_asap": 0.10,  # Boost for urgent needs
    },
}

# ============================================================================
# COMPOSITE SCORING ALGORITHM
# ============================================================================

def calculate_composite_score(signals: dict) -> dict:
    """
    Calculate final opportunity score based on multiple factors
    
    Args:
        signals: Dict containing detected patterns, location, category, etc.
    
    Returns:
        Dict with final_score, confidence_tier, and reasoning
    """
    
    # Base score from highest pattern match
    base_score = signals.get('highest_pattern_score', 0.0)
    
    # Location validation boost
    location_confidence = signals.get('location_confidence', 0.0)
    if location_confidence >= 0.90:
        base_score += 0.05
    elif location_confidence >= 0.75:
        base_score += 0.03
    
    # Category identification boost
    if signals.get('category_identified'):
        base_score += 0.03
    
    # Quantification boost
    if signals.get('has_money_mention'):
        base_score += 0.10
    if signals.get('has_time_mention'):
        base_score += 0.10
    if signals.get('has_frequency_mention'):
        base_score += 0.10
    
    # Multiple signal types boost
    signal_types = len(signals.get('signal_types', []))
    if signal_types >= 3:
        base_score += 0.10
    elif signal_types == 2:
        base_score += 0.05
    
    # Source-specific weight
    source_weight = SOURCE_WEIGHTS.get(signals['source'], {}).get('base', 1.0)
    base_score *= source_weight
    
    # Engagement boost (social proof)
    engagement = signals.get('engagement_score', 0.0)
    if engagement >= 0.90:
        base_score += 0.10
    elif engagement >= 0.70:
        base_score += 0.05
    
    # Cap at 1.0
    final_score = min(base_score, 1.0)
    
    # Determine confidence tier
    if final_score >= 0.85:
        tier = "GOLDMINE"  # Layer 4
        action = "IMMEDIATE_REVIEW"
    elif final_score >= 0.70:
        tier = "VALIDATED"  # Layer 3
        action = "PRIORITIZE"
    elif final_score >= 0.50:
        tier = "WEAK_SIGNAL"  # Layer 2
        action = "MONITOR"
    else:
        tier = "NOISE"  # Layer 1
        action = "FILTER_OUT"
    
    return {
        'final_score': round(final_score, 2),
        'confidence_tier': tier,
        'recommended_action': action,
        'score_breakdown': {
            'base_score': base_score,
            'location_boost': location_confidence,
            'quantification_boosts': signals.get('quantification_count', 0),
            'multi_signal_boost': signal_types,
            'engagement_boost': engagement,
        }
    }

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    # Example 1: Reddit post with explicit demand
    example_1 = {
        'text': "I wish there was an app in San Francisco that helps me find parking near restaurants. I'd pay $20/month for this!",
        'source': 'reddit',
        'subreddit': 'r/sanfrancisco',
        'upvotes': 120,
        'comments': 45
    }
    
    # This would score:
    # - "I wish there was" → 1.0
    # - "in San Francisco" → 0.95 location confidence
    # - "$20/month" → +0.10 quantification
    # - Category: transportation (parking)
    # - High engagement → +0.10
    # Final score: ~1.0 (GOLDMINE)
    
    # Example 2: Yelp review with frustration
    example_2 = {
        'text': "So frustrating that they never answer the phone. Every single time I call, it goes to voicemail. Waste of time.",
        'source': 'yelp',
        'rating': 1,
        'business_name': 'ABC Dental',
        'location': 'San Francisco, CA',
        'useful_count': 15
    }
    
    # This would score:
    # - "So frustrating that" → 0.85
    # - "Every single time" → +0.10 frequency
    # - "Waste of time" → 0.65
    # - 1-star rating → 1.0 source weight
    # - Category: healthcare
    # - Location: verified (1.0)
    # Final score: ~0.90 (GOLDMINE/VALIDATED)
    
    # Example 3: Twitter with weak signal
    example_3 = {
        'text': "parking here sucks",
        'source': 'twitter',
        'likes': 2,
        'retweets': 0,
        'has_location': False
    }
    
    # This would score:
    # - Generic complaint → 0.40
    # - No location → 0.0 location confidence
    # - No engagement → 0.0
    # - Category: transportation
    # Final score: ~0.40 (NOISE)
    
    print("Keyword Matrix loaded successfully!")
    print("Ready to validate locations and extract business ideas")
