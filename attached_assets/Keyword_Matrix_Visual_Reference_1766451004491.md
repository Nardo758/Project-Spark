# Keyword Matrix - Visual Reference Guide

Quick reference for location and business idea validation patterns.

---

## 🗺️ LOCATION VALIDATION MATRIX

### High Confidence (0.90-1.0) - USE IMMEDIATELY

| Pattern Type | Examples | Confidence | Extraction |
|-------------|----------|------------|------------|
| **City, State** | "in San Francisco, CA"<br/>"parking in NYC, NY"<br/>"living in Boston, MA" | 0.95 | Regex capture |
| **Full Address** | "123 Main Street"<br/>"456 Oak Avenue, SF" | 0.90 | Address parser |
| **ZIP Code** | "94102"<br/>"10001-1234" | 0.95 | ZIP lookup |
| **API Location** | Google Places<br/>Yelp Business<br/>Nextdoor Neighborhood | 1.0 | Structured data |

### Medium Confidence (0.70-0.89) - VERIFY

| Pattern Type | Examples | Confidence | Notes |
|-------------|----------|------------|-------|
| **City Only** | "in San Francisco"<br/>"Chicago restaurants" | 0.85 | Add state via lookup |
| **Neighborhood** | "the Mission"<br/>"Williamsburg"<br/>"my neighborhood" | 0.75 | Requires city context |
| **Subreddit Name** | r/sanfrancisco<br/>r/nyc | 0.95 | Direct mapping |

### Craigslist Domain Mapping

| Pattern Type | Examples | Confidence | Notes |
|-------------|----------|------------|-------|
| **City Domain** | sfbay.craigslist.org<br/>newyork.craigslist.org<br/>losangeles.craigslist.org | 0.95 | Direct city mapping |
| **Location Field** | "(Mission District)"<br/>"(Downtown)" | 0.85 | Neighborhood refinement |

### Low Confidence (0.50-0.69) - NEEDS CONTEXT

| Pattern Type | Examples | Confidence | Required Context |
|-------------|----------|------------|------------------|
| **Proximity** | "near me"<br/>"walking distance"<br/>"locally" | 0.65 | User location, subreddit |
| **Regional** | "Bay Area"<br/>"East Coast"<br/>"Silicon Valley" | 0.60 | Expand to cities |

---

## 💡 BUSINESS IDEA VALIDATION MATRIX

### 🏆 TIER 1: GOLDMINE (0.90-1.0)

**Explicit Demand Signals**

| Pattern | Example | Score | Why It's Gold |
|---------|---------|-------|---------------|
| "I wish there was" | "I wish there was an app that..." | 1.0 | Explicit unmet need |
| "Why doesn't anyone make" | "Why doesn't anyone make a service for..." | 1.0 | Market gap identified |
| "Can someone please build" | "Can someone please build a platform for..." | 1.0 | Direct request |
| "Someone needs to build" | "Someone needs to build a tool that..." | 1.0 | Problem + solution type |
| "We need a" | "We need a better way to..." | 0.95 | Community need |

**Willingness to Pay**

| Pattern | Example | Score | Validation |
|---------|---------|-------|------------|
| "I'd pay for" | "I'd pay for a solution that..." | 0.95 | Monetization validated |
| "I would pay $X" | "I would pay $50/month for this" | 1.0 | Price point given |
| "Shut up and take my money" | "Shut up and take my money!" | 0.95 | Strong buying intent |
| "Worth paying for" | "This would be worth paying for" | 0.90 | Value acknowledged |

**Product Demand** (NEW!)

| Pattern | Example | Score | Why It's Gold |
|---------|---------|-------|---------------|
| "Where can I buy" | "Where can I buy quality [X] in SF?" | 0.90 | Active purchase intent |
| "Can't find anywhere" | "Can't find this product anywhere" | 0.95 | Supply gap |
| "Out of stock everywhere" | "Out of stock at every store" | 0.95 | Inventory issue |
| "Who sells" | "Who sells [X] in my area?" | 0.90 | Seeking supplier |
| "Need to buy ASAP" | "Need to buy [X] today" | 0.95 | Urgency + intent |

**Service Demand** (NEW!)

| Pattern | Example | Score | Why It's Gold |
|---------|---------|-------|---------------|
| "Need a [X] who" | "Need a plumber who can come today" | 0.90 | Immediate need |
| "Looking for a good [X]" | "Looking for a good accountant" | 0.90 | Active search |
| "Anyone know a good [X]" | "Anyone know a good dentist?" | 0.90 | Recommendation seeking |
| "Urgently need" | "Urgently need contractor" | 0.95 | High urgency |
| "Where to find a [X]" | "Where to find reliable handyman?" | 0.90 | Discovery problem |

**Marketplace Gaps** (NEW!)

| Pattern | Example | Score | Ultimate Signal |
|---------|---------|-------|-----------------|
| "Why is there no" | "Why is there no same-day delivery?" | 0.95 | Service gap |
| "Why doesn't anyone offer" | "Why doesn't anyone offer weekends?" | 0.95 | Feature gap |
| "Can't find any [X] that" | "Can't find any cleaner that's eco" | 0.95 | Niche gap |
| "Doesn't exist" | "This service doesn't exist!" | 0.95 | Market gap |

---

### 🔥 TIER 2: VALIDATED (0.80-0.89)

**Frustration Signals**

| Pattern | Example | Score | Emotional Intensity |
|---------|---------|-------|-------------------|
| "So frustrating that" | "So frustrating that there's no..." | 0.85 | High |
| "I can't believe we still" | "I can't believe we still have to..." | 0.85 | High |
| "It's ridiculous that" | "It's ridiculous that this doesn't exist" | 0.85 | High |
| "Every single time" | "Every single time I need to..." | 0.80 | Frequency indicator |
| "Always have to" | "I always have to..." | 0.75 | Repetitive problem |

**Intensity Markers**

| Pattern | Example | Score | Boost |
|---------|---------|-------|-------|
| "!!!" (multiple) | "This is terrible!!!" | 0.80 | +1.3x multiplier |
| "Never again" | "Never again will I..." | 0.85 | Final straw |
| "Worst [X] ever" | "Worst experience ever" | 0.80 | Superlative |
| "Completely useless" | "Completely useless service" | 0.80 | Total failure |

**Product Quality Issues** (NEW!)

| Pattern | Example | Score | Gap Identified |
|---------|---------|-------|----------------|
| "[X] broke after" | "Laptop broke after 3 months" | 0.85 | Durability gap |
| "Terrible quality" | "Terrible quality - not worth it" | 0.85 | Quality alternative needed |
| "Doesn't last" | "Headphones don't last 6 months" | 0.85 | Reliability issue |
| "Always breaking" | "Chargers always breaking" | 0.85 | Repeat problem |
| "Cheap [X] that breaks" | "Cheap furniture that breaks" | 0.90 | Quality demand |

**Service Quality Issues** (NEW!)

| Pattern | Example | Score | Gap Identified |
|---------|---------|-------|----------------|
| "Never showed up" | "Plumber never showed up" | 0.90 | Reliability gap |
| "Terrible service" | "Terrible customer service" | 0.80 | Quality gap |
| "Overcharged me" | "Overcharged me $500" | 0.85 | Price transparency |
| "Did terrible job" | "Painter did terrible job" | 0.85 | Quality control needed |
| "Cancelled last minute" | "Cancelled 2 hours before" | 0.85 | Reliability problem |

---

### ✅ TIER 3: COMMUNITY VALIDATED (0.70-0.79)

**Community Questions**

| Pattern | Example | Score | Social Proof |
|---------|---------|-------|-------------|
| "Does anyone else struggle" | "Does anyone else struggle with..." | 0.75 | Shared problem |
| "Am I the only one who" | "Am I the only one who finds..." | 0.75 | Seeking validation |
| "How do you deal with" | "How do you deal with..." | 0.70 | Solution seeking |
| "What do you use for" | "What do you use for..." | 0.70 | Tool discovery |
| "Anyone found a solution" | "Has anyone found a solution for..." | 0.75 | Unsolved problem |

**Alternative Seeking**

| Pattern | Example | Score | Market Signal |
|---------|---------|-------|---------------|
| "Looking for a better" | "Looking for a better way to..." | 0.75 | Incumbent weakness |
| "Alternatives to [X]" | "What are alternatives to Uber?" | 0.75 | Competitive gap |
| "Sick of [X]" | "I'm sick of using..." | 0.75 | Churn signal |
| "Gave up on [X]" | "I gave up on finding..." | 0.70 | Abandonment |

**Product Recommendations** (NEW!)

| Pattern | Example | Score | Market Signal |
|---------|---------|-------|---------------|
| "What's the best [X]" | "What's the best laptop for coding?" | 0.80 | Product research |
| "Recommend a [X]" | "Recommend a good coffee maker" | 0.80 | Purchase consideration |
| "Which [X] should I" | "Which standing desk should I buy?" | 0.75 | Decision stage |
| "Better than [X]" | "Something better than basic blender" | 0.80 | Quality seeking |

**Service Recommendations** (NEW!)

| Pattern | Example | Score | Market Signal |
|---------|---------|-------|---------------|
| "Best [X] in [city]" | "Best dentist in Chicago?" | 0.85 | Research stage |
| "Who do you use for [X]" | "Who do you use for pest control?" | 0.85 | Referral seeking |
| "Good [X] near me" | "Good dog groomer near me?" | 0.85 | Local + service |
| "Reliable [X] in [area]" | "Reliable electrician in Brooklyn?" | 0.85 | Quality emphasis |

**Craigslist Wanted Ads** (High Signal)

| Pattern | Example | Score | Why It's Strong |
|---------|---------|-------|-----------------|
| "Wanted:" | "Wanted: parking near BART" | 0.85 | Explicit unmet need |
| "Looking for" | "Looking for 1BR apartment" | 0.85 | Active search |
| "Need ASAP" | "Need parking spot ASAP" | 0.90 | Urgency + need |
| "Willing to pay $X" | "Willing to pay $500/mo" | 0.95 | Budget + intent |
| "Desperately need" | "Desperately need childcare" | 0.90 | High urgency |

---

### ⚠️ TIER 4: WEAK SIGNAL (0.60-0.69)

**Problem Indicators**

| Pattern | Example | Score | Needs Context |
|---------|---------|-------|---------------|
| "There has to be a better way" | "There has to be a better way to..." | 0.65 | ✓ |
| "This shouldn't be this hard" | "This shouldn't be this hard" | 0.65 | ✓ |
| "No good options for" | "No good options for..." | 0.65 | ✓ |
| "Waste of time" | "Such a waste of time" | 0.60 | ✓ |
| "Such a hassle" | "It's such a hassle to..." | 0.60 | ✓ |

---

## 🎯 BUSINESS CATEGORY KEYWORDS

### Transportation (Parking, Transit, Rideshare)

**Keywords:** parking, uber, lyft, taxi, rideshare, car, transit, bus, train, commute, traffic

**Signals:**
- ✓ "Can't find parking"
- ✓ "Parking is expensive"
- ✓ "No parking spots"
- ✓ "Traffic is terrible"

**Opportunities:** Parking solutions, ride sharing, last-mile transit

---

### Food & Beverage

**Keywords:** restaurant, food, delivery, dining, meal, lunch, dinner, coffee, takeout

**Signals:**
- ✓ "Food delivery is slow"
- ✓ "Restaurant wait times"
- ✓ "No good options for"
- ✓ "Food is expensive"

**Opportunities:** Food delivery, meal prep, restaurant tech, dietary-specific

---

### Childcare & Education

**Keywords:** daycare, childcare, babysitter, nanny, preschool, school, tutor, kids

**Signals:**
- ✓ "Can't find daycare"
- ✓ "Childcare is expensive"
- ✓ "No available slots"
- ✓ "Long waitlist"

**Opportunities:** Childcare platform, tutoring, babysitter matching, edu-tech

---

### Healthcare

**Keywords:** doctor, dentist, medical, health, clinic, appointment, insurance, pharmacy

**Signals:**
- ✓ "Can't get appointment"
- ✓ "Doctor wait times"
- ✓ "Insurance doesn't cover"
- ✓ "Expensive copay"

**Opportunities:** Telemedicine, appointment booking, price transparency

---

### Home Services

**Keywords:** plumber, electrician, handyman, repair, cleaning, contractor, renovation

**Signals:**
- ✓ "Can't find reliable"
- ✓ "Overcharged by"
- ✓ "No show"
- ✓ "Poor quality work"

**Opportunities:** Home service platform, contractor matching, price comparison

---

### Real Estate & Housing

**Keywords:** apartment, housing, rent, lease, landlord, property, moving, roommate

**Signals:**
- ✓ "Can't find apartment"
- ✓ "Rent is too expensive"
- ✓ "Bad landlord"
- ✓ "Hidden fees"

**Opportunities:** Rental platform, roommate matching, moving services

---

### Pet Services

**Keywords:** pet, dog, cat, vet, grooming, pet sitting, dog walking, boarding

**Signals:**
- ✓ "Can't find pet sitter"
- ✓ "Vet is expensive"
- ✓ "No available boarding"
- ✓ "Grooming wait time"

**Opportunities:** Pet care platform, dog walking, vet booking

---

### Financial Services

**Keywords:** bank, credit, loan, mortgage, insurance, investment, payment, budget

**Signals:**
- ✓ "Bank fees are high"
- ✓ "Poor customer service"
- ✓ "Can't get approved"
- ✓ "Hidden charges"

**Opportunities:** Fintech, fee transparency, budget tool, insurance comparison

---

### Product Marketplace (NEW!)

**Keywords:** buy, purchase, product, shop, retail, sell, inventory, stock, equipment

**Signals:**
- ✓ "Can't find anywhere"
- ✓ "Out of stock"
- ✓ "Where to buy"
- ✓ "Terrible quality"
- ✓ "Breaks after"

**Opportunities:** Niche e-commerce, specialty retailer, quality alternative, marketplace platform

---

### Service Marketplace (NEW!)

**Keywords:** service, provider, professional, contractor, freelancer, booking, appointment, hire

**Signals:**
- ✓ "Can't find reliable"
- ✓ "Need a good"
- ✓ "Never showed up"
- ✓ "Overcharged"

**Opportunities:** Service marketplace, booking platform, quality verification, price transparency

---

### Local Services (NEW!)

**Keywords:** near me, nearby, local, delivery, pickup, same day, emergency, 24/7

**Signals:**
- ✓ "Nothing nearby"
- ✓ "No delivery options"
- ✓ "Too far away"
- ✓ "No emergency service"

**Opportunities:** Hyperlocal marketplace, delivery service, emergency service, 24/7 availability

---

### Specialty Products (NEW!)

**Keywords:** organic, vegan, specialty, niche, custom, handmade, artisan, eco-friendly, sustainable

**Signals:**
- ✓ "Hard to find"
- ✓ "Limited options"
- ✓ "Only available online"
- ✓ "Not available locally"

**Opportunities:** Specialty retailer, niche marketplace, subscription box, local distribution

---

## 📊 QUANTIFICATION BOOSTERS (+0.10 each)

### Money Mentions
- "$50", "$1,000", "500 dollars", "$5k"
- **Boost:** +0.10 to base score

### Time Mentions
- "2 hours", "30 minutes", "3 weeks", "daily"
- **Boost:** +0.10 to base score

### Frequency Markers
- "Every single time", "always", "constantly", "never"
- **Boost:** +0.10 to base score

### Scale Indicators
- "50%", "3 times a week", "most people", "everyone"
- **Boost:** +0.05 to base score

---

## 🎯 COMPOSITE SCORING FORMULA

```
Base Score (highest pattern match): 0.0 - 1.0
+ Location Confidence Boost: +0.03 to +0.05
+ Category Identified: +0.03
+ Quantification Boosts: +0.10 each (money, time, frequency)
+ Multiple Signal Types: +0.05 to +0.10
+ Source Weight Multiplier: x0.5 to x1.0
+ Engagement Boost: +0.05 to +0.10
= Final Score (capped at 1.0)
```

---

## 🏅 CONFIDENCE TIERS

| Tier | Score Range | Layer | Action |
|------|-------------|-------|---------|
| **GOLDMINE** | 0.85 - 1.00 | Layer 4 | IMMEDIATE REVIEW |
| **VALIDATED** | 0.70 - 0.84 | Layer 3 | PRIORITIZE |
| **WEAK SIGNAL** | 0.50 - 0.69 | Layer 2 | MONITOR |
| **NOISE** | 0.00 - 0.49 | Layer 1 | FILTER OUT |

**Minimum threshold for saving:** 0.70 (VALIDATED or higher)

---

## 🔍 SOURCE-SPECIFIC WEIGHTS

### Reddit
- r/SomebodyMakeThis: **1.0** (explicit requests)
- r/mildlyinfuriating: **0.90** (high frustration)
- r/CrappyDesign: **0.85** (design problems)
- City subreddits: **0.75** (local problems)

### Google Reviews / Yelp
- ⭐ (1 star): **1.0**
- ⭐⭐ (2 stars): **0.85**
- ⭐⭐⭐ (3 stars): **0.65**
- ⭐⭐⭐⭐ (4+ stars): **0.30** (rarely problems)

### Twitter
- High engagement (50+ likes): **+0.10**
- Has location: **+0.10**
- Verified user: **+0.05**

### Nextdoor
- Base confidence: **1.0** (hyper-local)
- Crime & Safety category: **0.90**

### Craigslist
- Wanted ads: **1.0** (explicit unmet needs)
- Services wanted: **0.95**
- Housing wanted: **0.95**
- Price mentioned: **+0.10** boost
- Urgent/ASAP: **+0.10** boost

---

## 📝 EXAMPLE SCORING

### Example 1: Reddit Post (GOLDMINE)

**Post:** "I wish there was an app in San Francisco that helps find parking. I'd pay $20/month!"

**Scoring:**
- "I wish there was": **1.0**
- "in San Francisco": **+0.05** (verified location)
- "$20/month": **+0.10** (money quantification)
- Category (parking): **+0.03**
- High engagement: **+0.10**

**Final Score:** **1.0 → GOLDMINE**

---

### Example 2: Yelp Review (VALIDATED)

**Review:** "So frustrating that they never answer the phone. Every single time I call, goes to voicemail."

**Scoring:**
- "So frustrating that": **0.85**
- "Every single time": **+0.10** (frequency)
- 1-star rating: **×1.0** (weight)
- Category (healthcare): **+0.03**
- Location verified: **+0.05**

**Final Score:** **0.90 → GOLDMINE/VALIDATED**

---

### Example 3: Twitter (NOISE)

**Tweet:** "parking here sucks"

**Scoring:**
- Generic complaint: **0.40**
- No location: **0.0**
- No engagement: **0.0**
- No quantification: **0.0**

**Final Score:** **0.40 → NOISE (filtered out)**

---

### Example 4: Craigslist Wanted Ad (GOLDMINE)

**Post:** "WANTED: Parking spot near Caltrain. Willing to pay up to $300/month. Need ASAP!"

**Scoring:**
- "WANTED": **0.85**
- "Willing to pay up to $300/month": **+0.10** (price quantification)
- "Need ASAP": **+0.10** (urgency)
- Domain (sfbay.craigslist.org): **+0.05** (verified location)
- Category (parking): **+0.03**

**Final Score:** **0.95 → GOLDMINE**

---

## ✅ QUICK CHECKLIST

**For each scraped item, validate:**

- [ ] Location extracted (city/state)?
- [ ] Location confidence ≥ 0.70?
- [ ] Business pattern detected?
- [ ] Pattern score ≥ 0.70?
- [ ] Category identified?
- [ ] Quantification present (money/time)?
- [ ] Final composite score ≥ 0.70?

**If YES to all → SAVE TO DATABASE**
**If NO → FILTER OUT**

---

## 🚀 Usage Summary

1. **Extract location** using source-specific strategy
2. **Match patterns** from business idea matrix
3. **Identify category** from 10+ categories
4. **Check quantifications** (money, time, frequency)
5. **Calculate composite score** using formula
6. **Apply threshold** (≥0.70 to save)
7. **Tag with tier** (GOLDMINE, VALIDATED, etc.)

This ensures **only high-quality, validated opportunities with verified locations** make it into your database!
