# routes/save.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from db_control import mymodels
from db_control.connect_MySQL import SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter()

class FashionItem(BaseModel):
    name: str
    brand: str
    price: str
    description: str

class SaveRequest(BaseModel):
    family_id: str
    before_url: str
    after_url: str
    fashion_items: List[FashionItem]

@router.post("/api/save")
def save_result(data: SaveRequest):
    db: Session = SessionLocal()
    try:
        # BeDandy提案テーブルに登録
        new_bedandy = mymodels.Bedandy(
            family_id=data.family_id,
            before_photourl=data.before_url,
            after_photourl=data.after_url,
            created_at=datetime.now()
        )
        db.add(new_bedandy)
        db.flush()
        # db.commit()
        # db.refresh(new_bedandy)  # bedandy_id を取得

        # item テーブルに登録し、中間テーブル bd_item にも登録
        for f in data.fashion_items:
            item = mymodels.Item(
                item_name=f.name,
                price=f.price,
                brand=f.brand,
                description=f.description
            )
            db.add(item)
            db.flush()
            # db.commit()
            # db.refresh(item)

            bd_item = mymodels.BdItem(
                bedandy_id=new_bedandy.bedandy_id,
                item_id=item.item_id
            )
            db.add(bd_item)
            
        db.commit()

        print(f"✅ 保存成功：bedandy_id={new_bedandy.bedandy_id}, items={len(data.fashion_items)}")
        return {"status": "success", "bedandy_id": new_bedandy.bedandy_id}
    except Exception as e:
        db.rollback()
        print("❌ 保存失敗:", e)
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()
