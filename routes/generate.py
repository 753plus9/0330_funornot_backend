# backend/routes/generate.py
import os
import shutil
import uuid
import time
import io
import logging


from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from replicate.exceptions import ModelError
from routes.fashion_service import generate_fashion_description
from utils.upload_to_blob import upload_image_to_blob  # ← 追加！
import replicate

# グローバルにログレベル設定
logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post("/api/generate")
async def generate_image(image: UploadFile = File(...)):
    print("🔥 画像を受け取りました（print）:", image.filename)
    logging.info(f"🔥 画像を受け取りました（logging）: {image.filename}")

    try:

        # Azure Blobにアップロードしつつ、image_bytes を取得
        blob_url, image_bytes = await upload_image_to_blob(image)
        print("📤 Blob URL（print）:", blob_url)
        logging.info(f"📤 Blob URL（logging）: {blob_url}")

    except Exception as e:
        logging.error(f"💥 Blobアップロードでエラー（logging）: {e}")
        return JSONResponse(content={"error": "Blob upload failed"}, status_code=500)

    # Replicateに画像（bytes）を渡す（BytesIOで包む）
    image_io = io.BytesIO(image_bytes)   
    
    # temp_filename = f"temp_{uuid.uuid4().hex}.png"
    # temp_path = f"./temp/{temp_filename}"
    # os.makedirs("temp", exist_ok=True)
    # with open(temp_path, "wb") as buffer:
    #     shutil.copyfileobj(image.file, buffer)

    try:
        output = replicate.run(
            "stability-ai/stable-diffusion-3.5-large",
            input={
                "image": blob_url,  # ← open() ではなく URL
                # "image": open(temp_path, "rb"),
                "prompt": "A highly realistic, photorealistic image of the Japanese man as in the original photo. Keep the face, hair, and body shape exactly the same and maintain natural skin texture. Focus on changing only the clothing to a stylish, modern outfit with high-quality fabric and a well-fitted design. Preserve a natural pose and lighting, ensuring the result looks like a genuine photograph of the same person.",
                "strength": 0.85,
            }
        )
        logging.info("🧠 Replicate 呼び出し成功（logging）")

    # try:
    #     output = replicate.run(
    #         "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
    #         input={
    #             "image": open(temp_path, "rb"),
    #             "prompt": "Without changing the person in the original photo, change the hairstyle and clothes to make them cool and stylish, safe for work",
    #             "strength": 0.7,
    #         }
    #     )
    except ModelError as e:
        logging.error(f"💥 Replicate呼び出しエラー: {e}")

        if "NSFW" in str(e):
            print("⚠️ NSFW判定されたので再実行")
            time.sleep(1)
            image_io.seek(0)  # ← 重要！読み直す準備

            output = replicate.run(
                "stability-ai/stable-diffusion-3.5-large",
                # "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
                input={
                    "image": blob_url,  # ← open() ではなく URL
                    # "image": open(temp_path, "rb"),
                    "prompt": "a cool fashionable middle-aged man, fully clothed, wearing stylish outfit, realistic portrait, safe for work",
                    "strength": 0.7,
                }
            )
        else:
            raise e
        return JSONResponse(content={"error": "Replicate API failed"}, status_code=500)

    generated_url = str(output[0]) if isinstance(output, list) else str(output)

    # Visionで画像解析 → ファッション情報を構造化取得
    try:
        fashion_items = generate_fashion_description(generated_url)

    except Exception as e:
        logging.error(f"💥 ファッション情報生成でエラー（logging）: {e}")
        return JSONResponse(content={"error": "Fashion description failed"}, status_code=500)

    return JSONResponse(content={
        "generated_image_url": generated_url,
        "before_image_url": blob_url,  # ← blob の URL も返す
        "fashion_items": fashion_items,
    })
