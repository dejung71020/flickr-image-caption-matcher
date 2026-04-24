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
