from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.security import get_current_user
from app.deps import get_db

router = APIRouter()


# --- Creating a new short link ---
@router.post(
    "/urls/",
    response_model=schemas.URLRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new short link",
)
def create_short_url(
    url_in: schemas.URLCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Creates a short link.
    If expire_seconds is not passed in the request, settings.ACCESS_TOKEN_EXPIRE_SECONDS is taken.
    """
    url_obj = crud.create_url(
        db=db,
        owner_id=current_user.id,
        original_url=url_in.original_url,
        expire_seconds=url_in.expire_seconds,
    )
    return url_obj


# --- List of user links ---
@router.get(
    "/urls/",
    response_model=List[schemas.URLRead],
    summary="Get a list of your own short links",
)
def read_own_urls(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    urls = crud.list_urls(db, owner_id=current_user.id)
    return urls


# --- Deactivating a link ---
@router.patch(
    "/urls/{url_id}/deactivate",
    response_model=schemas.URLRead,
    summary="Deactivate the link (do not physically remove it)",
)
def deactivate_url(
    url_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    db_url = crud.deactivate_url(db, url_id=url_id, owner_id=current_user.id)
    if not db_url:
        raise HTTPException(status_code=404, detail="Link not found")
    return db_url


# --- Obtaining statistics on links ---
@router.get(
    "/stats/",
    response_model=List[schemas.URLWithStats],
    summary="Get statistics on your own links",
)
def get_statistics(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    stats = crud.get_url_stats(db, owner_id=current_user.id)
    results = []
    for row in stats:
        results.append(
            {
                "id": row.id,
                "short_path": row.short_path,
                "original_url": row.original_url,
                "is_active": row.is_active,
                "expires_at": row.expires_at,
                "total_clicks": row.total_clicks,
                "last_clicked_at": row.last_clicked_at,
            }
        )
    return results
