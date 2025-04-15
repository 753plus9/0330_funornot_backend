# backend/routers/submit.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime
import logging

from db_control.connect_MySQL import SessionLocal
from db_control.mymodels import Bedandy, Message

router = APIRouter()
# router = APIRouter(prefix="/api")

# データベースセッションを取得する依存関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 受け取るJSONの構造を定義
class SendMessageRequest(BaseModel):
    family_id: str
    message: str
    before_url: Optional[str] = None
    after_url: Optional[str] = None

@router.post("/api/sendMessage")
async def send_message(payload: SendMessageRequest, db: Session = Depends(get_db)):
    print("✅ /api/sendMessage が呼ばれました:", payload.dict())

    try:
        # 該当 family_id の最新の Bedandy レコードを取得
        latest_bedandy = (
            db.query(Bedandy)
            .filter(Bedandy.family_id == payload.family_id)
            .order_by(Bedandy.created_at.desc())
            .first()
        )

        if not latest_bedandy:
            logging.warning(f"❌ family_id {payload.family_id} に該当する BeDandy が見つかりません")
            raise HTTPException(status_code=404, detail="BeDandy レコードが存在しません")

        # Message レコードの作成（テーブル構成に対応）
        new_message = Message(
            bedandy_id=latest_bedandy.bedandy_id,
            message_text=payload.message,
            sent_at=datetime.datetime.utcnow()
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        print("✅ Message 登録完了:", new_message.message_id)
        return {"status": "success", "message_id": new_message.message_id}

    except Exception as e:
        db.rollback()
        print(f"❌ 送信エラー発生: {str(e)}")  # ← エラー内容を出す
        raise HTTPException(status_code=500, detail=f"送信エラー: {str(e)}")

# @router.post("/sendMessage")
# async def send_message(payload: SendMessageRequest, db: Session = Depends(get_db)):
#     try:
#         # Bedandyレコードの作成
#         # new_bedandy = Bedandy(
#         #     family_id=payload.family_id,
#         #     before_photourl=payload.before_url,
#         #     after_photourl=payload.after_url,
#         #     created_at=datetime.datetime.utcnow()
#         # )
#         # db.add(new_bedandy)
#         # db.commit()
#         # db.refresh(new_bedandy)

#         # Messageレコードの作成
#         new_message = Message(
#             bedandy_id=new_bedandy.bedandy_id,
#             message_text=payload.message,
#             sent_at=datetime.datetime.utcnow()
#         )
#         db.add(new_message)
#         db.commit()
#         db.refresh(new_message)

#         return {"status": "success", "message_id": new_message.message_id}
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"送信エラー: {str(e)}")
# backend/routers/submit.py （追記）

# from typing import List

# # メッセージ取得API（GET）
# @router.get("/messages/{family_id}")
# async def get_messages(family_id: str, db: Session = Depends(get_db)):
#     try:
#         # Bedandyレコードを取得
#         bedandies = db.query(Bedandy).filter(Bedandy.family_id == family_id).all()
#         messages = []
#         for bedandy in bedandies:
#             for message in bedandy.messages:
#                 messages.append({
#                     "message_id": message.message_id,
#                     "message_text": message.message_text,
#                     "sent_at": message.sent_at,
#                     "before_url": bedandy.before_photourl,
#                     "after_url": bedandy.after_photourl
#                 })
#         # sent_atで降順にソート
#         messages.sort(key=lambda x: x["sent_at"], reverse=True)
#         return {"messages": messages}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"取得エラー: {str(e)}")