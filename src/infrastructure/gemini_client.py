# src/infrastructure/gemini_client.py
import os
import json
import time
from google import genai
from google.genai import types
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
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-2.5-flash-lite"

    def predict(self, image_path: str, caption: str) -> dict:
        image_data = Path(image_path).read_bytes()
        prompt = f"""You are an image-caption matching evaluator.

        Given an image and a caption, determine whether they match.

        Caption: "{caption}"

        Respond ONLY in this JSON format:
        {{
        "match": 0 or 1,
        "confidence": float between 0.0 and 1.0,
        "reason": "1-3 sentence explanation in Korean"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                    prompt,
                ],
            )

        except Exception as e:
            if "429" in str(e):
                print("  Rate limit, 60초 대기 후 재시도...")
                time.sleep(60)
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                        prompt,
                    ],
                )
            else:
                raise
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    def generate_swap(self, caption: str, swap_type: str) -> str:
        prompts = {
            "object_swap": (
                f'Change exactly ONE object or noun in this sentence to a clearly different object. '
                f'The change must make the sentence factually wrong for the original image. '
                f'Return ONLY the modified sentence, nothing else.\n\nOriginal: "{caption}"'
            ),
            "action_swap": (
                f'Change exactly ONE action or verb in this sentence to a clearly different action. '
                f'The change must make the sentence factually wrong for the original image. '
                f'Return ONLY the modified sentence, nothing else.\n\nOriginal: "{caption}"'
            ),
            "place_swap": (
                f'Change exactly ONE location, place, or setting in this sentence to a clearly different place. '
                f'The change must make the sentence factually wrong for the original image. '
                f'Return ONLY the modified sentence, nothing else.\n\nOriginal: "{caption}"'
            ),
        }
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompts[swap_type],
            )

        except Exception as e:
            if "429" in str(e):
                print("  Rate limit, 10초 대기 후 재시도...")
                time.sleep(10)
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompts[swap_type],
                )
            else:
                raise
        time.sleep(0.5)
        text = response.text
        if not text:
            return caption
        return text.strip().strip('"')