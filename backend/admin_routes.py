from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User

router = APIRouter(prefix="/admin", tags=["Admin"])


# ---------------------------
# DB Dependency
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# 📊 ADMIN DASHBOARD
# ---------------------------
@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db)):
    users = db.query(User).all()

    total_users = len(users)
    premium_users = len([u for u in users if u.subscription == "premium"])
    admin_users = len([u for u in users if u.role == "admin"])

    return {
        "summary": {
            "total_users": total_users,
            "premium_users": premium_users,
            "admin_users": admin_users
        },
        "users": [
            {
                "username": u.username,
                "role": u.role,
                "subscription": u.subscription
            }
            for u in users
        ]
    }


# ---------------------------
# 👥 VIEW ALL USERS
# ---------------------------
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return [
        {
            "username": user.username,
            "role": user.role,
            "subscription": user.subscription
        }
        for user in users
    ]


# ---------------------------
# 🔼 PROMOTE TO ADMIN
# ---------------------------
@router.post("/make-admin")
def make_admin(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = "admin"
    db.commit()

    return {"message": f"{username} promoted to admin"}


# ---------------------------
# 🔽 REMOVE ADMIN
# ---------------------------
@router.post("/remove-admin")
def remove_admin(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = "user"
    db.commit()

    return {"message": f"{username} downgraded to user"}


# ---------------------------
# 💳 MAKE PREMIUM
# ---------------------------
@router.post("/make-premium")
def make_premium(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.subscription = "premium"
    db.commit()

    return {"message": f"{username} upgraded to premium"}


# ---------------------------
# 🔄 REMOVE PREMIUM
# ---------------------------
@router.post("/remove-premium")
def remove_premium(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.subscription = "free"
    db.commit()

    return {"message": f"{username} downgraded to free plan"}