from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.utils import check_url_valid
from app.crud import get_url_by_short_path, log_click
from app.deps import get_db

router = APIRouter()


@router.get("/{short_path}", summary="Public redirect via a shortcut")
async def redirect_to_original(
    short_path: str, request: Request, db: Session = Depends(get_db)
):
    """
    Looking for an entry in the URL table by short_path.
    If not found - 404.
    If found, check validity (active and not expired).
    Logging the click (IP, User-Agent) and make RedirectResponse.
    """
    url_obj = get_url_by_short_path(db, short_path)
    if not url_obj:
        raise HTTPException(status_code=404, detail="Link not found.")
    check_url_valid(url_obj)

    # Logging the click
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    log_click(db, url_obj, visitor_ip=client_host, user_agent=user_agent)

    return RedirectResponse(url=url_obj.original_url)
