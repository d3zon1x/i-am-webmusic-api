import asyncio
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from app.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, UserResponse, PasswordResetRequest, PasswordReset
from app.services.auth_service import create_user, authenticate_user, create_access_token, decode_access_token, \
    create_activation_token, decode_activation_token, generate_reset_token, reset_password
from app.services.token_service import get_current_user
from app.utils.email_utils import send_email, get_password_reset_template
from fastapi import BackgroundTasks


router = APIRouter(tags=["Auth"])

class UserLogin(BaseModel):
    email: str
    password: str
    remember_me: bool = False  # 👈 додай це

@router.post("/register", response_model=UserOut)
def register(background_tasks: BackgroundTasks, user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user)

    activation_token = create_activation_token(db_user.email)


    print(f"Activate your account: http://localhost:8000/api/activate/{activation_token}")
    activation_link = f"http://localhost:8000/api/activate/{activation_token}"
    subject = "Activate your account"
    body = f"Hello {db_user.username},\n\nPlease activate your account:\n{activation_link}"

    background_tasks.add_task(send_email, db_user.email, "IAMWEBMUSIC account activation", activation_link)
    return db_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    auth_user = authenticate_user(db, user.email, user.password)
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Якщо remember_me → 30 днів, інакше сесія
    max_age = 60 * 60 * 24 * 30 if user.remember_me else None

    access_token = create_access_token(data={"sub": auth_user.email})

    response = JSONResponse(content={"message": "Logged in"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=max_age,       # 👈 тут магія
        samesite="Lax",
        secure=False           # продакшн → True
    )
    return response



@router.get("/me", response_model=UserOut)
def get_me(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        email = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token")
    return response

@router.get("/activate/{token}")
def activate_account(token: str, db: Session = Depends(get_db)):
    try:
        email = decode_access_token(token)
    except HTTPException as e:
        raise HTTPException(status_code=400, detail="Invalid or expired activation link")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active:
        return {"message": "Account already activated"}

    user.is_active = True
    db.commit()

    return RedirectResponse(url="http://localhost:5173")  # ⚡ сюди редірект


@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"detail": f"User {user.email} deleted"}

@router.post("/forgot-password")
def forgot_password(request_data: PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = generate_reset_token(user.email)
    reset_link = f"http://localhost:5173/reset-password?token={token}"
    subject = "Reset your password"
    html = get_password_reset_template(reset_link)

    background_tasks.add_task(send_email, user.email, subject, html)
    return {"message": "Password reset link sent"}

@router.post("/reset-password")
def reset_password_route(data: PasswordReset, db: Session = Depends(get_db)):
    reset_password(data.token, data.new_password, db)
    return {"message": "Password successfully updated"}