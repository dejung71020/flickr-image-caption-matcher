# src/application/prompt_comparison_service.py
import time
import pandas as pd
from src.domain.entities import Prediction
from src.domain.value_objects import Label
from src.infrastructure.gemini_client import GeminiClient
from src.application.evaluation_service import EvaluationService


class PromptComparisonService:
    def __init__(self, client: GeminiClient):
        self.client = client
        self.evaluator = EvaluationService()

    def run(self, dataset_path: str):
        df = pd.read_csv(dataset_path)

        detail = {
            i: {
                "image_id":      row["image_id"],
                "caption":       row["caption"],
                "label":         row["label"],
                "mismatch_type": row["mismatch_type"],
            }
            for i, (_, row) in enumerate(df.iterrows())
        }

        summary_rows = []

        for prompt_type in ["A", "B", "C"]:
            print(f"\n=== Prompt {prompt_type} 실행 중 ===")
            predictions = []

            for i, (_, row) in enumerate(df.iterrows()):
                print(f"  [{i+1}/{len(df)}] {row['image_id']}")
                try:
                    result = self.client.predict(
                        row["image_path"], row["caption"], prompt_type
                    )
                    pred_match  = result["match"]
                    confidence  = result["confidence"]
                    reason      = result["reason"]
                except Exception as e:
                    print(f"    오류: {e}")
                    pred_match  = -1
                    confidence  = 0.0
                    reason      = f"오류: {e}"

                predictions.append(Prediction(
                    image_id=row["image_id"],
                    caption=row["caption"],
                    label=Label(row["label"]),
                    pred_match=pred_match,
                    confidence=confidence,
                    reason=reason,
                ))

                pt = prompt_type.lower()
                detail[i][f"prompt_{pt}_match"]      = pred_match
                detail[i][f"prompt_{pt}_confidence"] = confidence
                detail[i][f"prompt_{pt}_reason"]     = reason

                time.sleep(1)

            metrics = self.evaluator.evaluate(predictions)
            print(f"  Accuracy:{metrics['accuracy']} F1:{metrics['f1_score']}")
            summary_rows.append({
                "prompt_type": prompt_type,
                "accuracy":    metrics["accuracy"],
                "precision":   metrics["precision"],
                "recall":      metrics["recall"],
                "f1":          metrics["f1_score"],
            })

        return pd.DataFrame(summary_rows), pd.DataFrame(list(detail.values()))