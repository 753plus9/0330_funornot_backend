
import logging
import sys

# 標準出力にログを出す設定（Azureに出すために必要）
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import generate,save

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")  # .env 読み込み

# REPLICATE_TOKEN を環境変数から明示的にセット（これも重要！）
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if REPLICATE_API_TOKEN:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
    masked_token = REPLICATE_API_TOKEN[:4] + "..." + REPLICATE_API_TOKEN[-4:]

    logging.info("✅ Replicate API token has been set from environment.")
    logging.info(f"🔑 Replicate API token (masked): {masked_token}")

else:
    logging.warning("⚠️ Replicate API token is not set. Check environment variables.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000"],
    allow_origins=[
        "http://localhost:3000",
        "https://app-002-step3-2-node-oshima6.azurewebsites.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
# os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# ルーター登録（ここで他のルートもまとめて登録できるようにする）
app.include_router(generate.router)
app.include_router(save.router)