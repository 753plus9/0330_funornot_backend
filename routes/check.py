# routes/check.py

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from db_control.connect_MySQL import SessionLocal
from db_control.mymodels import Bedandy, Message,Item,BdItem
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/check_by_family/{family_id}")
def get_check_data_by_family(family_id: str):
    session: Session = SessionLocal()
    try:
         # ✅ Bedandyテーブルの中から最新のcreated_atのレコードを取得
        bedandy_record = (
            session.query(Bedandy)
            .filter(Bedandy.family_id == family_id)
            .order_by(Bedandy.created_at.desc())
            .first()
        )
        if not bedandy_record:
            raise HTTPException(status_code=404, detail="BeDandy record not found")

        # ✅ Messageテーブルの中からbedandy_idに紐づく最新のsent_atのレコードを取得
        message_record = (
            session.query(Message)
            .filter(Message.bedandy_id == bedandy_record.bedandy_id)
            .order_by(Message.sent_at.desc())
            .first()
        )
        message_text = message_record.message_text if message_record else ""

        # ✅ BdItem → Item の関連データ取得
        bd_items = (
            session.query(Item)
            .join(BdItem, Item.item_id == BdItem.item_id)
            .filter(BdItem.bedandy_id == bedandy_record.bedandy_id)
            .all()
        )

        # fashion_items を辞書形式に変換
        fashion_items = [
            {
                "name": item.item_name,
                "brand": item.brand,
                "price": item.price,
                "description": item.description,
            }
            for item in bd_items
        ]

        return {
            "status": "success",
            "before_url": bedandy_record.before_photourl,
            "after_url": bedandy_record.after_photourl,  # ← ✅ これを追加！
            "message": message_text,
            "fashion_items": fashion_items,  # ← これを追加

        }
    finally:
        session.close()
