from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from open_webui.models.feedbacks import (
    FeedbackIdResponse,
    FeedbackModel,
    FeedbackResponse,
    FeedbackForm,
    FeedbackUserResponse,
    FeedbackListResponse,
    LeaderboardFeedbackData,
    Feedbacks,
)

from open_webui.constants import ERROR_MESSAGES
from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.internal.db import get_session
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)


router = APIRouter()


############################
# Reviews
############################


class ReviewEntry(BaseModel):
    model_id: str
    score: float  # final confidence-weighted score (0-1)
    total: int  # N
    positive: int  # thumbs up count
    negative: int  # thumbs down count


class ReviewsResponse(BaseModel):
    entries: list[ReviewEntry]


def _calculate_reviews(feedbacks: list[LeaderboardFeedbackData]) -> list[ReviewEntry]:
    """
    Calculate review scores for models using Jeffreys-smoothed positivity
    with confidence weighting.

    Each feedback with rating="1" counts as positive, rating="-1" as negative.
    Works with single-model feedback (thumbs up/down on individual responses).

    Formula:
        smoothed = (pos + 0.5) / (N + 1)
        final    = (N / (N + k)) * smoothed + (k / (N + k)) * 0.5
    where k=10.
    """
    K = 10
    model_counts: dict[str, dict] = {}

    for feedback in feedbacks:
        data = feedback.data or {}
        model_id = data.get("model_id")
        rating_value = str(data.get("rating", ""))
        if not model_id or rating_value not in ("1", "-1"):
            continue

        if model_id not in model_counts:
            model_counts[model_id] = {"positive": 0, "negative": 0}

        if rating_value == "1":
            model_counts[model_id]["positive"] += 1
        else:
            model_counts[model_id]["negative"] += 1

    entries = []
    for model_id, counts in model_counts.items():
        pos = counts["positive"]
        neg = counts["negative"]
        N = pos + neg

        smoothed = (pos + 0.5) / (N + 1)
        score = (N / (N + K)) * smoothed + (K / (N + K)) * 0.5

        entries.append(
            ReviewEntry(
                model_id=model_id,
                score=round(score, 4),
                total=N,
                positive=pos,
                negative=neg,
            )
        )

    entries.sort(key=lambda e: e.score, reverse=True)
    return entries


@router.get("/reviews", response_model=ReviewsResponse)
async def get_reviews(
    user=Depends(get_admin_user),
    db: Session = Depends(get_session),
):
    """Get model reviews ranked by positive/negative feedback with confidence weighting."""
    feedbacks = Feedbacks.get_feedbacks_for_reviews(db=db)
    entries = _calculate_reviews(feedbacks)
    return ReviewsResponse(entries=entries)


############################
# Feedback CRUD
############################


@router.get("/feedbacks/all", response_model=list[FeedbackResponse])
async def get_all_feedbacks(
    user=Depends(get_admin_user), db: Session = Depends(get_session)
):
    feedbacks = Feedbacks.get_all_feedbacks(db=db)
    return feedbacks


@router.get("/feedbacks/all/ids", response_model=list[FeedbackIdResponse])
async def get_all_feedback_ids(
    user=Depends(get_admin_user), db: Session = Depends(get_session)
):
    return Feedbacks.get_all_feedback_ids(db=db)


@router.delete("/feedbacks/all")
async def delete_all_feedbacks(
    user=Depends(get_admin_user), db: Session = Depends(get_session)
):
    success = Feedbacks.delete_all_feedbacks(db=db)
    return success


@router.get("/feedbacks/all/export", response_model=list[FeedbackModel])
async def export_all_feedbacks(
    user=Depends(get_admin_user), db: Session = Depends(get_session)
):
    feedbacks = Feedbacks.get_all_feedbacks(db=db)
    return feedbacks


@router.get("/feedbacks/user", response_model=list[FeedbackUserResponse])
async def get_user_feedbacks(
    user=Depends(get_verified_user), db: Session = Depends(get_session)
):
    feedbacks = Feedbacks.get_feedbacks_by_user_id(user.id, db=db)
    return feedbacks


@router.delete("/feedbacks", response_model=bool)
async def delete_user_feedbacks(
    user=Depends(get_verified_user), db: Session = Depends(get_session)
):
    success = Feedbacks.delete_feedbacks_by_user_id(user.id, db=db)
    return success


PAGE_ITEM_COUNT = 30


@router.get("/feedbacks/list", response_model=FeedbackListResponse)
async def get_feedback_list(
    order_by: Optional[str] = None,
    direction: Optional[str] = None,
    page: Optional[int] = 1,
    user=Depends(get_admin_user),
    db: Session = Depends(get_session),
):
    limit = PAGE_ITEM_COUNT

    page = max(1, page)
    skip = (page - 1) * limit

    filter = {}
    if order_by:
        filter["order_by"] = order_by
    if direction:
        filter["direction"] = direction

    result = Feedbacks.get_feedback_items(filter=filter, skip=skip, limit=limit, db=db)
    return result


@router.post("/feedback", response_model=FeedbackModel)
async def create_feedback(
    form_data: FeedbackForm,
    user=Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    feedback = Feedbacks.insert_new_feedback(
        user_id=user.id, form_data=form_data, db=db
    )
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.DEFAULT(),
        )

    return feedback


@router.get("/feedback/{id}", response_model=FeedbackModel)
async def get_feedback_by_id(
    id: str, user=Depends(get_verified_user), db: Session = Depends(get_session)
):
    if user.role == "admin":
        feedback = Feedbacks.get_feedback_by_id(id=id, db=db)
    else:
        feedback = Feedbacks.get_feedback_by_id_and_user_id(
            id=id, user_id=user.id, db=db
        )

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    return feedback


@router.post("/feedback/{id}", response_model=FeedbackModel)
async def update_feedback_by_id(
    id: str,
    form_data: FeedbackForm,
    user=Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    if user.role == "admin":
        feedback = Feedbacks.update_feedback_by_id(id=id, form_data=form_data, db=db)
    else:
        feedback = Feedbacks.update_feedback_by_id_and_user_id(
            id=id, user_id=user.id, form_data=form_data, db=db
        )

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    return feedback


@router.delete("/feedback/{id}")
async def delete_feedback_by_id(
    id: str, user=Depends(get_verified_user), db: Session = Depends(get_session)
):
    if user.role == "admin":
        success = Feedbacks.delete_feedback_by_id(id=id, db=db)
    else:
        success = Feedbacks.delete_feedback_by_id_and_user_id(
            id=id, user_id=user.id, db=db
        )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.NOT_FOUND
        )

    return success
