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

    def predict(self, image_path: str, caption: str, prompt_type: str = "A") -> dict:
        image_data = Path(image_path).read_bytes()

        prompts = {
            "A": f"""You are an image-caption matching evaluator.
            Determine if the image and caption match.
            Caption: "{caption}"
            Respond ONLY in this JSON format:
            {{"match": 0 or 1, "confidence": float between 0.0 and 1.0, "reason": "1-3
            sentence explanation in Korean"}}""",

                        "B": f"""You are an image-caption matching evaluator.
            Analyze these aspects in order:
            1. Objects/subjects: Are the main objects in the image the same as in the
            caption?
            2. Actions/verbs: Do the actions match?
            3. Location/setting: Does the background match?
            4. Overall meaning: Does the overall scene match?
            Based on this structured analysis, determine if they match.
            Caption: "{caption}"
            Respond ONLY in this JSON format:
            {{"match": 0 or 1, "confidence": float between 0.0 and 1.0, "reason": "1-3
            sentence explanation in Korean"}}""",

                        "C": f"""You are an image-caption matching evaluator.
            Follow these steps:
            Step 1 - Key elements in the IMAGE: List main objects, actions, locations
            you see.
            Step 2 - Key elements in the CAPTION: List main objects, actions,
            locations mentioned.
            Step 3 - Compare: Identify similarities and differences.
            Step 4 - Final judgment: Based on comparison, decide if they match.
            Caption: "{caption}"
            Respond ONLY in this JSON format:
            {{"match": 0 or 1, "confidence": float between 0.0 and 1.0, "reason": "1-3
            sentence explanation in Korean"}}""",
        }

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                    prompts[prompt_type],
                ],
            )
        except Exception as e:
            if "429" in str(e):
                print("  Rate limit, 10초 대기 후 재시도...")
                time.sleep(10)
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                        prompts[prompt_type],
                    ],
                )
            else:
                raise

        text = response.text
        if not text:
            return {"match": -1, "confidence": 0.0, "reason": "응답 없음"}
        text = text.strip()
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
    
    def analyze_image(self, image_path: str) -> dict:
        image_data = Path(image_path).read_bytes()
        prompt = """Analyze this image and extract key information.
        Return ONLY this JSON format:
        {
        "objects": ["list of main objects/subjects"],
        "actions": ["list of actions/verbs happening"],
        "locations": ["list of locations/settings"]
        }
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
                time.sleep(10)
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                        prompt,
                    ],
                )
            else:
                raise
        text = (response.text or "{}").strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    def analyze_text(self, caption: str) -> dict:
        prompt = f"""Extract key information from this caption.
Caption: "{caption}"
Return ONLY this JSON format:
{{
"objects": ["list of objects/subjects mentioned"],
"actions": ["list of actions/verbs mentioned"],
"locations": ["list of locations/settings mentioned"]
}}"""
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=prompt
            )
        except Exception as e:
            if "429" in str(e):
                time.sleep(10)
                response = self.client.models.generate_content(
                    model=self.model, contents=prompt
                )
            else:
                raise
        text = (response.text or "{}").strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    def judge(self, image_features: dict, text_features: dict,
            caption: str, image_path: str, prompt_type: str = "B") -> dict:
        image_data = Path(image_path).read_bytes()
        prompts = {
            "A": f"""Determine if the image and caption match.
            Caption: "{caption}"
            Image has: {image_features}
            Respond ONLY: {{"match": 0 or 1, "confidence": float, "reason":
            "Korean"}}""",

                        "B": f"""Analyze these aspects:
            1. Objects match? Image:{image_features.get('objects',[])}
            Caption:{text_features.get('objects',[])}
            2. Actions match? Image:{image_features.get('actions',[])}
            Caption:{text_features.get('actions',[])}
            3. Locations match? Image:{image_features.get('locations',[])}
            Caption:{text_features.get('locations',[])}
            4. Overall meaning?
            Caption: "{caption}"
            Respond ONLY: {{"match": 0 or 1, "confidence": float, "reason":
            "Korean"}}""",

                        "C": f"""Step 1 - Image elements: {image_features}
            Step 2 - Caption elements: {text_features}
            Step 3 - Compare similarities and differences
            Step 4 - Final judgment
            Caption: "{caption}"
            Respond ONLY: {{"match": 0 or 1, "confidence": float, "reason":
            "Korean"}}
            """,
        }
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                    prompts.get(prompt_type, prompts["B"]),
                ],
            )
        except Exception as e:
            if "429" in str(e):
                time.sleep(10)
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                        prompts.get(prompt_type, prompts["B"]),
                    ],
                )
            else:
                raise
        text = response.text
        if not text:
            return {"match": -1, "confidence": 0.0, "reason": "응답 없음"}
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

    def critic(self, judge_result: dict, image_features: dict, text_features: dict) -> dict:
        prompt = f"""You are a critic reviewing an image-caption matching
        judgment.

        Judge's result: {judge_result}
        Image features: {image_features}
        Caption features: {text_features}

        Review critically:
        - Is the confidence score appropriate?
        - Were all objects, actions, and locations properly compared?
        - Is the reasoning sufficient and accurate?

        Return ONLY this JSON:
        {{
        "agree": true or false,
        "needs_review": true or false,
        "reason": "Korean explanation"
        }}"""
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=prompt
            )
        except Exception as e:
            if "429" in str(e):
                time.sleep(10)
                response = self.client.models.generate_content(
                    model=self.model, contents=prompt
                )
            else:
                raise
        text = (response.text or "").strip()
        if not text:
            return {"agree": True, "needs_review": False, "reason": "응답 없음"}
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())