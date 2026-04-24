# src/application/langgraph_service.py
import time
import pandas as pd
from typing import TypedDict
from langgraph.graph import StateGraph, END

from src.infrastructure.gemini_client import GeminiClient
from src.application.evaluation_service import EvaluationService
from src.domain.entities import Prediction
from src.domain.value_objects import Label


class VerificationState(TypedDict):
    image_path: str
    caption: str
    image_features: dict
    text_features: dict
    judge_result: dict
    critic_result: dict
    judge_call_count: int
    best_prompt: str


class LangGraphService:
    MAX_JUDGE_CALLS = 3

    def __init__(self, client: GeminiClient, best_prompt: str = "B"):
        self.client = client
        self.best_prompt = best_prompt
        self.graph = self._build_graph()

    def _image_analyzer(self, state: VerificationState) -> dict:
        print("    [Node 1] Image Analyzer")
        features = self.client.analyze_image(state["image_path"])
        time.sleep(1)
        return {"image_features": features}

    def _text_analyzer(self, state: VerificationState) -> dict:
        print("    [Node 2] Text Analyzer")
        features = self.client.analyze_text(state["caption"])
        time.sleep(1)
        return {"text_features": features}

    def _judge(self, state: VerificationState) -> dict:
        call_count = state.get("judge_call_count", 0) + 1
        print(f"    [Node 3] Judge (호출 #{call_count})")
        result = self.client.judge(
            image_features=state["image_features"],
            text_features=state["text_features"],
            caption=state["caption"],
            image_path=state["image_path"],
            prompt_type=state["best_prompt"],
        )
        time.sleep(1)
        return {"judge_result": result, "judge_call_count": call_count}

    def _critic(self, state: VerificationState) -> dict:
        print("    [Node 4] Critic")
        result = self.client.critic(
            judge_result=state["judge_result"],
            image_features=state["image_features"],
            text_features=state["text_features"],
        )
        time.sleep(1)
        return {"critic_result": result}

    def _should_retry(self, state: VerificationState) -> str:
        if state.get("judge_call_count", 1) >= self.MAX_JUDGE_CALLS:
            return "end"
        confidence = state["judge_result"].get("confidence", 1.0)
        needs_review = state["critic_result"].get("needs_review", False)
        if confidence < 0.60 or needs_review:
            print(f"    → 재실행 (confidence={confidence}, needs_review={needs_review})")
            return "retry"
        return "end"

    def _build_graph(self):
        workflow = StateGraph(VerificationState)
        workflow.add_node("image_analyzer", self._image_analyzer)
        workflow.add_node("text_analyzer",  self._text_analyzer)
        workflow.add_node("judge",          self._judge)
        workflow.add_node("critic",         self._critic)
        workflow.set_entry_point("image_analyzer")
        workflow.add_edge("image_analyzer", "text_analyzer")
        workflow.add_edge("text_analyzer",  "judge")
        workflow.add_edge("judge",          "critic")
        workflow.add_conditional_edges(
            "critic",
            self._should_retry,
            {"retry": "judge", "end": END},
        )
        return workflow.compile()

    def run_single(self, image_path: str, caption: str) -> VerificationState:
        initial = VerificationState(
            image_path=image_path,
            caption=caption,
            image_features={},
            text_features={},
            judge_result={},
            critic_result={},
            judge_call_count=0,
            best_prompt=self.best_prompt,
        )
        return self.graph.invoke(initial)

    def run_all(self, dataset_path: str) -> list[dict]:
        df = pd.read_csv(dataset_path)
        results = []
        for i, (_, row) in enumerate(df.iterrows()):
            print(f"\n[{i+1}/{len(df)}] {row['image_id']}")
            try:
                state = self.run_single(row["image_path"], row["caption"])
                judge = state["judge_result"]
                retry_count = max(0, state.get("judge_call_count", 1) - 1)
                results.append({
                    "image_id":          row["image_id"],
                    "label":             row["label"],
                    "pred_match":        judge.get("match", -1),
                    "confidence":        judge.get("confidence", 0.0),
                    "judge_retry_count": retry_count,
                    "final_reason":      judge.get("reason", ""),
                })
            except Exception as e:
                print(f"  오류: {e}")
                results.append({
                    "image_id":          row["image_id"],
                    "label":             row["label"],
                    "pred_match":        -1,
                    "confidence":        0.0,
                    "judge_retry_count": 0,
                    "final_reason":      f"오류: {e}",
                })
        return results