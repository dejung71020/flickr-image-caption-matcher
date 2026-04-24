# src/interface/main_exam2.py
import os
import pandas as pd
from dotenv import load_dotenv

from src.infrastructure.gemini_client import GeminiClient
from src.application.prompt_comparison_service import PromptComparisonService


def main():
    load_dotenv()

    print("=== 시험 2: 프롬프트 비교 분석 ===")
    client  = GeminiClient()
    service = PromptComparisonService(client)
    summary_df, detail_df = service.run("data/dataset.csv")

    summary_df.to_csv("data/prompt_results.csv", index=False)
    detail_df.to_csv("data/prompt_predictions_detail.csv", index=False)
    print("\nprompt_results.csv 저장 완료")

    print("\n=== 결과 요약 ===")
    print(summary_df.to_string(index=False))

    print("\n=== 분석 ===")

    best = summary_df.loc[summary_df["f1"].idxmax(), "prompt_type"]
    print(f"\n1. 가장 높은 F1: Prompt {best}")

    print("\n2. mismatch_type별 오류:")
    for pt in ["A", "B", "C"]:
        col = f"prompt_{pt.lower()}_match"
        errors = detail_df[
            (detail_df["label"] != detail_df[col]) & (detail_df[col] !=
-1)
        ]
        by_type = errors.groupby("mismatch_type").size().to_dict()
        print(f"  Prompt {pt}: {by_type}")

    print("\n3. confidence > 0.8 이면서 틀린 경우:")
    for pt in ["A", "B", "C"]:
        mc = f"prompt_{pt.lower()}_match"
        cc = f"prompt_{pt.lower()}_confidence"
        mask = (
            (detail_df["label"] != detail_df[mc]) &
            (detail_df[cc] > 0.8) &
            (detail_df[mc] != -1)
        )
        print(f"  Prompt {pt}: {mask.sum()}개")

    print("\n4. reason 있지만 틀린 샘플 (상위 3개 예시):")
    for pt in ["A", "B", "C"]:
        mc = f"prompt_{pt.lower()}_match"
        rc = f"prompt_{pt.lower()}_reason"
        wrong = detail_df[
            (detail_df["label"] != detail_df[mc]) & (detail_df[mc] != -1)
        ][["image_id", "label", mc, rc]].head(3)
        print(f"\n  Prompt {pt}:")
        print(wrong.to_string(index=False))


if __name__ == "__main__":
    main()