import os
import replicate
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import uuid
import time
from replicate.exceptions import ModelError


load_dotenv()  # .env 読み込み

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

@app.post("/api/generate")
async def generate_image(image: UploadFile = File(...)):
    print("🔥 画像を受け取りました:", image.filename)
    # 一時保存
    temp_filename = f"temp_{uuid.uuid4().hex}.png"
    temp_path = f"./temp/{temp_filename}"
    os.makedirs("temp", exist_ok=True)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Replicate に画像を送る（例：SDXLのimg2img）
    try:
        output = replicate.run(
            "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
            input={
                "image": open(temp_path, "rb"),
                "prompt": "Without changing the person in the original photo, change the hairstyle and clothes to make them cool and stylish, safe for work",
                "strength": 0.7,
            }
        )
    except ModelError as e:
        if "NSFW" in str(e):
            print("⚠️ NSFW判定されました。1回だけ再実行します...")
            time.sleep(1)
            output = replicate.run(
                "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
                input={
                    "image": open(temp_path, "rb"),
                    "prompt": "a cool fashionable middle-aged man, fully clothed, wearing stylish outfit, realistic portrait, safe for work",
                    "strength": 0.7,
                }
            )   
        else:
            raise e  # 他のエラーならそのまま例外を出す
    

    # 🔽 ここで文字列（URL）だけ取り出す！
    # outputがリスト形式なら最初のURLを取得
    generated_url = str(output[0]) if isinstance(output, list) else str(output)

    # ↓ JSONResponseに入れるときは文字列にしておく
    return JSONResponse(content={
        "generated_image_url": generated_url,
        "fashion_info": "ジャケット：UNIQLO ¥5,990<br>パンツ：ZARA ¥6,800"
    })


##　テスト動作確認

# from fastapi import FastAPI, File, UploadFile
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# import shutil
# import os
# import uuid

# app = FastAPI()

# from fastapi.staticfiles import StaticFiles
# app.mount("/generated_images", StaticFiles(directory="generated_images"), name="generated_images")


# # CORS設定：Next.jsからのリクエスト許可
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 画像生成エンドポイント（仮）
# @app.post("/api/generate")
# async def generate_image(image: UploadFile = File(...)):
#     # 保存用のファイル名を生成
#     unique_filename = f"{uuid.uuid4().hex}.jpg"
#     save_path = f"./generated_images/{unique_filename}"

#     # 保存ディレクトリがなければ作成
#     os.makedirs(os.path.dirname(save_path), exist_ok=True)

#     # 画像を保存
#     with open(save_path, "wb") as buffer:
#         shutil.copyfileobj(image.file, buffer)

#     # 仮の返却データ（本番は生成画像とChatGPTファッション情報を入れる）
#     return JSONResponse(content={
#         "generated_image_url": f"http://localhost:8000/generated_images/{unique_filename}",
#         "fashion_info": "ジャケット：UNIQLO ¥5,990<br>パンツ：ZARA ¥6,800"
#     })


## 元のpracticalのapp.py

# from fastapi import FastAPI, HTTPException, Query
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import requests
# import json
# # from db_control import crud, mymodels
# from db_control import crud, mymodels
# # MySQLのテーブル作成
# # from db_control.create_tables import init_db

# # # アプリケーション初期化時にテーブルを作成
# # init_db()


# class Customer(BaseModel):
#     customer_id: str
#     customer_name: str
#     age: int
#     gender: str


# app = FastAPI()

# # CORSミドルウェアの設定
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/")
# def index():
#     return {"message": "FastAPI top page!"}


# @app.post("/customers")
# def create_customer(customer: Customer):
#     values = customer.dict()
#     tmp = crud.myinsert(mymodels.Customers, values)
#     result = crud.myselect(mymodels.Customers, values.get("customer_id"))

#     if result:
#         result_obj = json.loads(result)
#         return result_obj if result_obj else None
#     return None


# @app.get("/customers")
# def read_one_customer(customer_id: str = Query(...)):
#     result = crud.myselect(mymodels.Customers, customer_id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Customer not found")
#     result_obj = json.loads(result)
#     return result_obj[0] if result_obj else None

# @app.get("/allcustomers")
# def read_all_customer():
#     result = crud.myselectAll(mymodels.Customers)
#     # 結果がNoneの場合は空配列を返す
#     if not result:
#         return []
#     # JSON文字列をPythonオブジェクトに変換
#     return json.loads(result)


# @app.put("/customers")
# def update_customer(customer: Customer):
#     values = customer.dict()
#     values_original = values.copy()
#     tmp = crud.myupdate(mymodels.Customers, values)
#     result = crud.myselect(mymodels.Customers, values_original.get("customer_id"))
#     if not result:
#         raise HTTPException(status_code=404, detail="Customer not found")
#     result_obj = json.loads(result)
#     return result_obj[0] if result_obj else None


# @app.delete("/customers")
# def delete_customer(customer_id: str = Query(...)):
#     result = crud.mydelete(mymodels.Customers, customer_id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Customer not found")
#     return {"customer_id": customer_id, "status": "deleted"}


# @app.get("/fetchtest")
# def fetchtest():
#     response = requests.get('https://jsonplaceholder.typicode.com/users')
#     return response.json()
