# src/application/evaluation_service.py
from src.domain.entities import Prediction

class EvaluationService:
    def evaluate(self, predictions: list[Prediction]) -> dict:
        valid = [p for p in predictions if p.pred_match != -1]

        # 예측한 양성 중에 맞춤
        tp = sum(1 for p in valid if p.label == 1 and p.pred_match == 1)

        # 예측한 음성 중에 맞춤
        tn = sum(1 for p in valid if p.label == 1 and p.pred_match == 0)

        # 예측한 양성 중에 틀림
        fp = sum(1 for p in valid if p.label == 0 and p.pred_match == 1)

        # 예측한 음성 중에 틀림
        fn = sum(1 for p in valid if p.label == 1 and p.pred_match == 0)

        # 정확도 : 전체 데이터에서 맞춘 거
        accuracy = (tp + tn) / len(valid) if valid else 0

        # 정밀도 : 양성이라 예측한 것중에 진짜 양성인거
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0

        # 재현율 : 실제 양성 중에 예측한 양성
        recall = tp / (tp + tn) if (tp + tn) > 0 else 0

        # f1-score : 정밀도와 재현율의 조화평균이었던거 같은데 개념만 빅분기때외우고 식은 모름
        f1 = (2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0)

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "total": len(valid),
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
        }