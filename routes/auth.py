from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from db_control.connect_MySQL import SessionLocal
from sqlalchemy.orm import Session
import logging
import hashlib

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(UserLogin):
    name: str
    family_id: str

@router.post("/api/login")
def login(user: UserLogin, request: Request):
    db: Session = SessionLocal()
    try:
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        result = db.execute(
            "SELECT * FROM user WHERE email=%s AND password=%s",
            (user.email, hashed_password)
        )
        user_data = result.fetchone()
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {
            "id": user_data["id"],
            "email": user_data["email"],
            "family_id": user_data["family_id"]
        }
    except Exception as e:
        logging.error(f"ログインエラー: {e}")
        raise HTTPException(status_code=500, detail="ログインに失敗しました")
    finally:
        db.close()

@router.post("/api/register")
def register(user: UserRegister):
    db: Session = SessionLocal()
    try:
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        db.execute(
            "INSERT INTO user (name, email, password, family_id) VALUES (%s, %s, %s, %s)",
            (user.name, user.email, hashed_password, user.family_id)
        )
        db.commit()
        return {"message": "登録完了"}
    except Exception as e:
        logging.error(f"登録エラー: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="ユーザー登録失敗")
    finally:
        db.close()
