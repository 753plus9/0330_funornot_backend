from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from db_control.connect_MySQL import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import text

import logging
import hashlib
# import uuid


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
            text("SELECT * FROM user WHERE email = :email AND password = :password"),
            {"email": user.email, "password": hashed_password}
        )
        user_data = result.mappings().fetchone()  # ←ここを変更！
        
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
    print("📥 受け取ったリクエスト:", user.dict())

    db: Session = SessionLocal()
    try:

        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        db.execute(
            text("INSERT INTO user (name, email, password, family_id) VALUES (:name, :email, :password, :family_id)"),
            {"name": user.name, "email": user.email, "password": hashed_password, "family_id": user.family_id}
        )
        db.commit()
        return {"message": "登録完了", "family_id": user.family_id}

    except IntegrityError:
        db.rollback()
        logging.error("登録エラー: メールアドレスが既に存在します")
        raise HTTPException(status_code=400, detail="このメールアドレスはすでに登録されています")
    
    except Exception as e:
        logging.error(f"登録エラー: {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="ユーザー登録失敗")
    finally:
        db.close()
