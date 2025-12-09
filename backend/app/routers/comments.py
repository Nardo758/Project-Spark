from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.comment import Comment
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, Comment as CommentSchema
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new comment on an opportunity"""
    # Check if opportunity exists
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == comment_data.opportunity_id
    ).first()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    new_comment = Comment(
        content=comment_data.content,
        user_id=current_user.id,
        opportunity_id=comment_data.opportunity_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.get("/opportunity/{opportunity_id}", response_model=List[CommentSchema])
def get_opportunity_comments(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    """Get all comments for an opportunity"""
    comments = db.query(Comment).filter(
        Comment.opportunity_id == opportunity_id
    ).order_by(Comment.created_at.desc()).all()

    return comments


@router.put("/{comment_id}", response_model=CommentSchema)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a comment (only by author)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Check if user is the author
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment"
        )

    comment.content = comment_data.content
    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a comment (only by author)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    # Check if user is the author
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )

    db.delete(comment)
    db.commit()

    return None


@router.post("/{comment_id}/like", response_model=CommentSchema)
def like_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Like a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    comment.likes += 1
    db.commit()
    db.refresh(comment)

    return comment
