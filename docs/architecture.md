# 아키텍처 설계

## 프로젝트 개요
Flickr8k 데이터셋을 기반으로 120개의 이미지-캡션 샘플을 생성하고,
Gemini LLM으로 이미지와 문장의 일치 여부를 판단하는 시스템.

## DDD(Domain-Driven Design) 레이어 구조

DDD는 소프트웨어를 비즈니스 도메인 중심으로 설계하는 방법론입니다.
레이어를 나누는 이유: 각 계층이 한 가지 역할만 담당 → 유지보수·테스트 용이

### 레이어별 역할

| 레이어 | 폴더 | 역할 | 외부 의존 |
|--------|------|------|-----------|
| Domain | src/domain/ | 핵심 비즈니스 규칙. 엔티티·값객체 정의 | 없음 |
| Application | src/application/ | 유스케이스 조율. 도메인을 조합해 흐름
구성 | Domain만 |
| Infrastructure | src/infrastructure/ | 파일 I/O, 외부 API 연동 | 모두
가능 |
| Interface | src/interface/ | 실행 진입점 (CLI) | Application만 |

### 의존성 방향
Interface → Application → Domain ← Infrastructure

## 파일 구조

src/
├── domain/
│   ├── entities.py        # Sample, Prediction 엔티티
│   └── value_objects.py   # MismatchType, Label 값 객체
├── application/
│   ├── dataset_service.py    # 120개 샘플 생성
│   ├── prediction_service.py # Gemini 판단 실행
│   └── evaluation_service.py # 지표 계산
├── infrastructure/
│   ├── flickr_repository.py  # captions.txt 파싱
│   └── gemini_client.py      # Gemini API 래퍼
└── interface/
    └── main.py               # 실행 진입점

## 사용 기술
- Python 3.11
- Gemini API: models/gemini-2.5-flash-lite (multimodal)
- pandas: 데이터 처리 및 CSV 저장
- Pillow: 이미지 로딩
- python-dotenv: 환경변수 관리

  ---