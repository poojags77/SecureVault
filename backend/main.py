from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import User
from auth import hash_password, verify_password, create_token
import re

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password Strength Validation
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

# Login Attempt Tracking
login_attempts = {}
MAX_ATTEMPTS = 5

# Register Endpoint
@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):

    # Check if username exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Enforce strong password
    if not validate_password_strength(password):
        raise HTTPException(
            status_code=400,
            detail="Password must be 8+ chars, include upper, lower, number, and special character"
        )

    # Hash password
    hashed = hash_password(password)

    # Create user
    user = User(username=username, password_hash=hashed)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully"}

# Login Endpoint
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):

    # Check lockout
    if username in login_attempts and login_attempts[username] >= MAX_ATTEMPTS:
        raise HTTPException(status_code=403, detail="Account temporarily locked due to multiple failed attempts")

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        login_attempts[username] = login_attempts.get(username, 0) + 1
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Reset attempts on successful login
    login_attempts[username] = 0

    token = create_token(username)

    return {"access_token": token}