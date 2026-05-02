import re
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.admin_routes import router as admin_router
from backend.auth import create_token, get_current_username, hash_password, verify_password
from backend.database import Base, SessionLocal, engine
from backend.models import User
from backend.payment import router as payment_router

app = FastAPI(title="SecureVault API")

app.include_router(payment_router)
app.include_router(admin_router)

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


login_attempts = {}
MAX_ATTEMPTS = 5


@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists.")

    if not validate_password_strength(password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters and include uppercase, lowercase, number, and special character.",
        )

    user = User(
        username=username,
        password_hash=hash_password(password),
        subscription="free",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully."}


@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    if username in login_attempts and login_attempts[username] >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=403,
            detail="Account temporarily locked after multiple failed login attempts.",
        )

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        login_attempts[username] = login_attempts.get(username, 0) + 1
        raise HTTPException(status_code=401, detail="Invalid credentials. Please try again.")

    login_attempts[username] = 0

    return {"access_token": create_token(username), "token_type": "bearer"}


@app.get("/profile")
def get_profile(
    current_username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == current_username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "username": user.username,
        "role": user.role,
        "subscription": user.subscription,
    }


@app.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == current_username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    if not validate_password_strength(new_password):
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 8 characters and include uppercase, lowercase, number, and special character.",
        )

    user.password_hash = hash_password(new_password)
    db.commit()
    login_attempts[current_username] = 0

    return {"message": "Password changed successfully."}


@app.get("/", include_in_schema=False)
def web_app():
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend files not found.")
    return FileResponse(index_file)
