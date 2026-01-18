"""
Report Pricing Router
Endpoints for report pricing, purchases, and access checks
"""

import os
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta, timezone

from app.db.database import get_db


def validate_redirect_url(url: str, request: Request) -> bool:
    """Validate that redirect URLs are from trusted origins to prevent open redirect attacks."""
    if not url:
        return False
    
    parsed = urlparse(url)
    
    allowed_hosts = [
        request.headers.get("host", "").split(":")[0],
        "localhost",
        "127.0.0.1",
    ]
    
    replit_domain = os.getenv("REPLIT_DOMAINS", "").split(",")
    allowed_hosts.extend([d.strip() for d in replit_domain if d.strip()])
    
    if os.getenv("REPLIT_DEPLOYMENT"):
        allowed_hosts.append(f"{os.getenv('REPL_SLUG', '')}.{os.getenv('REPL_OWNER', '')}.repl.co")
    
    return parsed.netloc.split(":")[0] in allowed_hosts or parsed.netloc == ""


from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.purchased_report import PurchasedReport, PurchasedBundle, ConsultantLicense, PurchaseType, GuestReportPurchase
from app.core.dependencies import get_current_user, get_current_active_user, get_current_user_optional
from app.core.report_pricing import (
    REPORT_PRODUCTS,
    BUNDLES,
    ReportProductType,
    BundleType,
    get_pricing_summary,
    is_report_included_for_tier,
    get_report_price,
    get_bundle_price,
)
from app.services.stripe_service import stripe_service, get_stripe_client
from app.services.usage_service import usage_service
from app.services.entitlements import get_opportunity_entitlements
from app.services.audit import log_event

router = APIRouter(prefix="/report-pricing", tags=["Report Pricing"])


class PublicPricingResponse(BaseModel):
    """Public pricing data - no auth required"""
    reports: List[dict]
    bundles: List[dict]
    subscription_tiers: List[dict]


class ReportPricingResponse(BaseModel):
    reports: List[dict]
    bundles: List[dict]
    user_tier: Optional[str] = None
    purchased_reports: List[dict] = []
    has_consultant_license: bool = False


class ReportPurchaseRequest(BaseModel):
    opportunity_id: int
    report_type: str


class BundlePurchaseRequest(BaseModel):
    opportunity_id: int
    bundle_type: str


class PurchaseResponse(BaseModel):
    client_secret: str
    amount: int
    publishable_key: str


class ConfirmPurchaseRequest(BaseModel):
    payment_intent_id: str


SUBSCRIPTION_TIERS = [
    {
        "id": "explorer",
        "name": "Explorer",
        "price_cents": 0,
        "price_label": "Free",
        "description": "Try quality, pay for what you need",
        "access_window_days": 91,
        "features": [
            "Browse validated opportunities",
            "Layer 1 access (91+ days)",
            "FREE Feasibility Study per opportunity",
            "Pay-per-report execution tools",
        ],
    },
    {
        "id": "builder",
        "name": "Builder",
        "price_cents": 9900,
        "price_label": "$99/mo",
        "description": "Unlimited research, professional execution",
        "access_window_days": 31,
        "features": [
            "Layer 1 + 2 access (31+ days)",
            "Unlimited Layer 1 reports",
            "10 Layer 2 reports/month",
            "All Explorer features",
        ],
        "is_popular": True,
    },
    {
        "id": "scaler",
        "name": "Scaler",
        "price_cents": 49900,
        "price_label": "$499/mo",
        "description": "Move faster with deep intelligence",
        "access_window_days": 8,
        "features": [
            "Full Layer 1-3 access (8+ days)",
            "Unlimited Layer 1-2 reports",
            "5 Layer 3 execution packages/month",
            "Priority AI processing",
        ],
    },
    {
        "id": "enterprise",
        "name": "Enterprise",
        "price_cents": 250000,
        "price_label": "$2,500+/mo",
        "description": "First-mover advantage + unlimited execution",
        "access_window_days": 0,
        "features": [
            "Real-time opportunity access (0+ days)",
            "Unlimited all layers",
            "API access",
            "Dedicated support",
        ],
    },
]


@router.get("/public", response_model=PublicPricingResponse)
def get_public_pricing():
    """Get public pricing data - no authentication required"""
    pricing = get_pricing_summary()
    
    reports_with_details = []
    consultant_prices = {
        "feasibility_study": "$1,500-$15,000",
        "business_plan": "$3,000-$15,000",
        "financial_model": "$2,500-$10,000",
        "market_analysis": "$2,000-$8,000",
        "strategic_assessment": "$1,500-$5,000",
        "pestle_analysis": "$1,500-$5,000",
        "pitch_deck": "$2,000-$5,000",
    }
    
    for report in pricing["reports"]:
        report["consultant_price"] = consultant_prices.get(report["id"], "$1,500-$5,000")
        report["user_price"] = report["price"]
        report["is_included"] = False
        reports_with_details.append(report)
    
    bundles_with_details = []
    bundle_consultant_values = {
        "starter": "$8,500-$35,000",
        "professional": "$17,000-$98,000",
        "consultant_license": "$50,000-$250,000",
    }
    
    for bundle in pricing["bundles"]:
        bundle["consultant_value"] = bundle_consultant_values.get(bundle["id"], "$10,000+")
        bundles_with_details.append(bundle)
    
    return PublicPricingResponse(
        reports=reports_with_details,
        bundles=bundles_with_details,
        subscription_tiers=SUBSCRIPTION_TIERS,
    )


@router.get("/", response_model=ReportPricingResponse)
def get_report_pricing(
    opportunity_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get report pricing, user's tier, and purchased reports for opportunity"""
    subscription = usage_service.get_or_create_subscription(current_user, db)
    user_tier = subscription.tier.value if hasattr(subscription.tier, 'value') else str(subscription.tier)
    
    pricing = get_pricing_summary()
    
    for report in pricing["reports"]:
        report["is_included"] = is_report_included_for_tier(report["id"], user_tier)
        if report["is_included"]:
            report["user_price"] = 0
        else:
            report["user_price"] = report["price"]
    
    for bundle in pricing["bundles"]:
        bundle["is_available"] = True
    
    purchased_reports = []
    if opportunity_id:
        purchases = db.query(PurchasedReport).filter(
            PurchasedReport.user_id == current_user.id,
            PurchasedReport.opportunity_id == opportunity_id
        ).all()
        purchased_reports = [
            {
                "report_type": p.report_type,
                "purchased_at": p.purchased_at.isoformat() if p.purchased_at else None,
                "is_generated": p.is_generated,
            }
            for p in purchases
        ]
    
    has_consultant_license = db.query(ConsultantLicense).filter(
        ConsultantLicense.user_id == current_user.id,
        ConsultantLicense.is_active == True
    ).first() is not None
    
    return ReportPricingResponse(
        reports=pricing["reports"],
        bundles=pricing["bundles"],
        user_tier=user_tier,
        purchased_reports=purchased_reports,
        has_consultant_license=has_consultant_license,
    )


@router.get("/check-access/{opportunity_id}")
def check_report_access(
    opportunity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Check if user has Layer 1 access to opportunity (required for report purchase)"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    ent = get_opportunity_entitlements(db, opportunity, current_user)
    
    return {
        "opportunity_id": opportunity_id,
        "has_layer1_access": ent.is_accessible,
        "user_tier": ent.user_tier.value if ent.user_tier else "free",
        "can_purchase_reports": ent.is_accessible,
        "message": "Layer 1 access required to purchase reports" if not ent.is_accessible else "Ready to purchase reports"
    }


@router.post("/purchase-report", response_model=PurchaseResponse)
def create_report_purchase(
    purchase_data: ReportPurchaseRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a payment intent for report purchase"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == purchase_data.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    ent = get_opportunity_entitlements(db, opportunity, current_user)
    if not ent.is_accessible:
        raise HTTPException(
            status_code=403, 
            detail="Layer 1 access required. Unlock this opportunity first or upgrade your subscription."
        )
    
    if purchase_data.report_type not in REPORT_PRODUCTS:
        raise HTTPException(status_code=400, detail=f"Invalid report type: {purchase_data.report_type}")
    
    subscription = usage_service.get_or_create_subscription(current_user, db)
    user_tier = subscription.tier.value if hasattr(subscription.tier, 'value') else str(subscription.tier)
    
    if is_report_included_for_tier(purchase_data.report_type, user_tier):
        raise HTTPException(
            status_code=400, 
            detail=f"This report is included in your {user_tier} subscription. No purchase needed."
        )
    
    existing = db.query(PurchasedReport).filter(
        PurchasedReport.user_id == current_user.id,
        PurchasedReport.opportunity_id == purchase_data.opportunity_id,
        PurchasedReport.report_type == purchase_data.report_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already purchased this report for this opportunity")
    
    amount_cents = get_report_price(purchase_data.report_type)
    report_product = REPORT_PRODUCTS[purchase_data.report_type]
    
    if not subscription.stripe_customer_id:
        customer = stripe_service.create_customer(
            email=current_user.email,
            name=current_user.name,
            metadata={"user_id": current_user.id}
        )
        subscription.stripe_customer_id = customer.id
        db.commit()
    
    stripe_client = get_stripe_client()
    payment_intent = stripe_client.payment_intents.create(
        amount=amount_cents,
        currency="usd",
        customer=subscription.stripe_customer_id,
        metadata={
            "user_id": str(current_user.id),
            "opportunity_id": str(purchase_data.opportunity_id),
            "report_type": purchase_data.report_type,
            "payment_type": "report_purchase",
        },
        description=f"OppGrid Report: {report_product.name} for Opportunity #{purchase_data.opportunity_id}",
        automatic_payment_methods={"enabled": True},
    )
    
    log_event(
        db,
        action="report_pricing.purchase_intent_created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="opportunity",
        resource_id=purchase_data.opportunity_id,
        metadata={
            "payment_intent_id": payment_intent.id,
            "report_type": purchase_data.report_type,
            "amount_cents": amount_cents,
        },
    )
    
    from app.services.stripe_service import get_stripe_credentials
    _, publishable_key = get_stripe_credentials()
    
    return PurchaseResponse(
        client_secret=payment_intent.client_secret,
        amount=amount_cents,
        publishable_key=publishable_key,
    )


class ReportCheckoutRequest(BaseModel):
    opportunity_id: int
    report_type: str
    success_url: str
    cancel_url: str


class BundleCheckoutRequest(BaseModel):
    opportunity_id: int
    bundle_type: str
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    session_id: str
    url: str


@router.post("/checkout-report", response_model=CheckoutResponse)
def create_report_checkout(
    checkout_data: ReportCheckoutRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout session for report purchase"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == checkout_data.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    ent = get_opportunity_entitlements(db, opportunity, current_user)
    if not ent.is_accessible:
        raise HTTPException(
            status_code=403, 
            detail="Layer 1 access required. Unlock this opportunity first or upgrade your subscription."
        )
    
    if checkout_data.report_type not in REPORT_PRODUCTS:
        raise HTTPException(status_code=400, detail=f"Invalid report type: {checkout_data.report_type}")
    
    existing = db.query(PurchasedReport).filter(
        PurchasedReport.user_id == current_user.id,
        PurchasedReport.opportunity_id == checkout_data.opportunity_id,
        PurchasedReport.report_type == checkout_data.report_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already purchased this report for this opportunity")
    
    subscription = usage_service.get_or_create_subscription(current_user, db)
    report_product = REPORT_PRODUCTS[checkout_data.report_type]
    
    if is_report_included_for_tier(checkout_data.report_type, subscription.tier):
        raise HTTPException(status_code=400, detail="This report is included with your subscription. No purchase needed.")
    
    amount_cents = get_report_price(checkout_data.report_type, subscription.tier)
    if amount_cents <= 0:
        raise HTTPException(status_code=400, detail="Invalid price for this report")
    
    if not validate_redirect_url(checkout_data.success_url, request) or not validate_redirect_url(checkout_data.cancel_url, request):
        raise HTTPException(status_code=400, detail="Invalid redirect URL")
    
    stripe_client = get_stripe_client()
    
    session = stripe_client.checkout.Session.create(
        customer=subscription.stripe_customer_id,
        mode="payment",
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"OppGrid Report: {report_product.name}",
                    "description": f"AI-generated {report_product.name} for opportunity #{checkout_data.opportunity_id}",
                },
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        success_url=checkout_data.success_url,
        cancel_url=checkout_data.cancel_url,
        metadata={
            "user_id": str(current_user.id),
            "opportunity_id": str(checkout_data.opportunity_id),
            "report_type": checkout_data.report_type,
            "payment_type": "report_purchase",
        },
    )
    
    log_event(
        db,
        action="report_pricing.checkout_session_created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="opportunity",
        resource_id=checkout_data.opportunity_id,
        metadata={
            "session_id": session.id,
            "report_type": checkout_data.report_type,
            "amount_cents": amount_cents,
        },
    )
    
    return CheckoutResponse(session_id=session.id, url=session.url)


@router.post("/checkout-bundle", response_model=CheckoutResponse)
def create_bundle_checkout(
    checkout_data: BundleCheckoutRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout session for bundle purchase"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == checkout_data.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    ent = get_opportunity_entitlements(db, opportunity, current_user)
    if not ent.is_accessible:
        raise HTTPException(
            status_code=403, 
            detail="Layer 1 access required. Unlock this opportunity first or upgrade your subscription."
        )
    
    if checkout_data.bundle_type not in BUNDLES:
        raise HTTPException(status_code=400, detail=f"Invalid bundle type: {checkout_data.bundle_type}")
    
    existing = db.query(PurchasedBundle).filter(
        PurchasedBundle.user_id == current_user.id,
        PurchasedBundle.opportunity_id == checkout_data.opportunity_id,
        PurchasedBundle.bundle_type == checkout_data.bundle_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already purchased this bundle for this opportunity")
    
    subscription = usage_service.get_or_create_subscription(current_user, db)
    bundle = BUNDLES[checkout_data.bundle_type]
    
    amount_cents = get_bundle_price(checkout_data.bundle_type, subscription.tier)
    if amount_cents <= 0:
        raise HTTPException(status_code=400, detail="Invalid price for this bundle")
    
    if not validate_redirect_url(checkout_data.success_url, request) or not validate_redirect_url(checkout_data.cancel_url, request):
        raise HTTPException(status_code=400, detail="Invalid redirect URL")
    
    stripe_client = get_stripe_client()
    
    session = stripe_client.checkout.Session.create(
        customer=subscription.stripe_customer_id,
        mode="payment",
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"OppGrid Bundle: {bundle.name}",
                    "description": f"Includes: {', '.join(bundle.reports)}",
                },
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        success_url=checkout_data.success_url,
        cancel_url=checkout_data.cancel_url,
        metadata={
            "user_id": str(current_user.id),
            "opportunity_id": str(checkout_data.opportunity_id),
            "bundle_type": checkout_data.bundle_type,
            "payment_type": "bundle_purchase",
            "reports": ",".join(bundle.reports),
        },
    )
    
    log_event(
        db,
        action="report_pricing.bundle_checkout_session_created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="opportunity",
        resource_id=checkout_data.opportunity_id,
        metadata={
            "session_id": session.id,
            "bundle_type": checkout_data.bundle_type,
            "amount_cents": amount_cents,
        },
    )
    
    return CheckoutResponse(session_id=session.id, url=session.url)


class GuestCheckoutRequest(BaseModel):
    opportunity_id: int
    report_type: str
    email: str
    success_url: str
    cancel_url: str


class GuestBundleCheckoutRequest(BaseModel):
    opportunity_id: int
    bundle_type: str
    email: str
    success_url: str
    cancel_url: str


@router.post("/guest-checkout-report", response_model=CheckoutResponse)
def create_guest_report_checkout(
    checkout_data: GuestCheckoutRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout session for guest report purchase (no auth required)"""
    import secrets
    import re
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, checkout_data.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    opportunity = db.query(Opportunity).filter(Opportunity.id == checkout_data.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    if checkout_data.report_type not in REPORT_PRODUCTS:
        raise HTTPException(status_code=400, detail=f"Invalid report type: {checkout_data.report_type}")
    
    report_product = REPORT_PRODUCTS[checkout_data.report_type]
    amount_cents = report_product.price_cents
    
    if not validate_redirect_url(checkout_data.success_url, request) or not validate_redirect_url(checkout_data.cancel_url, request):
        raise HTTPException(status_code=400, detail="Invalid redirect URL")
    
    access_token = secrets.token_urlsafe(32)
    
    stripe_client = get_stripe_client()
    
    session = stripe_client.checkout.Session.create(
        customer_email=checkout_data.email,
        mode="payment",
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"OppGrid Report: {report_product.name}",
                    "description": f"AI-generated {report_product.name} for opportunity #{checkout_data.opportunity_id}",
                },
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        success_url=checkout_data.success_url,
        cancel_url=checkout_data.cancel_url,
        metadata={
            "guest_email": checkout_data.email,
            "opportunity_id": str(checkout_data.opportunity_id),
            "report_type": checkout_data.report_type,
            "payment_type": "guest_report_purchase",
            "access_token": access_token,
        },
    )
    
    log_event(
        db,
        action="report_pricing.guest_checkout_session_created",
        actor=None,
        actor_type="guest",
        request=request,
        resource_type="opportunity",
        resource_id=checkout_data.opportunity_id,
        metadata={
            "session_id": session.id,
            "report_type": checkout_data.report_type,
            "amount_cents": amount_cents,
            "guest_email": checkout_data.email[:3] + "***",
        },
    )
    
    return CheckoutResponse(session_id=session.id, url=session.url)


@router.post("/guest-checkout-bundle", response_model=CheckoutResponse)
def create_guest_bundle_checkout(
    checkout_data: GuestBundleCheckoutRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout session for guest bundle purchase (no auth required)"""
    import secrets
    import re
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, checkout_data.email):
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    opportunity = db.query(Opportunity).filter(Opportunity.id == checkout_data.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    if checkout_data.bundle_type not in BUNDLES:
        raise HTTPException(status_code=400, detail=f"Invalid bundle type: {checkout_data.bundle_type}")
    
    bundle = BUNDLES[checkout_data.bundle_type]
    amount_cents = bundle.price_cents
    
    if not validate_redirect_url(checkout_data.success_url, request) or not validate_redirect_url(checkout_data.cancel_url, request):
        raise HTTPException(status_code=400, detail="Invalid redirect URL")
    
    access_token = secrets.token_urlsafe(32)
    
    stripe_client = get_stripe_client()
    
    session = stripe_client.checkout.Session.create(
        customer_email=checkout_data.email,
        mode="payment",
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"OppGrid Bundle: {bundle.name}",
                    "description": f"Includes: {', '.join(bundle.reports)}",
                },
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        success_url=checkout_data.success_url,
        cancel_url=checkout_data.cancel_url,
        metadata={
            "guest_email": checkout_data.email,
            "opportunity_id": str(checkout_data.opportunity_id),
            "bundle_type": checkout_data.bundle_type,
            "payment_type": "guest_bundle_purchase",
            "reports": ",".join(bundle.reports),
            "access_token": access_token,
        },
    )
    
    log_event(
        db,
        action="report_pricing.guest_bundle_checkout_session_created",
        actor=None,
        actor_type="guest",
        request=request,
        resource_type="opportunity",
        resource_id=checkout_data.opportunity_id,
        metadata={
            "session_id": session.id,
            "bundle_type": checkout_data.bundle_type,
            "amount_cents": amount_cents,
            "guest_email": checkout_data.email[:3] + "***",
        },
    )
    
    return CheckoutResponse(session_id=session.id, url=session.url)


class StudioReportCheckoutRequest(BaseModel):
    """Request for standalone studio report checkout (no opportunity required)"""
    report_type: str  # market_analysis, strategic_assessment, pestle_analysis, business_plan, financial_model, pitch_deck
    success_url: str
    cancel_url: str
    email: Optional[str] = None  # Required for guest purchases
    report_context: Optional[dict] = None  # User-provided context for report generation


STUDIO_REPORT_PRICES = {
    "market_analysis": {"name": "Market Analysis", "price_cents": 9900},
    "strategic_assessment": {"name": "Strategic Assessment", "price_cents": 8900},
    "pestle_analysis": {"name": "PESTLE Analysis", "price_cents": 7900},
    "business_plan": {"name": "Business Plan", "price_cents": 14900},
    "financial_model": {"name": "Financial Model", "price_cents": 12900},
    "pitch_deck": {"name": "Pitch Deck", "price_cents": 7900},
}


@router.post("/studio-report-checkout", response_model=CheckoutResponse)
async def create_studio_report_checkout(
    checkout_data: StudioReportCheckoutRequest,
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout session for standalone studio report purchase (supports guest purchases)"""
    if checkout_data.report_type not in STUDIO_REPORT_PRICES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid report type: {checkout_data.report_type}. Valid types: {list(STUDIO_REPORT_PRICES.keys())}"
        )
    
    # Guest purchases require email
    if not current_user and not checkout_data.email:
        raise HTTPException(status_code=400, detail="Email is required for guest purchases")
    
    report_info = STUDIO_REPORT_PRICES[checkout_data.report_type]
    amount_cents = report_info["price_cents"]
    
    if not validate_redirect_url(checkout_data.success_url, request) or not validate_redirect_url(checkout_data.cancel_url, request):
        raise HTTPException(status_code=400, detail="Invalid redirect URL")
    
    stripe_client = get_stripe_client()
    
    # Build metadata based on whether user is authenticated
    metadata = {
        "report_type": checkout_data.report_type,
        "payment_type": "studio_report_purchase",
    }
    if current_user:
        metadata["user_id"] = str(current_user.id)
    if checkout_data.email:
        metadata["guest_email"] = checkout_data.email
    if checkout_data.report_context:
        import json
        metadata["report_context"] = json.dumps(checkout_data.report_context)[:500]
    
    session_params = {
        "payment_method_types": ["card"],
        "line_items": [{
            "price_data": {
                "currency": "usd",
                "unit_amount": amount_cents,
                "product_data": {
                    "name": f"OppGrid {report_info['name']}",
                    "description": f"AI-generated {report_info['name']} report",
                },
            },
            "quantity": 1,
        }],
        "mode": "payment",
        "success_url": checkout_data.success_url,
        "cancel_url": checkout_data.cancel_url,
        "metadata": metadata,
    }
    
    # Pre-fill email for guests
    if checkout_data.email and not current_user:
        session_params["customer_email"] = checkout_data.email
    
    session = stripe_client.checkout.Session.create(**session_params)
    
    log_event(
        db,
        action="report_pricing.studio_checkout_session_created",
        actor=current_user,
        actor_type="user" if current_user else "guest",
        request=request,
        resource_type="studio_report",
        resource_id=None,
        metadata={
            "session_id": session.id,
            "report_type": checkout_data.report_type,
            "amount_cents": amount_cents,
            "is_guest": current_user is None,
        },
    )
    
    return CheckoutResponse(session_id=session.id, url=session.url)


@router.post("/purchase-bundle", response_model=PurchaseResponse)
def create_bundle_purchase(
    purchase_data: BundlePurchaseRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a payment intent for bundle purchase"""
    opportunity = db.query(Opportunity).filter(Opportunity.id == purchase_data.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    ent = get_opportunity_entitlements(db, opportunity, current_user)
    if not ent.is_accessible:
        raise HTTPException(
            status_code=403, 
            detail="Layer 1 access required. Unlock this opportunity first or upgrade your subscription."
        )
    
    if purchase_data.bundle_type not in BUNDLES:
        raise HTTPException(status_code=400, detail=f"Invalid bundle type: {purchase_data.bundle_type}")
    
    existing = db.query(PurchasedBundle).filter(
        PurchasedBundle.user_id == current_user.id,
        PurchasedBundle.opportunity_id == purchase_data.opportunity_id,
        PurchasedBundle.bundle_type == purchase_data.bundle_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already purchased this bundle for this opportunity")
    
    bundle = BUNDLES[purchase_data.bundle_type]
    amount_cents = bundle.price_cents
    
    subscription = usage_service.get_or_create_subscription(current_user, db)
    if not subscription.stripe_customer_id:
        customer = stripe_service.create_customer(
            email=current_user.email,
            name=current_user.name,
            metadata={"user_id": current_user.id}
        )
        subscription.stripe_customer_id = customer.id
        db.commit()
    
    stripe_client = get_stripe_client()
    payment_intent = stripe_client.payment_intents.create(
        amount=amount_cents,
        currency="usd",
        customer=subscription.stripe_customer_id,
        metadata={
            "user_id": str(current_user.id),
            "opportunity_id": str(purchase_data.opportunity_id),
            "bundle_type": purchase_data.bundle_type,
            "payment_type": "bundle_purchase",
            "reports": ",".join(bundle.reports),
        },
        description=f"OppGrid Bundle: {bundle.name} for Opportunity #{purchase_data.opportunity_id}",
        automatic_payment_methods={"enabled": True},
    )
    
    log_event(
        db,
        action="report_pricing.bundle_intent_created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="opportunity",
        resource_id=purchase_data.opportunity_id,
        metadata={
            "payment_intent_id": payment_intent.id,
            "bundle_type": purchase_data.bundle_type,
            "amount_cents": amount_cents,
        },
    )
    
    from app.services.stripe_service import get_stripe_credentials
    _, publishable_key = get_stripe_credentials()
    
    return PurchaseResponse(
        client_secret=payment_intent.client_secret,
        amount=amount_cents,
        publishable_key=publishable_key,
    )


@router.post("/confirm-report-purchase")
def confirm_report_purchase(
    confirm_data: ConfirmPurchaseRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Confirm a successful report or bundle payment and grant access"""
    stripe_client = get_stripe_client()
    
    try:
        payment_intent = stripe_client.payment_intents.retrieve(confirm_data.payment_intent_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payment intent: {str(e)}")
    
    if payment_intent.status != "succeeded":
        raise HTTPException(status_code=400, detail=f"Payment not completed. Status: {payment_intent.status}")
    
    payment_type = payment_intent.metadata.get("payment_type")
    user_id = int(payment_intent.metadata.get("user_id", 0))
    opportunity_id = int(payment_intent.metadata.get("opportunity_id", 0))
    
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Payment belongs to another user")
    
    if payment_type == "report_purchase":
        report_type = payment_intent.metadata.get("report_type")
        
        existing = db.query(PurchasedReport).filter(
            PurchasedReport.user_id == current_user.id,
            PurchasedReport.opportunity_id == opportunity_id,
            PurchasedReport.report_type == report_type,
            PurchasedReport.stripe_payment_intent_id == confirm_data.payment_intent_id
        ).first()
        
        if existing:
            return {
                "success": True,
                "message": "Report already confirmed",
                "report_type": report_type,
                "opportunity_id": opportunity_id,
            }
        
        purchased = PurchasedReport(
            user_id=current_user.id,
            opportunity_id=opportunity_id,
            report_type=report_type,
            purchase_type=PurchaseType.INDIVIDUAL,
            amount_paid=payment_intent.amount,
            stripe_payment_intent_id=confirm_data.payment_intent_id,
        )
        db.add(purchased)
        db.commit()
        
        log_event(
            db,
            action="report_pricing.report_purchase_confirmed",
            actor=current_user,
            actor_type="user",
            request=request,
            resource_type="opportunity",
            resource_id=opportunity_id,
            metadata={
                "payment_intent_id": confirm_data.payment_intent_id,
                "report_type": report_type,
                "amount_cents": payment_intent.amount,
            },
        )
        
        return {
            "success": True,
            "message": f"Report '{report_type}' unlocked successfully",
            "report_type": report_type,
            "opportunity_id": opportunity_id,
        }
    
    elif payment_type == "bundle_purchase":
        bundle_type = payment_intent.metadata.get("bundle_type")
        reports_str = payment_intent.metadata.get("reports", "")
        reports = reports_str.split(",") if reports_str else []
        
        existing = db.query(PurchasedBundle).filter(
            PurchasedBundle.user_id == current_user.id,
            PurchasedBundle.opportunity_id == opportunity_id,
            PurchasedBundle.bundle_type == bundle_type,
            PurchasedBundle.stripe_payment_intent_id == confirm_data.payment_intent_id
        ).first()
        
        if existing:
            return {
                "success": True,
                "message": "Bundle already confirmed",
                "bundle_type": bundle_type,
                "opportunity_id": opportunity_id,
                "reports": reports,
            }
        
        bundle_record = PurchasedBundle(
            user_id=current_user.id,
            opportunity_id=opportunity_id,
            bundle_type=bundle_type,
            amount_paid=payment_intent.amount,
            stripe_payment_intent_id=confirm_data.payment_intent_id,
        )
        db.add(bundle_record)
        
        for report_type in reports:
            existing_report = db.query(PurchasedReport).filter(
                PurchasedReport.user_id == current_user.id,
                PurchasedReport.opportunity_id == opportunity_id,
                PurchasedReport.report_type == report_type
            ).first()
            
            if not existing_report:
                purchased = PurchasedReport(
                    user_id=current_user.id,
                    opportunity_id=opportunity_id,
                    report_type=report_type,
                    purchase_type=PurchaseType.BUNDLE,
                    bundle_id=bundle_type,
                    amount_paid=0,
                    stripe_payment_intent_id=confirm_data.payment_intent_id,
                )
                db.add(purchased)
        
        db.commit()
        
        log_event(
            db,
            action="report_pricing.bundle_purchase_confirmed",
            actor=current_user,
            actor_type="user",
            request=request,
            resource_type="opportunity",
            resource_id=opportunity_id,
            metadata={
                "payment_intent_id": confirm_data.payment_intent_id,
                "bundle_type": bundle_type,
                "reports": reports,
                "amount_cents": payment_intent.amount,
            },
        )
        
        return {
            "success": True,
            "message": f"Bundle '{bundle_type}' unlocked successfully",
            "bundle_type": bundle_type,
            "opportunity_id": opportunity_id,
            "reports": reports,
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid payment type")


@router.get("/my-purchases")
def get_my_purchases(
    opportunity_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get user's purchased reports"""
    query = db.query(PurchasedReport).filter(PurchasedReport.user_id == current_user.id)
    
    if opportunity_id:
        query = query.filter(PurchasedReport.opportunity_id == opportunity_id)
    
    purchases = query.order_by(PurchasedReport.purchased_at.desc()).all()
    
    return {
        "purchases": [
            {
                "id": p.id,
                "opportunity_id": p.opportunity_id,
                "report_type": p.report_type,
                "purchase_type": p.purchase_type.value if p.purchase_type else "individual",
                "bundle_id": p.bundle_id,
                "amount_paid": p.amount_paid,
                "is_generated": p.is_generated,
                "purchased_at": p.purchased_at.isoformat() if p.purchased_at else None,
            }
            for p in purchases
        ],
        "total": len(purchases),
    }


@router.get("/can-generate/{opportunity_id}/{report_type}")
def can_generate_report(
    opportunity_id: int,
    report_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Check if user can generate a specific report (included in tier or purchased)"""
    subscription = usage_service.get_or_create_subscription(current_user, db)
    user_tier = subscription.tier.value if hasattr(subscription.tier, 'value') else str(subscription.tier)
    
    if is_report_included_for_tier(report_type, user_tier):
        return {
            "can_generate": True,
            "reason": "included_in_tier",
            "user_tier": user_tier,
        }
    
    purchased = db.query(PurchasedReport).filter(
        PurchasedReport.user_id == current_user.id,
        PurchasedReport.opportunity_id == opportunity_id,
        PurchasedReport.report_type == report_type
    ).first()
    
    if purchased:
        return {
            "can_generate": True,
            "reason": "purchased",
            "purchased_at": purchased.purchased_at.isoformat() if purchased.purchased_at else None,
        }
    
    license_active = db.query(ConsultantLicense).filter(
        ConsultantLicense.user_id == current_user.id,
        ConsultantLicense.is_active == True
    ).first()
    
    if license_active and license_active.opportunities_used < license_active.max_opportunities:
        return {
            "can_generate": True,
            "reason": "consultant_license",
            "opportunities_remaining": license_active.max_opportunities - license_active.opportunities_used,
        }
    
    price = get_report_price(report_type)
    return {
        "can_generate": False,
        "reason": "purchase_required",
        "price": price,
        "price_formatted": f"${price / 100:.0f}",
    }
