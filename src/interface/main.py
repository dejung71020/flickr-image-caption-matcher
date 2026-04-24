import os
import pandas as pd
from dotenv import load_dotenv

from src.infrastructure.flickr_repository import FlickrRepository
from src.infrastructure.gemini_client import GeminiClient
from src.application.dataset_service import DatasetService
from src.application.prediction_service import PredictionService
from src.application.evaluation_service import EvaluationService

def main():
    load_dotenv()

    caption_file = os.getenv("CAPTION_FILE", "captions.txt")
    image_dir = os.getenv("IMAGE_DIR", "Images")

    print("=== 1단계 - 데이터셋 생성 ===")
    repo = FlickrRepository(caption_file, image_dir)
    dataset = DatasetService(repo).build()
    print(f"생성 완료: {len(dataset)}개 샘플")

    dataset_rows = [
        {
            "image_id": s.image_id,
            "image_path": s.image_path,
            "caption": s.caption,
            "label": s.label.value,
            "mismatch_type": s.mismatch_type.value,
        } for s in dataset
    ]
    pd.DataFrame(dataset_rows).to_csv("data/dataset.csv", index=False)
    print("dataset.csv 저장 완료")

    print("\n=== 2단계 LLM pred ===")
    client = GeminiClient()
    predictions = PredictionService(client).predict_all(dataset)

    pred_rows = [
        {
            "image_id": p.image_id,
            "caption": p.caption,
            "label": p.label.value,
            "pred_match": p.pred_match,
            "confidence": p.confidence,
            "reason": p.reason,
        } for p in predictions
    ]

    pd.DataFrame(pred_rows).to_csv("data/llm_predictions.csv", index=False)
    print("llm_predictions.csv 저장 완료")

    print("\n=== 3단계 성능 평가 ===")
    metrics = EvaluationService().evaluate(predictions)
    print(f"Accuracy:  {metrics['accuracy']}")
    print(f"Precision: {metrics['precision']}")
    print(f"Recall:    {metrics['recall']}")
    print(f"F1-score:  {metrics['f1_score']}")
    print(f"\nTP:{metrics['tp']} TN:{metrics['tn']} FP:{metrics['fp']} FN:{metrics['fn']}")

if __name__ == "__main__":
    main()

