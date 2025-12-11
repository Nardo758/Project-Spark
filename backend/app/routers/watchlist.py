from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.db.database import get_db
from app.models.watchlist import WatchlistItem
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.watchlist import WatchlistItemCreate, WatchlistItem as WatchlistItemSchema
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=WatchlistItemSchema, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    watchlist_data: WatchlistItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add an opportunity to user's watchlist"""
    # Check if opportunity exists
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == watchlist_data.opportunity_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    # Create watchlist item
    new_item = WatchlistItem(
        user_id=current_user.id,
        opportunity_id=watchlist_data.opportunity_id
    )

    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        return new_item

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This opportunity is already in your watchlist"
        )


@router.delete("/{watchlist_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    watchlist_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove an opportunity from user's watchlist"""
    watchlist_item = db.query(WatchlistItem).filter(
        WatchlistItem.id == watchlist_item_id,
        WatchlistItem.user_id == current_user.id
    ).first()

    if not watchlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found"
        )

    db.delete(watchlist_item)
    db.commit()

    return None


@router.delete("/opportunity/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist_by_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove an opportunity from watchlist by opportunity ID"""
    watchlist_item = db.query(WatchlistItem).filter(
        WatchlistItem.opportunity_id == opportunity_id,
        WatchlistItem.user_id == current_user.id
    ).first()

    if not watchlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not in watchlist"
        )

    db.delete(watchlist_item)
    db.commit()

    return None


@router.get("/", response_model=List[WatchlistItemSchema])
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all opportunities in user's watchlist"""
    watchlist_items = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == current_user.id
    ).order_by(WatchlistItem.created_at.desc()).all()

    return watchlist_items


@router.get("/check/{opportunity_id}")
def check_in_watchlist(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if an opportunity is in user's watchlist"""
    watchlist_item = db.query(WatchlistItem).filter(
        WatchlistItem.opportunity_id == opportunity_id,
        WatchlistItem.user_id == current_user.id
    ).first()

    return {
        "in_watchlist": watchlist_item is not None,
        "watchlist_item_id": watchlist_item.id if watchlist_item else None
    }
