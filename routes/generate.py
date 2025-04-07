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

router = APIRouter()

logging.info(f"🪪 環境変数 REPLICATE_API_TOKEN = {os.getenv('REPLICATE_API_TOKEN')}")

@router.post("/api/generate")
async def generate_image(image: UploadFile = File(...)):
    
    try:
        logging.info(f"🔥 画像を受け取りました（logging）: {image.filename}")

        # Azure Blobにアップロードしつつ、image_bytes を取得
        blob_url, image_bytes = await upload_image_to_blob(image)
        logging.info(f"📤 Blob URL（logging）: {blob_url}")

        # Replicateに画像（bytes）を渡す（BytesIOで包む）
        image_io = io.BytesIO(image_bytes)   

        try:
            
            logging.info(f"🧪 Replicate 呼び出し準備：token={os.getenv('REPLICATE_API_TOKEN')}")

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
               
        except Exception as e:
            logging.error(f"💥 処理全体で予期せぬエラーが発生しました: {e}", exc_info=True)
            return JSONResponse(content={"error": "Internal server error"}, status_code=500)
        # try:
        #     output = replicate.run(
        #         "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
        #         input={
        #             "image": open(temp_path, "rb"),
        #             "prompt": "Without changing the person in the original photo, change the hairstyle and clothes to make them cool and stylish, safe for work",
        #             "strength": 0.7,
        #         }
        #     )

        # if "NSFW" in str(e):
        #     print("⚠️ NSFW判定されたので再実行")
        #     time.sleep(1)
        #     image_io.seek(0)  # ← 重要！読み直す準備

        #     output = replicate.run(
        #         "stability-ai/stable-diffusion-3.5-large",
        #         # "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
        #         input={
        #             "image": blob_url,  # ← open() ではなく URL
        #             # "image": open(temp_path, "rb"),
        #             "prompt": "a cool fashionable middle-aged man, fully clothed, wearing stylish outfit, realistic portrait, safe for work",
        #             "strength": 0.7,
        #         }
        #     )
        # else:
        #     raise e
        # return JSONResponse(content={"error": "Replicate API failed"}, status_code=500)

        generated_url = str(output[0]) if isinstance(output, list) else str(output)
        fashion_items = generate_fashion_description(generated_url)
        logging.info("👕 ファッション情報の取得成功")

        return JSONResponse(content={
            "generated_image_url": generated_url,
            "before_image_url": blob_url,  # ← blob の URL も返す
            "fashion_items": fashion_items,
        })
        
    except Exception as e:
        logging.error(f"💥 全体でエラー発生: {e}", exc_info=True)
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)
        