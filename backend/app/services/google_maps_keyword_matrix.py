# OppGrid - Google Maps Industry-Specific Keyword Matrix
# Calibrated for how people actually write reviews on Google Maps

"""
Key differences from Reddit/Social Media patterns:
1. More indirect language ("would be nice if" vs "I wish there was")
2. Star ratings carry signal weight
3. Specific entity mentions (staff names, competitors)
4. Policy/procedure complaints vs general frustration
5. Comparison language ("used to be", "new policy")
"""

# ============================================================================
# APARTMENT/HOUSING KEYWORD PATTERNS
# ============================================================================

APARTMENT_PATTERNS = {
    
    # TIER 1: Policy/Fee Complaints (Very high signal)
    "new_policy_complaints": {
        "patterns": [
            r"new\s+(policy|rule|charge|fee)",
            r"now\s+(charge|charging|cost|require)",
            r"used to be\s+(free|included|better)",
            r"changed\s+to\s+\$\d+",
            r"pay\s+\$\d+\s+(for|every|per)",
            r"disappointed\s+with\s+(new|the new)",
            r"unfortunate\s+(change|policy|new)",
        ],
        "confidence": 0.90,
        "category": "policy_friction",
        "signal_type": "monetization_gap",
        "examples": [
            "new guest parking policy - now $5 every time",
            "used to allow 15 guest parking days per month",
            "disappointed with the new guest parking policy"
        ],
        "opportunity_extraction": "fee_elimination_service"
    },
    
    "hidden_fees": {
        "patterns": [
            r"hidden\s+(fee|charge|cost)",
            r"surprise\s+(fee|charge|bill)",
            r"not\s+disclosed",
            r"wasn't\s+told\s+about",
            r"found\s+out\s+about\s+\$",
            r"additional\s+charges",
            r"unexpected\s+(cost|bill)",
        ],
        "confidence": 0.85,
        "category": "transparency_gap",
        "signal_type": "information_asymmetry",
        "examples": [
            "hidden fees at move-out",
            "surprise charge for parking",
            "wasn't told about the pet deposit"
        ],
        "opportunity_extraction": "fee_transparency_tool"
    },
    
    # TIER 2: Service Quality Issues
    "maintenance_problems": {
        "patterns": [
            r"maintenance\s+(takes|took)\s+(forever|days|weeks)",
            r"still\s+(waiting|haven't|no)\s+.*\s+fix",
            r"reported\s+.*\s+months?\s+ago",
            r"multiple\s+requests",
            r"never\s+(fixed|repaired|responded)",
            r"broken\s+.*\s+for\s+(weeks|months)",
        ],
        "confidence": 0.80,
        "category": "service_reliability",
        "signal_type": "process_breakdown",
        "examples": [
            "maintenance takes forever",
            "reported leak 3 weeks ago, still waiting",
            "broken AC for 2 months"
        ],
        "opportunity_extraction": "maintenance_tracking_app"
    },
    
    "noise_complaints": {
        "patterns": [
            r"noisy\s+(neighbors|building|area)",
            r"loud\s+(music|parties|noise)",
            r"can\s+hear\s+(everything|neighbors)",
            r"thin\s+walls",
            r"sound\s+insulation",
            r"airport\s+noise",
            r"disturbed\s+by",
        ],
        "confidence": 0.75,
        "category": "quality_of_life",
        "signal_type": "environmental_issue",
        "examples": [
            "thin walls - can hear everything",
            "airport noise is terrible",
            "loud neighbors every night"
        ],
        "opportunity_extraction": "noise_rating_database"
    },
    
    # TIER 3: Utility/Infrastructure Issues
    "utility_problems": {
        "patterns": [
            r"water\s+(smells|tastes|quality)",
            r"sulfur\s+smell",
            r"hot\s+water\s+(issues|runs out)",
            r"internet\s+(slow|unreliable|down)",
            r"hvac\s+(broken|doesn't work)",
            r"heating.*cooling",
        ],
        "confidence": 0.85,
        "category": "infrastructure_quality",
        "signal_type": "building_deficiency",
        "examples": [
            "water smells like sulfur",
            "hot water runs out constantly",
            "internet constantly goes down"
        ],
        "opportunity_extraction": "building_quality_report"
    },
    
    "parking_problems": {
        "patterns": [
            r"parking\s+(is|very)\s+(expensive|limited|difficult)",
            r"no\s+(parking|spots|guest parking)",
            r"guest\s+parking\s+(fee|charge|\$)",
            r"can't\s+find\s+parking",
            r"parking\s+garage\s+(full|always)",
        ],
        "confidence": 0.80,
        "category": "amenity_access",
        "signal_type": "resource_scarcity",
        "examples": [
            "guest parking now costs $5 per day",
            "parking garage always full",
            "no visitor parking available"
        ],
        "opportunity_extraction": "parking_solution_service"
    },
    
    # TIER 4: Management/Communication Issues
    "management_problems": {
        "patterns": [
            r"management\s+(changed|new|terrible|poor)",
            r"no\s+(communication|response|follow-up)",
            r"never\s+(answer|respond|return)",
            r"sent\s+to\s+collections",
            r"credit\s+report",
            r"lease\s+(renewal|terms|increase)",
        ],
        "confidence": 0.85,
        "category": "management_quality",
        "signal_type": "service_breakdown",
        "examples": [
            "new management is terrible",
            "sent to collections without notice",
            "lease renewal increase was 20%"
        ],
        "opportunity_extraction": "tenant_rights_platform"
    },
}

# ============================================================================
# CHILDCARE/EDUCATION KEYWORD PATTERNS
# ============================================================================

CHILDCARE_PATTERNS = {
    
    "availability_issues": {
        "patterns": [
            r"waitlist\s+(is|of)\s+\d+\s+(months|year)",
            r"no\s+(spots|availability|openings)",
            r"wait\s+(time|list|period)",
            r"can't\s+find\s+(daycare|childcare|preschool)",
            r"full\s+capacity",
            r"closed\s+enrollment",
        ],
        "confidence": 0.90,
        "category": "supply_shortage",
        "signal_type": "market_gap",
        "examples": [
            "18-month waitlist",
            "no spots available for infants",
            "closed enrollment for 2024"
        ],
        "opportunity_extraction": "childcare_marketplace"
    },
    
    "cost_complaints": {
        "patterns": [
            r"too\s+expensive",
            r"\$\d+\s+per\s+(month|week|day)",
            r"can't\s+afford",
            r"price\s+increase",
            r"tuition\s+went\s+up",
            r"more\s+than\s+rent",
            r"financial\s+burden",
        ],
        "confidence": 0.85,
        "category": "affordability_crisis",
        "signal_type": "price_barrier",
        "examples": [
            "$2000/month for infant care",
            "tuition increased 15% this year",
            "costs more than my rent"
        ],
        "opportunity_extraction": "affordable_childcare_alternative"
    },
    
    "hours_flexibility": {
        "patterns": [
            r"hours\s+(don't|too)\s+(work|limited|short)",
            r"close\s+(too\s+early|at\s+\d+pm)",
            r"need\s+(evening|weekend|flexible)",
            r"work\s+schedule\s+doesn't\s+match",
            r"no\s+(after-hours|late|weekend)",
        ],
        "confidence": 0.80,
        "category": "schedule_mismatch",
        "signal_type": "service_gap",
        "examples": [
            "closes at 5pm, need until 7pm",
            "no weekend care available",
            "work schedule doesn't align"
        ],
        "opportunity_extraction": "flexible_hours_childcare"
    },
    
    "quality_concerns": {
        "patterns": [
            r"high\s+turnover",
            r"different\s+teacher\s+every",
            r"ratios?\s+(too\s+high|bad|poor)",
            r"not\s+enough\s+staff",
            r"safety\s+(concern|issue|problem)",
            r"curriculum\s+(lacking|poor|basic)",
        ],
        "confidence": 0.85,
        "category": "quality_degradation",
        "signal_type": "service_quality",
        "examples": [
            "high teacher turnover - 5 in 6 months",
            "child-to-teacher ratio is 8:1",
            "safety concerns with outdoor area"
        ],
        "opportunity_extraction": "quality_verification_service"
    },
}

# ============================================================================
# RESTAURANT/FOOD SERVICE KEYWORD PATTERNS
# ============================================================================

RESTAURANT_PATTERNS = {
    
    "wait_time_issues": {
        "patterns": [
            r"wait\s+(time|was|is)\s+\d+\s+(minutes|hours|min|hr)",
            r"waited\s+(over|more than)\s+\d+",
            r"long\s+wait",
            r"reservation\s+(wait|delay|late)",
            r"seated\s+(late|after\s+\d+)",
        ],
        "confidence": 0.75,
        "category": "service_speed",
        "signal_type": "efficiency_gap",
        "examples": [
            "45-minute wait with reservation",
            "waited over an hour for table",
            "always a long wait"
        ],
        "opportunity_extraction": "queue_management_system"
    },
    
    "reservation_problems": {
        "patterns": [
            r"can't\s+(get|make|find)\s+reservation",
            r"booked\s+(weeks|months)\s+(out|ahead|in advance)",
            r"impossible\s+to\s+reserve",
            r"always\s+full",
            r"reservation\s+(system|app)\s+(broken|bad)",
        ],
        "confidence": 0.80,
        "category": "access_friction",
        "signal_type": "booking_gap",
        "examples": [
            "can't get weekend reservations",
            "booked 3 months in advance",
            "reservation system never works"
        ],
        "opportunity_extraction": "reservation_aggregator"
    },
    
    "delivery_issues": {
        "patterns": [
            r"delivery\s+(took|was|over)\s+\d+\s+(minutes|hours|min|hr)",
            r"cold\s+when\s+arrived",
            r"wrong\s+order",
            r"missing\s+items",
            r"driver\s+(couldn't find|got lost|late)",
            r"delivery\s+fee\s+\$\d+",
        ],
        "confidence": 0.80,
        "category": "delivery_quality",
        "signal_type": "logistics_gap",
        "examples": [
            "delivery took 90 minutes",
            "food was cold when it arrived",
            "$8 delivery fee for 2 miles"
        ],
        "opportunity_extraction": "local_delivery_service"
    },
    
    "dietary_limitations": {
        "patterns": [
            r"no\s+(vegan|vegetarian|gluten-free|dairy-free)",
            r"limited\s+(options|menu|choices)\s+for",
            r"can't\s+accommodate",
            r"allergy\s+(concerns|issues|problems)",
            r"nothing\s+for\s+(kids|children|toddlers)",
        ],
        "confidence": 0.75,
        "category": "menu_gaps",
        "signal_type": "dietary_underserved",
        "examples": [
            "no vegan options at all",
            "limited gluten-free choices",
            "can't accommodate nut allergies"
        ],
        "opportunity_extraction": "dietary_specific_restaurant"
    },
}

# ============================================================================
# HEALTHCARE KEYWORD PATTERNS
# ============================================================================

HEALTHCARE_PATTERNS = {
    
    "appointment_access": {
        "patterns": [
            r"can't\s+get\s+appointment",
            r"next\s+available\s+(is|in)\s+\d+\s+(weeks|months)",
            r"wait\s+(list|time)\s+\d+",
            r"booking\s+(weeks|months)\s+(out|ahead)",
            r"no\s+(appointments|availability)",
            r"new\s+patients\s+not\s+accepted",
        ],
        "confidence": 0.90,
        "category": "access_shortage",
        "signal_type": "supply_constraint",
        "examples": [
            "next available appointment is 3 months out",
            "wait list of 6 weeks for new patients",
            "not accepting new patients"
        ],
        "opportunity_extraction": "healthcare_marketplace"
    },
    
    "wait_time_issues": {
        "patterns": [
            r"waited\s+\d+\s+(minutes|hours|min|hr)\s+in",
            r"waiting\s+room\s+(for|wait|time)",
            r"appointment\s+\d+\s+minutes\s+late",
            r"always\s+(late|behind|running late)",
            r"never\s+on\s+time",
        ],
        "confidence": 0.75,
        "category": "time_waste",
        "signal_type": "scheduling_inefficiency",
        "examples": [
            "waited 90 minutes in waiting room",
            "doctor always 45 minutes late",
            "appointment was 1 hour behind"
        ],
        "opportunity_extraction": "real_time_wait_tracking"
    },
    
    "insurance_problems": {
        "patterns": [
            r"insurance\s+(doesn't|didn't|won't)\s+cover",
            r"not\s+in\s+network",
            r"out\s+of\s+network",
            r"surprise\s+bill",
            r"billed\s+\$\d+",
            r"copay\s+(is|was)\s+\$\d+",
            r"denied\s+claim",
        ],
        "confidence": 0.85,
        "category": "insurance_friction",
        "signal_type": "financial_barrier",
        "examples": [
            "insurance didn't cover procedure",
            "surprise $2000 bill",
            "not in network, paid full price"
        ],
        "opportunity_extraction": "price_transparency_tool"
    },
    
    "specialist_access": {
        "patterns": [
            r"can't\s+find\s+(specialist|doctor for)",
            r"no\s+(specialists|doctors)\s+in\s+area",
            r"nearest\s+(is|specialist)\s+\d+\s+(miles|hours)",
            r"have\s+to\s+travel\s+to",
            r"referral\s+(denied|wait|required)",
        ],
        "confidence": 0.85,
        "category": "specialist_shortage",
        "signal_type": "geographic_gap",
        "examples": [
            "no pediatric allergists in 50 miles",
            "nearest endocrinologist is 2 hours away",
            "can't find specialist who accepts my insurance"
        ],
        "opportunity_extraction": "telemedicine_specialist"
    },
}

# ============================================================================
# HOME SERVICES KEYWORD PATTERNS
# ============================================================================

HOME_SERVICES_PATTERNS = {
    
    "reliability_issues": {
        "patterns": [
            r"no\s+show",
            r"didn't\s+show\s+up",
            r"cancelled\s+(last minute|day of)",
            r"never\s+(showed|arrived|came)",
            r"stood\s+me\s+up",
            r"rescheduled\s+\d+\s+times",
        ],
        "confidence": 0.90,
        "category": "service_reliability",
        "signal_type": "trust_gap",
        "examples": [
            "no show without calling",
            "cancelled day of appointment",
            "rescheduled 3 times then never came"
        ],
        "opportunity_extraction": "verified_contractor_platform"
    },
    
    "pricing_transparency": {
        "patterns": [
            r"quoted\s+\$\d+.*charged\s+\$\d+",
            r"overcharged",
            r"hidden\s+(fees|charges|costs)",
            r"estimate\s+was\s+\$\d+.*bill\s+was\s+\$\d+",
            r"unexpected\s+(charges|costs|fees)",
            r"price\s+(doubled|tripled|increased)",
        ],
        "confidence": 0.85,
        "category": "price_transparency",
        "signal_type": "trust_erosion",
        "examples": [
            "quoted $200, charged $650",
            "hidden fees added $300 to bill",
            "estimate was $500, bill was $1200"
        ],
        "opportunity_extraction": "fixed_price_service_platform"
    },
    
    "quality_issues": {
        "patterns": [
            r"poor\s+quality\s+work",
            r"had\s+to\s+hire\s+someone\s+else\s+to\s+fix",
            r"came\s+back\s+\d+\s+times",
            r"still\s+(broken|not working|leaking)",
            r"worse\s+than\s+before",
            r"damage",
        ],
        "confidence": 0.85,
        "category": "workmanship_quality",
        "signal_type": "quality_gap",
        "examples": [
            "poor quality work, had to redo",
            "still leaking after 3 visits",
            "damaged my wall during install"
        ],
        "opportunity_extraction": "quality_guarantee_service"
    },
    
    "emergency_access": {
        "patterns": [
            r"couldn't\s+find\s+anyone\s+(for|on)",
            r"no\s+one\s+available\s+(on|for)\s+(weekend|emergency|holiday)",
            r"emergency\s+(fee|charge|rate)",
            r"waited\s+\d+\s+(hours|days)\s+for\s+emergency",
        ],
        "confidence": 0.80,
        "category": "emergency_access",
        "signal_type": "availability_gap",
        "examples": [
            "couldn't find anyone for weekend emergency",
            "no plumbers available on Sunday",
            "$500 emergency fee for same-day service"
        ],
        "opportunity_extraction": "emergency_service_network"
    },
}

# ============================================================================
# RATING-BASED SIGNAL AMPLIFICATION
# ============================================================================

RATING_WEIGHTS = {
    # Google Maps uses 1-5 stars
    1: 1.0,   # 1-star = maximum signal weight
    2: 0.85,  # 2-star = high signal weight
    3: 0.60,  # 3-star = moderate signal weight
    4: 0.20,  # 4-star = low signal weight (only strong patterns)
    5: 0.0    # 5-star = ignore (positive reviews)
}

# ============================================================================
# ENGAGEMENT MULTIPLIERS
# ============================================================================

ENGAGEMENT_BOOSTS = {
    # Yelp "useful" votes, Google "helpful" votes
    "high_engagement": {
        "threshold": 10,  # 10+ votes
        "multiplier": 1.2
    },
    "medium_engagement": {
        "threshold": 5,
        "multiplier": 1.1
    },
    "verified_purchase": {
        "multiplier": 1.15  # Verified resident/customer
    },
    "photo_attached": {
        "multiplier": 1.1  # Review includes photos (evidence)
    },
    "owner_response": {
        # If owner responded defensively, boost signal
        "defensive_patterns": [
            r"we regret",
            r"we're sorry you feel",
            r"we take.*seriously",
            r"please contact us"
        ],
        "multiplier": 1.15
    }
}

# ============================================================================
# COMPETITOR MENTIONS (Strong Signal)
# ============================================================================

COMPETITIVE_PATTERNS = {
    "switching_signals": {
        "patterns": [
            r"switched\s+to\s+[A-Z][a-z]+",
            r"went\s+to\s+[A-Z][a-z]+\s+instead",
            r"trying\s+[A-Z][a-z]+\s+next",
            r"[A-Z][a-z]+\s+is\s+better",
            r"should\s+have\s+gone\s+to\s+[A-Z][a-z]+",
        ],
        "confidence": 0.90,
        "category": "competitive_displacement",
        "extraction": "extract_winning_competitor"
    }
}

# ============================================================================
# QUANTIFICATION PATTERNS (Add Weight)
# ============================================================================

QUANTIFICATION_BOOSTS = {
    # Dollar amounts indicate serious friction
    "dollar_amount": {
        "pattern": r"\$\d+",
        "multiplier": 1.1
    },
    # Time waste
    "time_amount": {
        "pattern": r"\d+\s+(hours?|minutes?|days?|weeks?|months?)",
        "multiplier": 1.1
    },
    # Frequency
    "frequency": {
        "patterns": [
            r"every\s+(time|day|week|month)",
            r"\d+\s+times",
            r"always",
            r"constantly"
        ],
        "multiplier": 1.15
    }
}

# ============================================================================
# INDUSTRY CLASSIFIER
# ============================================================================

def classify_business_category(business_name: str, business_type: str = None) -> str:
    """
    Determine which industry pattern set to use
    
    Args:
        business_name: Name of business from review
        business_type: Optional Google Maps category (e.g., "restaurant", "apartment")
    
    Returns:
        Industry category string
    """
    # Direct category mapping from Google Maps API
    if business_type:
        category_map = {
            # Real Estate / Housing
            "apartment_complex": "apartment",
            "housing": "apartment",
            "real_estate": "apartment",
            "property": "apartment",
            "rental": "apartment",
            # Childcare / Education
            "daycare": "childcare",
            "preschool": "childcare",
            "school": "education",
            "university": "education",
            "college": "education",
            "tutoring": "education",
            "learning": "education",
            # Food & Beverage
            "restaurant": "restaurant",
            "cafe": "restaurant",
            "food": "restaurant",
            "bakery": "restaurant",
            "bar": "restaurant",
            "coffee": "restaurant",
            "diner": "restaurant",
            # Healthcare
            "doctor": "healthcare",
            "clinic": "healthcare",
            "hospital": "healthcare",
            "dentist": "healthcare",
            "pharmacy": "healthcare",
            "medical": "healthcare",
            "veterinary": "healthcare",
            "therapy": "healthcare",
            "chiropractor": "healthcare",
            # Home Services
            "plumber": "home_services",
            "electrician": "home_services",
            "contractor": "home_services",
            "hvac": "home_services",
            "roofing": "home_services",
            "landscaping": "home_services",
            "cleaning": "home_services",
            "pest": "home_services",
            "moving": "home_services",
            # Retail / Shopping
            "store": "retail",
            "shop": "retail",
            "retail": "retail",
            "supermarket": "retail",
            "grocery": "retail",
            "mall": "retail",
            "boutique": "retail",
            # Fitness & Wellness
            "gym": "fitness",
            "fitness": "fitness",
            "yoga": "fitness",
            "spa": "fitness",
            "wellness": "fitness",
            "pilates": "fitness",
            "crossfit": "fitness",
            # Beauty & Personal Care
            "salon": "beauty",
            "barbershop": "beauty",
            "beauty": "beauty",
            "nail": "beauty",
            "hair": "beauty",
            # Automotive
            "auto": "automotive",
            "car": "automotive",
            "mechanic": "automotive",
            "dealership": "automotive",
            "tire": "automotive",
            "car_wash": "automotive",
            "gas_station": "automotive",
            # Professional Services
            "lawyer": "professional",
            "attorney": "professional",
            "accountant": "professional",
            "insurance": "professional",
            "bank": "financial",
            "financial": "financial",
            "tax": "financial",
            # Entertainment
            "entertainment": "entertainment",
            "theater": "entertainment",
            "cinema": "entertainment",
            "museum": "entertainment",
            "amusement": "entertainment",
            "bowling": "entertainment",
            # Travel / Transportation
            "hotel": "travel",
            "motel": "travel",
            "airport": "transportation",
            "parking": "transportation",
            "transit": "transportation",
            # Pet Services
            "pet": "pet_services",
            "veterinarian": "pet_services",
            "grooming": "pet_services",
            "kennel": "pet_services",
        }
        
        for key, industry in category_map.items():
            if key in business_type.lower():
                return industry
    
    # Fallback: keyword matching in business name
    business_lower = business_name.lower()
    
    if any(word in business_lower for word in ["apartment", "residences", "living", "lofts", "realty", "properties"]):
        return "apartment"
    elif any(word in business_lower for word in ["childcare", "daycare", "preschool", "montessori", "nursery"]):
        return "childcare"
    elif any(word in business_lower for word in ["restaurant", "cafe", "bistro", "grill", "pizza", "sushi", "diner", "eatery"]):
        return "restaurant"
    elif any(word in business_lower for word in ["medical", "clinic", "doctor", "dental", "health", "hospital", "pharmacy"]):
        return "healthcare"
    elif any(word in business_lower for word in ["plumbing", "electric", "repair", "contractor", "hvac", "roofing", "landscap"]):
        return "home_services"
    elif any(word in business_lower for word in ["gym", "fitness", "yoga", "crossfit", "workout", "pilates"]):
        return "fitness"
    elif any(word in business_lower for word in ["salon", "barber", "beauty", "nail", "spa", "hair"]):
        return "beauty"
    elif any(word in business_lower for word in ["auto", "car", "mechanic", "tire", "motor", "vehicle"]):
        return "automotive"
    elif any(word in business_lower for word in ["store", "shop", "mart", "retail", "boutique", "outlet"]):
        return "retail"
    elif any(word in business_lower for word in ["school", "academy", "university", "college", "tutor", "learning"]):
        return "education"
    elif any(word in business_lower for word in ["bank", "credit", "finance", "insurance", "invest", "tax"]):
        return "financial"
    elif any(word in business_lower for word in ["law", "attorney", "legal", "accountant", "consult"]):
        return "professional"
    elif any(word in business_lower for word in ["hotel", "motel", "inn", "resort", "lodge"]):
        return "travel"
    elif any(word in business_lower for word in ["pet", "vet", "animal", "groom", "kennel"]):
        return "pet_services"
    
    return "retail"

# ============================================================================
# PATTERN MATCHER
# ============================================================================

def get_industry_patterns(industry: str) -> dict:
    """Get the appropriate pattern dictionary for an industry"""
    pattern_map = {
        "apartment": APARTMENT_PATTERNS,
        "childcare": CHILDCARE_PATTERNS,
        "restaurant": RESTAURANT_PATTERNS,
        "healthcare": HEALTHCARE_PATTERNS,
        "home_services": HOME_SERVICES_PATTERNS,
        # Map new categories to similar existing patterns
        "fitness": HEALTHCARE_PATTERNS,
        "beauty": HOME_SERVICES_PATTERNS,
        "automotive": HOME_SERVICES_PATTERNS,
        "retail": RESTAURANT_PATTERNS,
        "education": CHILDCARE_PATTERNS,
        "financial": HOME_SERVICES_PATTERNS,
        "professional": HOME_SERVICES_PATTERNS,
        "travel": RESTAURANT_PATTERNS,
        "entertainment": RESTAURANT_PATTERNS,
        "pet_services": HEALTHCARE_PATTERNS,
        "transportation": HOME_SERVICES_PATTERNS,
    }
    return pattern_map.get(industry, HOME_SERVICES_PATTERNS)

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
Example: Scoring a Google Maps apartment review

review = {
    'text': 'New guest parking policy is very disappointing. Guests now have to pay $5 
             every single time just to park in the garage. It used to be much more reasonable.',
    'rating': 2,
    'useful_count': 15,
    'business_name': 'Indigo West Palm Beach',
    'business_type': 'apartment_complex'
}

industry = classify_business_category(review['business_name'], review['business_type'])
# Returns: 'apartment'

patterns = get_industry_patterns(industry)
# Returns: APARTMENT_PATTERNS

# Pattern matching:
# - Detects: "new...policy" (0.90 confidence)
# - Detects: "pay $5" (quantification boost +0.10)  
# - Detects: "used to be" (0.90 confidence)
# - Rating: 2-star (0.85 weight)
# - Engagement: 15 votes (1.2x multiplier)

# Final signal score: 0.90 * 0.85 * 1.2 * 1.1 = 1.0+ (GOLDMINE)
# Opportunity: "Guest parking fee elimination service"
"""
