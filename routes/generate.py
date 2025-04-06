# backend/routes/generate.py
import os
import shutil
import uuid
import time

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from replicate.exceptions import ModelError
from routes.fashion_service import generate_fashion_description
from utils.upload_to_blob import upload_image_to_blob  # ← 追加！
import replicate

router = APIRouter()

@router.post("/api/generate")
async def generate_image(image: UploadFile = File(...)):
    print("🔥 画像を受け取りました:", image.filename)

    # Azure Blob にアップロード
    blob_url = await upload_image_to_blob(image)
    print("📤 Blob URL:", blob_url)
    
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
        if "NSFW" in str(e):
            print("⚠️ NSFW判定されたので再実行")
            time.sleep(1)
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

    generated_url = str(output[0]) if isinstance(output, list) else str(output)

    # Visionで画像解析 → ファッション情報を構造化取得
    fashion_items = generate_fashion_description(generated_url)

    return JSONResponse(content={
        "generated_image_url": generated_url,
        "fashion_items": fashion_items,
    })
