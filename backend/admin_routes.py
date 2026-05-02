from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth import get_current_username
from backend.database import SessionLocal
from backend.models import User

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_admin(
    current_username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == current_username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access is required.")

    return user


@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    users = db.query(User).all()

    return {
        "summary": {
            "total_users": len(users),
            "premium_users": len([u for u in users if u.subscription == "premium"]),
            "admin_users": len([u for u in users if u.role == "admin"]),
        },
        "users": [
            {
                "username": u.username,
                "role": u.role,
                "subscription": u.subscription,
            }
            for u in users
        ],
    }


@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    users = db.query(User).all()

    return [
        {
            "username": user.username,
            "role": user.role,
            "subscription": user.subscription,
        }
        for user in users
    ]


@router.post("/make-admin")
def make_admin(
    username: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.role = "admin"
    db.commit()

    return {"message": f"{username} promoted to admin."}


@router.post("/remove-admin")
def remove_admin(
    username: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.username == current_admin.username:
        raise HTTPException(status_code=400, detail="You cannot remove your own admin role.")

    user.role = "user"
    db.commit()

    return {"message": f"{username} downgraded to user."}


@router.post("/make-premium")
def make_premium(
    username: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.subscription = "premium"
    db.commit()

    return {"message": f"{username} upgraded to premium."}


@router.post("/remove-premium")
def remove_premium(
    username: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.subscription = "free"
    db.commit()

    return {"message": f"{username} downgraded to free plan."}
