# 기능 정의

## 기능 1: 데이터셋 생성 (DatasetService)

120개 샘플을 아래 규칙으로 생성합니다.

| 타입 | 개수 | label | 방법 |
|------|------|-------|------|
| original | 40 | 1 | 원본 이미지 + 원본 캡션 |
| shuffle | 20 | 0 | 원본 이미지 + 다른 이미지의 캡션 |
| object_swap | 20 | 0 | 원본 캡션에서 객체(명사) 교체 |
| action_swap | 20 | 0 | 원본 캡션에서 행동(동사) 교체 |
| place_swap | 20 | 0 | 원본 캡션에서 장소/배경 교체 |

### 출력 컬럼
image_id, image_path, caption, label, mismatch_type

### swap 교체 사전
- object: dog↔cat, man↔woman, boy↔girl, horse↔dog, ball↔frisbee
- action: running↔sleeping, jumping↔sitting, playing↔eating,
swimming↔walking, riding↔pushing
- place: grass↔water, beach↔mountain, street↔field, pool↔grass, sand↔snow

## 기능 2: LLM 판단 (PredictionService)

각 샘플마다 이미지 + 캡션을 Gemini에 전달하여 JSON 응답을 받습니다.

### 입력
- 이미지 1장 (base64 인코딩)
- 캡션 문자열 1개

### 출력 (JSON)
```json
{
"match": 0 또는 1,
"confidence": 0.0 ~ 1.0,
"reason": "판단 이유 1~3문장"
}

출력 컬럼

image_id, caption, label, pred_match, confidence, reason

기능 3: 성능 평가 (EvaluationService)

label(정답) vs pred_match(예측)을 비교하여 지표를 계산합니다.

- Accuracy  = (TP + TN) / 전체
- Precision = TP / (TP + FP)
- Recall    = TP / (TP + FN)
- F1-score  = 2 × Precision × Recall / (Precision + Recall)

---