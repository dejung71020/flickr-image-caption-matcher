# src/interface/main_exam3.py
import os
import pandas as pd
from dotenv import load_dotenv

from src.infrastructure.gemini_client import GeminiClient
from src.application.langgraph_service import LangGraphService
from src.application.evaluation_service import EvaluationService
from src.domain.entities import Prediction
from src.domain.value_objects import Label


def main():
    load_dotenv()

    try:
        pr = pd.read_csv("data/prompt_results.csv")
        best_prompt = pr.loc[pr["f1"].idxmax(), "prompt_type"]
    except FileNotFoundError:
        best_prompt = "B"
    print(f"Judge에 사용할 프롬프트: Prompt {best_prompt}")

    print("\n=== 시험 3: LangGraph 다단계 검증 ===")
    client  = GeminiClient()
    service = LangGraphService(client, best_prompt)
    results = service.run_all("data/dataset.csv")

    results_df = pd.DataFrame(results)
    results_df.to_csv("data/langgraph_results.csv", index=False)
    print("\nlanggraph_results.csv 저장 완료")

    evaluator = EvaluationService()
    lg_preds = [
        Prediction(
            image_id=r["image_id"],
            caption="",
            label=Label(r["label"]),
            pred_match=r["pred_match"],
            confidence=r["confidence"],
            reason=r["final_reason"],
        )
        for r in results
    ]
    lg_metrics = evaluator.evaluate(lg_preds)

    try:
        simple_df = pd.read_csv("data/llm_predictions.csv")
        simple_preds = [
            Prediction(
                image_id=row["image_id"],
                caption=row["caption"],
                label=Label(row["label"]),
                pred_match=row["pred_match"],
                confidence=row["confidence"],
                reason=row["reason"],
            )
            for _, row in simple_df.iterrows()
        ]
        simple_metrics = evaluator.evaluate(simple_preds)
    except FileNotFoundError:
        simple_metrics = None

    print("\n=== 성능 비교 ===")
    print(f"{'':20} {'단순 1회':>12} {'LangGraph':>12}")
    print("-" * 46)
    if simple_metrics:
        print(f"{'Accuracy':<20} {simple_metrics['accuracy']:>12} {lg_metrics['accuracy']:>12}")
        print(f"{'F1-score':<20} {simple_metrics['f1_score']:>12} {lg_metrics['f1_score']:>12}")
        simple_err = simple_metrics['fp'] + simple_metrics['fn']
        lg_err     = lg_metrics['fp'] + lg_metrics['fn']
        print(f"{'오류 개수':<20} {simple_err:>12} {lg_err:>12}")
        print(f"\n오류 감소: {simple_err - lg_err}개")

    retried = results_df[results_df["judge_retry_count"] > 0]
    print(f"\nJudge 재실행 발생: {len(retried)}개 샘플")
    print(f"평균 재실행 횟수: {results_df['judge_retry_count'].mean():.2f}")


if __name__ == "__main__":
    main()