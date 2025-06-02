from datetime import datetime

from fastapi import HTTPException, status

from app.models import URL


def check_url_valid(url: URL) -> None:
    """Checks if the link is active and has not expired.
    If invalid, it throws HTTPException."""
    if not url.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Link deactivated."
        )
    if url.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE, detail="The link is outdated."
        )
