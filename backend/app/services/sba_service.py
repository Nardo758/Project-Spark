from typing import Optional, List, Dict


SBA_LOAN_PROGRAMS = [
    {
        "id": 1,
        "name": "7(a) Loan Program",
        "category": "SBA Guaranteed Loans",
        "amount": "Up to $5 million",
        "description": "The SBA's most common loan program, providing financial help for businesses with special requirements.",
        "uses": ["Working capital", "Equipment", "Real estate", "Debt refinancing"],
        "terms": "Up to 25 years for real estate, 10 years for equipment",
        "link": "https://www.sba.gov/funding-programs/loans/7a-loans"
    },
    {
        "id": 2,
        "name": "504 Loan Program",
        "category": "SBA Guaranteed Loans",
        "amount": "Up to $5.5 million",
        "description": "Long-term, fixed-rate financing for major fixed assets that promote business growth and job creation.",
        "uses": ["Land and buildings", "Long-term machinery", "Renovating facilities"],
        "terms": "10-20 years fixed rate",
        "link": "https://www.sba.gov/funding-programs/loans/504-loans"
    },
    {
        "id": 3,
        "name": "Microloans",
        "category": "SBA Guaranteed Loans",
        "amount": "Up to $50,000",
        "description": "Small, short-term loans to help small businesses and certain not-for-profit childcare centers.",
        "uses": ["Working capital", "Inventory", "Supplies", "Furniture", "Equipment"],
        "terms": "Up to 6 years",
        "link": "https://www.sba.gov/funding-programs/loans/microloans"
    },
    {
        "id": 4,
        "name": "Disaster Loans",
        "category": "Disaster Assistance",
        "amount": "Up to $2 million",
        "description": "Low-interest loans to businesses of all sizes affected by declared disasters.",
        "uses": ["Physical damage repair", "Economic injury recovery"],
        "terms": "Up to 30 years",
        "link": "https://www.sba.gov/funding-programs/disaster-assistance"
    },
    {
        "id": 5,
        "name": "Community Advantage Loans",
        "category": "SBA Guaranteed Loans",
        "amount": "Up to $350,000",
        "description": "Loans designed to increase access to capital for small businesses in underserved communities.",
        "uses": ["Working capital", "Equipment", "Debt refinancing"],
        "terms": "Similar to 7(a) loans",
        "link": "https://www.sba.gov/partners/lenders/community-advantage"
    },
    {
        "id": 6,
        "name": "Export Express Loans",
        "category": "Export Financing",
        "amount": "Up to $500,000",
        "description": "Streamlined financing to help small businesses develop or expand their export activities.",
        "uses": ["Export development", "International marketing", "Trade show participation"],
        "terms": "Revolving or term loans",
        "link": "https://www.sba.gov/funding-programs/loans/export-loans"
    }
]


SBA_COURSES = [
    {
        "id": 1,
        "title": "Financing Options for Small Businesses",
        "summary": "An introduction to financing options for your small business, including loans, lines of credit, and alternative financing.",
        "courseCategory": ["Plan your business", "Launch your business"],
        "url": "/course/financing-options-small-businesses",
        "image": {"url": "/sites/default/files/2018-01/shutterstock_648969952_500.jpg", "alt": "Financing Options"}
    },
    {
        "id": 2,
        "title": "How to Prepare a Loan Package",
        "summary": "Learn what documents lenders require and how to present your business in the best light when applying for a loan.",
        "courseCategory": ["Launch your business"],
        "url": "/course/how-prepare-loan-package",
        "image": {"url": "/sites/default/files/2018-02/loan-package.jpg", "alt": "Loan Package"}
    },
    {
        "id": 3,
        "title": "Understanding Your Credit",
        "summary": "Learn about business and personal credit, how they affect your financing options, and strategies to improve your credit score.",
        "courseCategory": ["Plan your business"],
        "url": "/course/understanding-your-credit",
        "image": {"url": "/sites/default/files/2018-02/credit-score.jpg", "alt": "Credit Score"}
    },
    {
        "id": 4,
        "title": "Small Business Taxes and Bookkeeping",
        "summary": "An overview of business taxes, recordkeeping requirements, and financial management best practices.",
        "courseCategory": ["Manage your business"],
        "url": "/course/small-business-taxes",
        "image": {"url": "/sites/default/files/2018-02/taxes.jpg", "alt": "Small Business Taxes"}
    },
    {
        "id": 5,
        "title": "Cash Flow Management",
        "summary": "Learn strategies for managing your business cash flow to maintain financial health and avoid common pitfalls.",
        "courseCategory": ["Manage your business"],
        "url": "/course/cash-flow-management",
        "image": {"url": "/sites/default/files/2018-02/cash-flow.jpg", "alt": "Cash Flow"}
    },
    {
        "id": 6,
        "title": "Understanding SBA Loan Programs",
        "summary": "A comprehensive guide to SBA loan programs, eligibility requirements, and how to apply.",
        "courseCategory": ["Launch your business"],
        "url": "/course/sba-loan-programs",
        "image": {"url": "/sites/default/files/2018-02/sba-loans.jpg", "alt": "SBA Loans"}
    }
]


SBA_LENDER_MATCH_URL = "https://www.sba.gov/funding-programs/loans/lender-match"


class SBAService:
    async def get_loan_programs(self, category: Optional[str] = None) -> List[Dict]:
        programs = SBA_LOAN_PROGRAMS
        if category:
            programs = [p for p in programs if category.lower() in p.get("category", "").lower()]
        return programs

    async def get_financing_courses(self, business_stage: Optional[str] = None) -> List[Dict]:
        courses = SBA_COURSES
        if business_stage:
            courses = [c for c in courses if business_stage in c.get("courseCategory", [])]
        return courses

    async def get_all_courses(self, business_stage: Optional[str] = None) -> List[Dict]:
        return await self.get_financing_courses(business_stage)

    async def get_lender_match_url(self) -> str:
        return SBA_LENDER_MATCH_URL

    async def get_top_sba_lenders(self) -> List[Dict]:
        return TOP_SBA_LENDERS


TOP_SBA_LENDERS = [
    {
        "id": "1",
        "name": "Wells Fargo",
        "description": "One of the largest SBA lenders in the nation, offering 7(a) and 504 loans.",
        "loan_types": ["7(a) Loans", "504 Loans", "SBA Express"],
        "website": "https://www.wellsfargo.com/biz/loans-and-lines/sba-loans",
        "national": True
    },
    {
        "id": "2", 
        "name": "JPMorgan Chase",
        "description": "Major national bank with comprehensive SBA lending programs for small businesses.",
        "loan_types": ["7(a) Loans", "SBA Express"],
        "website": "https://www.chase.com/business/loans/sba-loans",
        "national": True
    },
    {
        "id": "3",
        "name": "U.S. Bank",
        "description": "Offers SBA loans including 7(a), CDC/504, and Express programs nationwide.",
        "loan_types": ["7(a) Loans", "504 Loans", "SBA Express"],
        "website": "https://www.usbank.com/business-banking/business-loans/sba-loans.html",
        "national": True
    },
    {
        "id": "4",
        "name": "Bank of America",
        "description": "Provides SBA 7(a) loans for working capital, equipment, and real estate.",
        "loan_types": ["7(a) Loans"],
        "website": "https://www.bankofamerica.com/smallbusiness/business-financing/sba-loans/",
        "national": True
    },
    {
        "id": "5",
        "name": "Live Oak Bank",
        "description": "Top SBA 7(a) lender specializing in small business lending across industries.",
        "loan_types": ["7(a) Loans", "USDA Loans"],
        "website": "https://www.liveoakbank.com/",
        "national": True
    },
    {
        "id": "6",
        "name": "Celtic Bank",
        "description": "National SBA lender focused on small business financing with fast processing.",
        "loan_types": ["7(a) Loans", "SBA Express"],
        "website": "https://www.celticbank.com/",
        "national": True
    },
    {
        "id": "7",
        "name": "Byline Bank",
        "description": "One of the top SBA lenders, offering various SBA loan programs.",
        "loan_types": ["7(a) Loans", "504 Loans"],
        "website": "https://www.bylinebank.com/business/sba-loans/",
        "national": True
    },
    {
        "id": "8",
        "name": "Huntington National Bank",
        "description": "Leading SBA lender with strong presence in the Midwest and beyond.",
        "loan_types": ["7(a) Loans", "504 Loans", "SBA Express"],
        "website": "https://www.huntington.com/business/loans-and-lines-of-credit/sba-loans",
        "national": True
    }
]


US_STATES = [
    {"code": "AL", "name": "Alabama"},
    {"code": "AK", "name": "Alaska"},
    {"code": "AZ", "name": "Arizona"},
    {"code": "AR", "name": "Arkansas"},
    {"code": "CA", "name": "California"},
    {"code": "CO", "name": "Colorado"},
    {"code": "CT", "name": "Connecticut"},
    {"code": "DE", "name": "Delaware"},
    {"code": "FL", "name": "Florida"},
    {"code": "GA", "name": "Georgia"},
    {"code": "HI", "name": "Hawaii"},
    {"code": "ID", "name": "Idaho"},
    {"code": "IL", "name": "Illinois"},
    {"code": "IN", "name": "Indiana"},
    {"code": "IA", "name": "Iowa"},
    {"code": "KS", "name": "Kansas"},
    {"code": "KY", "name": "Kentucky"},
    {"code": "LA", "name": "Louisiana"},
    {"code": "ME", "name": "Maine"},
    {"code": "MD", "name": "Maryland"},
    {"code": "MA", "name": "Massachusetts"},
    {"code": "MI", "name": "Michigan"},
    {"code": "MN", "name": "Minnesota"},
    {"code": "MS", "name": "Mississippi"},
    {"code": "MO", "name": "Missouri"},
    {"code": "MT", "name": "Montana"},
    {"code": "NE", "name": "Nebraska"},
    {"code": "NV", "name": "Nevada"},
    {"code": "NH", "name": "New Hampshire"},
    {"code": "NJ", "name": "New Jersey"},
    {"code": "NM", "name": "New Mexico"},
    {"code": "NY", "name": "New York"},
    {"code": "NC", "name": "North Carolina"},
    {"code": "ND", "name": "North Dakota"},
    {"code": "OH", "name": "Ohio"},
    {"code": "OK", "name": "Oklahoma"},
    {"code": "OR", "name": "Oregon"},
    {"code": "PA", "name": "Pennsylvania"},
    {"code": "RI", "name": "Rhode Island"},
    {"code": "SC", "name": "South Carolina"},
    {"code": "SD", "name": "South Dakota"},
    {"code": "TN", "name": "Tennessee"},
    {"code": "TX", "name": "Texas"},
    {"code": "UT", "name": "Utah"},
    {"code": "VT", "name": "Vermont"},
    {"code": "VA", "name": "Virginia"},
    {"code": "WA", "name": "Washington"},
    {"code": "WV", "name": "West Virginia"},
    {"code": "WI", "name": "Wisconsin"},
    {"code": "WY", "name": "Wyoming"},
    {"code": "DC", "name": "District of Columbia"},
]


LOAN_CATEGORIES = [
    "SBA Lenders",
    "Export working capital",
    "International trade loans",
    "Microloans",
    "CDC/504 loans",
    "Disaster loans",
]


sba_service = SBAService()
