# src/application/prediction_service.py
import time
from src.domain.entities import Sample, Prediction
from src.infrastructure.gemini_client import GeminiClient

'''
예측 중간 오류 시에 예측 결과를 -1이로 함.
time.sleep(1)을 주어 API 요청속도제한을 피함.
'''
class PredictionService:
    def __init__(self, client: GeminiClient):
        self.client = client

    def predict_all(self, samples: list[Sample]) -> list[Prediction]:
        predictions = []
        for i, sample in enumerate(samples):
            print(f"[{i + 1}/{len(samples)}] {sample.image_id}")
            try:
                result = self.client.predict(sample.image_path, sample.caption)

                predictions.append(Prediction(
                    image_id=sample.image_id,
                    caption=sample.caption,
                    label=sample.label,
                    pred_match=result['match'],
                    confidence=result['confidence'],
                    reason=result['reason'],
                ))
            
            except Exception as e:
                print(f"제미나이 예측에서 오류: {e}")
                predictions.append(Prediction(
                    image_id=sample.image_id,
                    caption=sample.caption,
                    label=sample.label,
                    pred_match=-1,
                    confidence=0.0,
                    reason=f"오류: {e}",
                ))
            time.sleep(1)
        return predictions