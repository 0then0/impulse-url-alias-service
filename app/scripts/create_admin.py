import getpass

from sqlalchemy.orm import Session

from app.core.db import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import User


def main():
    # Make sure that the users table already exists
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        username = input("Enter a user name: ").strip()
        password = getpass.getpass("Enter password: ").strip()
        password_confirm = getpass.getpass("Confirm the password: ").strip()
        if password != password_confirm:
            print("The passwords don't match. Exit.")
            return
        hashed = hash_password(password)
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print("A user with this name already exists.")
            return
        user = User(username=username, password_hash=hashed, is_active=True)
        db.add(user)
        db.commit()
        print(f"The user '{username}' has been successfully created.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
