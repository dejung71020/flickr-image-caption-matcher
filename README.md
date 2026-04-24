# 🖼️ 이미지-캡션 일치 판단 시스템

Flickr8k 데이터셋을 기반으로 120개의 이미지-캡션 샘플을 생성하고,
Google Gemini LLM(멀티모달)을 활용해 이미지와 문장의 일치 여부를 자동 판단하는 시스템입니다.

---

# 🧰 기술 스택

| 분류       | 기술                                           |
| -------- | -------------------------------------------- |
| Language | Python 3.11                                  |
| LLM API  | Google Gemini `models/gemini-2.5-flash-lite` |
| 데이터 처리   | pandas                                       |
| 이미지 처리   | Pillow                                       |
| 환경변수 관리  | python-dotenv                                |
| 아키텍처     | DDD (Domain-Driven Design)                   |
| 버전 관리    | Git / GitHub                                 |

---

# 📁 프로젝트 구조

```
.
├── src/
│   ├── domain/
│   │   ├── entities.py
│   │   └── value_objects.py
│   ├── application/
│   │   ├── dataset_service.py
│   │   ├── prediction_service.py
│   │   └── evaluation_service.py
│   ├── infrastructure/
│   │   ├── flickr_repository.py
│   │   └── gemini_client.py
│   └── interface/
│       └── main.py
├── data/
├── docs/
│   ├── architecture.md
│   └── features.md
├── Images/
├── captions.txt
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

# ⚙️ 환경 세팅

## 1. 저장소 클론

```bash
git clone https://github.com/{계정명}/{저장소명}.git
cd {저장소명}
```

---

## 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### requirements.txt

```
google-genai
pandas
pillow
python-dotenv
```

---

## 3. 환경변수 설정 (.env)

프로젝트 루트에 `.env` 파일 생성 후:

```
GEMINI_API_KEY=본인_Gemini_API_키_입력
IMAGE_DIR=Images
CAPTION_FILE=captions.txt
```

⚠️ 주의

* `.env`는 `.gitignore`에 포함
* 절대 GitHub 업로드 금지

---

## 🔑 Gemini API 키 발급

1. https://aistudio.google.com/ 접속
2. 로그인 → Get API Key 클릭
3. `.env`에 붙여넣기

---

## 4. 데이터셋 준비 (Flickr8k)

```
프로젝트 루트/
├── Images/
│   ├── 1000268201_693b08cb0e.jpg
│   ├── 1001773457_577c3a7d70.jpg
│   └── ...
└── captions.txt
```

### captions.txt 형식

```
image,caption
1000268201_693b08cb0e.jpg,A child in a pink dress is climbing up a set of stairs.
1000268201_693b08cb0e.jpg,A girl going into a wooden building.
```

---

# ▶️ 실행 방법

```bash
python -m src.interface.main
```

⚠️ 반드시 `-m` 옵션 사용
(DDD 구조에서 절대 임포트 정상 동작을 위해 필요)

---

# 🔄 실행 흐름

## 1단계: 데이터셋 생성

* 8,091개 이미지 중 120개 샘플 선택 (seed=42)
* Gemini가 캡션 변형
* `data/dataset.csv` 저장

## 2단계: LLM 예측

* 이미지 + 캡션 입력
* match / confidence / reason 반환
* `data/llm_predictions.csv` 저장

## 3단계: 성능 평가

* Accuracy / Precision / Recall / F1-score 출력
* TP / TN / FP / FN 계산

---

# 📊 출력 파일

## data/dataset.csv

| 컬럼            | 설명                                                          |
| ------------- | ----------------------------------------------------------- |
| image_id      | 이미지 파일명                                                     |
| image_path    | 이미지 경로                                                      |
| caption       | 문장                                                          |
| label         | 1 = 일치 / 0 = 불일치                                            |
| mismatch_type | original / shuffle / object_swap / action_swap / place_swap |

---

## data/llm_predictions.csv

| 컬럼         | 설명      |
| ---------- | ------- |
| image_id   | 이미지 파일명 |
| caption    | 입력 문장   |
| label      | 정답      |
| pred_match | 예측값     |
| confidence | 확신도     |
| reason     | 판단 근거   |

---

# 🧪 데이터셋 구성 전략

| 유형          | 개수 | label | 설명        |
| ----------- | -- | ----- | --------- |
| original    | 40 | 1     | 원본        |
| shuffle     | 20 | 0     | 다른 이미지 캡션 |
| object_swap | 20 | 0     | 객체 변경     |
| action_swap | 20 | 0     | 행동 변경     |
| place_swap  | 20 | 0     | 장소 변경     |

---

## ✏️ 변형 예시

```
[원문]        A dog is running through the grass.
[object_swap] A cat is running through the grass.
[action_swap] A dog is sleeping through the grass.
[place_swap]  A dog is running inside a classroom.
```

---

# 🏗️ 아키텍처 (DDD)

```
Interface → Application → Domain
                             ↑
Infrastructure ──────────────┘
```

| 레이어            | 역할       | 특징             |
| -------------- | -------- | -------------- |
| Domain         | 비즈니스 규칙  | 외부 의존 없음       |
| Application    | 유스케이스 조율 | Domain 조합      |
| Infrastructure | 외부 연동    | API / 파일       |
| Interface      | 실행 진입점   | Application 호출 |

---

# 🚀 어필 포인트

### 1. DDD 아키텍처

레이어 분리로 유지보수성과 확장성 확보

### 2. Enum 기반 값 객체

오타 및 잘못된 값 방지

### 3. 재현 가능한 실험

`seed=42` 고정 → 동일 결과 보장

### 4. API 키 보안

`.env + .gitignore`

### 5. 멀티모달 LLM 활용

이미지 + 텍스트 동시 처리

### 6. 동적 데이터 증강

Gemini 기반 자연스러운 변형

### 7. Rate Limit 대응

`time.sleep()` 적용


# 🧠 프롬프트 설계 비교

---

## 🅰️ Prompts "A" : 기본 프롬프트 (Direct Prompting)

```text
"이 사진이랑 문장이 맞는지 확인하고, 바로 결과만 내놔."
```

### 📌 설명

가장 단순하고 직관적인 명령입니다.
복잡한 생각 과정 없이 이미지와 문장을 보고 일치 여부를 즉시 판단하라고 지시합니다.

### ⚖️ 장단점

* **장점**

  * 처리 속도가 가장 빠름
  * 프롬프트 구조가 매우 간단

* **단점**

  * 문장이 복잡한 경우 오류 발생 가능
  * 교묘한 불일치(예: 색상 차이)에서 오판 가능성 높음

---

## 🅱️ Prompts "B" : 구조화된 분석 프롬프트 (Aspect-based Prompting)

```text
"그냥 판단하지 말고, 
1. 사물 
2. 행동 
3. 장소 
4. 전체 느낌 
순서대로 하나씩 따져본 다음에 결과를 알려줘."
```

### 📌 설명

LLM에게 명확한 채점 기준을 제시하는 방식입니다.
이미지와 문장을 비교할 때 객체(사물/사람), 행동(동사), 배경(장소)이 각각 맞는지 꼼꼼히 체크하도록 유도합니다.

### ⚖️ 장단점

* **장점**

  * 논리적인 판단 가능
  * Object / Action / Place Swap 탐지에 강함
  * 데이터셋 설계와 직접적으로 정렬됨

* **단점**

  * A 방식보다 처리 속도 느림
  * 프롬프트 길이 증가

---

## 🅲 Prompts "C" : 단계별 추론 프롬프트 (Chain-of-Thought, CoT)

```text
"1단계: 사진에 있는 거 다 적어봐.
2단계: 문장에 있는 거 다 적어봐.
3단계: 둘을 꼼꼼히 비교해봐.
4단계: 그 비교를 바탕으로 최종 결론을 내려."
```

### 📌 설명

현재 AI 업계에서 가장 성능이 좋다고 알려진
**Chain-of-Thought (생각의 사슬)** 기법입니다.

AI가 답을 바로 내리지 않고,
사람처럼 단계별 사고 과정을 거치도록 강제합니다.

### ⚖️ 장단점

* **장점**

  * 가장 높은 정확도
  * 복잡한 불일치 상황에서도 강함

* **단점**

  * 처리 시간이 가장 오래 걸림
  * 비용 증가 가능성 (API 사용량 증가)

---

## 📊 결과 요약

| prompt_type | accuracy | precision | recall | f1     |
| ----------- | -------- | --------- | ------ | ------ |
| A           | 0.8707   | 0.8750    | 0.7179 | 0.7887 |
| B           | 0.8803   | 0.8571    | 0.7692 | 0.8108 |
| C           | 0.8793   | 0.9032    | 0.7179 | 0.8000 |

---

## 🔍 분석

### 1. 가장 높은 F1

* **Prompt B** (0.8108)

---

### 2. mismatch_type별 오류

* **Prompt A**

  ```json
  {'action_swap': 3, 'object_swap': 1, 'original': 11}
  ```

* **Prompt B**

  ```json
  {'action_swap': 3, 'object_swap': 1, 'original': 9, 'place_swap': 1}
  ```

* **Prompt C**

  ```json
  {'action_swap': 2, 'object_swap': 1, 'original': 11}
  ```

---

### 3. confidence > 0.8 이면서 틀린 경우

* Prompt A: **12개**
* Prompt B: **5개**
* Prompt C: **3개**

---

### 4. reason 있지만 틀린 샘플 (상위 3개)

#### 📌 Prompt A

| image_id                  | label | match | reason                                                                                                                   |
| ------------------------- | ----- | ----- | ------------------------------------------------------------------------------------------------------------------------ |
| 1247181182_35cabd76f3.jpg | 1     | 0     | 이미지에 있는 사람은 앉아 있는 것이 아니라 쪼그려 앉아 있습니다. 따라서 캡션과 이미지가 일치하지 않습니다.                                                            |
| 2180480870_dcaf5ac0df.jpg | 1     | 0     | 사진 속의 개는 뛰어가고 있는 모습이며, 점프를 하려는 자세로 보이지 않습니다. 따라서 캡션과 사진이 일치하지 않습니다.                                                      |
| 3517023411_a8fbd15230.jpg | 1     | 0     | 사진에는 복장을 갖춘 사람이 자전거를 타고 있는 모습이 담겨 있지만, 주변에 달리는 사람은 보이지 않습니다. 따라서 '달리는 사람들을 따라잡기 위해 경주하는 자전거 타는 사람'이라는 캡션은 사진과 일치하지 않습니다. |

---

#### 📌 Prompt B

| image_id                  | label | match | reason                                                                                                                           |
| ------------------------- | ----- | ----- | -------------------------------------------------------------------------------------------------------------------------------- |
| 2180480870_dcaf5ac0df.jpg | 1     | 0     | 사진 속 개는 뛰고 있는 모습이며, 점프하려는 자세를 하고 있지 않습니다. 따라서 캡션의 '점프하려는' 이라는 행동과 일치하지 않습니다. 개의 모습은 캡션과 부분적으로 일치하나, 행동 묘사가 틀려 전체적으로 매치가 되지 않습니다. |
| 3517023411_a8fbd15230.jpg | 1     | 0     | 사진에는 자전거를 타는 사람이 있지만, 달리는 사람은 보이지 않습니다. 따라서 캡션의 내용과 일치하지 않습니다.                                                                   |
| 3202360797_2084743e90.jpg | 1     | 0     | 사진 속 강아지는 눈 위를 걷고 있지만, 타이어 자국은 보이지 않습니다. 따라서 캡션의 내용과 사진이 일치하지 않습니다.                                                              |

---

#### 📌 Prompt C

| image_id                  | label | match | reason                                                                                                           |
| ------------------------- | ----- | ----- | ---------------------------------------------------------------------------------------------------------------- |
| 2180480870_dcaf5ac0df.jpg | 1     | 0     | 이미지에는 공원에서 달리는 갈색 개가 있지만, 개가 점프하려는 모습은 명확하게 보이지 않습니다. 점프하려는 자세보다는 달리는 듯한 움직임이 더 두드러집니다.                          |
| 3517023411_a8fbd15230.jpg | 1     | 0     | 이미지에는 자전거를 타는 사람이 있지만, 달리는 사람은 보이지 않습니다. 또한, 자전거를 타는 사람이 경주하는 상황인지도 불분명하며, 따라서 캡션과 일치하지 않습니다.                    |
| 2029280005_a19609c81a.jpg | 1     | 0     | 이미지에는 벤치가 있지만, 캡션에 언급된 '도시'라는 장소가 이미지에서 명확하게 드러나지 않습니다. 또한, 캡션은 '검은 셔츠'를 입은 남자를 묘사하지만, 이미지의 남자는 검은색 재킷을 입고 있습니다. |
