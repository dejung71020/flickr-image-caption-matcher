import os
from google import genai

# 1. 클라이언트 생성
# 환경 변수에 GEMINI_API_KEY가 설정되어 있다면 (api_key=...) 부분을 생략하고 
# client = genai.Client() 라고만 써도 자동으로 키를 인식합니다.
client = genai.Client(api_key="AIzaSyDm_YJJBsvp-N7AKvk5ctTnBtZitOJcwaw")

print("사용 가능한 Gemini 모델 목록:\n" + "="*50)

# 2. client.models.list() 메서드로 모델 목록 가져오기
for model in client.models.list():
    print(f"🔹 모델 ID (코드에 쓸 이름): {model.name}")
    print(f"   표시 이름: {model.display_name}")
    print(f"   설명: {model.description}")
    print("-" * 50)