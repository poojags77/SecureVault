from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import User   # ✅ ONLY import, DO NOT redefine
from auth import hash_password, verify_password, create_token
import re

# 🔥 Import payment routes
from payment import router as payment_router

from admin_routes import router as admin_router



app = FastAPI()

# Register payment routes
app.include_router(payment_router)
app.include_router(admin_router)

# Create tables
Base.metadata.create_all(bind=engine)

# ---------------------------
# Database Dependency
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Password Strength Validation
# ---------------------------
def validate_password_strength(password: str):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

# ---------------------------
# Login Attempt Tracking
# ---------------------------
login_attempts = {}
MAX_ATTEMPTS = 5

# ---------------------------
# Register Endpoint
# ---------------------------
@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    if not validate_password_strength(password):
        raise HTTPException(
            status_code=400,
            detail="Password must be 8+ chars, include upper, lower, number, and special character"
        )

    hashed = hash_password(password)

    # 🔥 Explicit subscription assignment (recommended for clarity)
    user = User(
        username=username,
        password_hash=hashed,
        subscription="free"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully"}

# ---------------------------
# Login Endpoint
# ---------------------------
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):

    if username in login_attempts and login_attempts[username] >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=403,
            detail="Account temporarily locked due to multiple failed attempts"
        )

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        login_attempts[username] = login_attempts.get(username, 0) + 1
        raise HTTPException(status_code=401, detail="Invalid credentials")

    login_attempts[username] = 0

    token = create_token(username)

    return {"access_token": token}

# ---------------------------
# Profile Endpoint
# ---------------------------
@app.get("/profile")
def get_profile(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user.username,
        "role": user.role,
        "subscription": user.subscription
    }