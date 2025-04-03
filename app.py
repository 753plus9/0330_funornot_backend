# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import generate,save

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")  # .env 読み込み

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

# ルーター登録（ここで他のルートもまとめて登録できるようにする）
app.include_router(generate.router)
app.include_router(save.router)