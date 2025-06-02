from datetime import datetime

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models import URL


def main():
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        expired = (
            db.query(URL).filter(URL.expires_at < now, URL.is_active == True).all()
        )
        for url in expired:
            url.is_active = False
        db.commit()
        print(f"Set inactive: {len(expired)} links")
    finally:
        db.close()


if __name__ == "__main__":
    main()
