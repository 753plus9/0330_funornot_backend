import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_fashion_description(image_url: str) -> list[dict]:
    print("🧠 GPT-4oに画像URLを渡して解析開始:", image_url)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "この画像に写っている男性の服装について、以下の形式でファッションアイテムを3つ教えてください：\n\n"
                            "[\n"
                            "  {\n"
                            "    \"name\": \"商品名\",\n"
                            "    \"brand\": \"ブランド名\",\n"
                            "    \"price\": \"価格（例：¥8,900）\",\n"
                            "    \"description\": \"簡単な説明（日本語）\"\n"
                            "  }\n"
                            "]\n\n"
                            "出力はJSONだけで、コードブロックや説明文は不要です。"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        max_tokens=1000
    )

    content = response.choices[0].message.content
    print("📦 GPTからのJSON応答:", content)

    # コードブロックなどが混ざっていたら削除
    cleaned = re.sub(r"^```json|```$", "", content.strip(), flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("❌ JSON変換エラー。中身:", cleaned)
        return []
