# src/infrastructure/gemini_client.py
import os
import json
import base64
import google.generativeai as genai
from pathlib import Path

'''
이미지를 이진화했다.
GEMINI에게 이진화한 이미지를 전송할 때에는 64진수로 변환하여 보내고(2진수인 경우 깨지는 경우가 있다.) json에 넣기 위해 문자열로 decode한다.

너는 이미지와 캡션이 일치하는지 평가하는 역할이야.
제공된 이미지와 문자를 분석하여 이미지와 캡션이 일치하는지 판단해.
를 영어로 해서 더 빠르게 처리하도록 한다.
판단 근거만 한국어로 하도록한다.

전처리 전 -> response.text.strip
```text
```json
{
  "match": 1,
  "confidence": 0.95,
  "reason": "이미지 속에서 개가 잔디밭을 달리는 모습이 확인되며, 문장의 설명과 일치합니다."
}
'''
class GeminiClient:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("models/gemini-2.5-flash-lite")

    def predict(self, image_path: str, caption: str) -> dict:
        image_data = Path(image_path).read_bytes()
        image_part = {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(image_data).decode("utf-8")
        }
        prompt = f"""
        You are an image-caption matching evaluator.

        Given an image and a caption, determine whether they match.

        Caption: "{caption}"

        Respond ONLY in this JSON format:
        {{
            "match": 0 or 1,
            "confidence": float between 0.0 and 1.0,
            "reason": "1-3 sentence explanation in Korean"
        }}
        """

        response = self.model.generate_content([image_part, prompt])
        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        return json.loads(text.strip())