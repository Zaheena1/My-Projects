"""
Lightweight agent framework with autonomous agents:

- `BehavioralRiskAgent` — rule-based behavioral checks
- `ANNAgent` — optional Keras model with heuristic fallback
- `CoordinatorAgent` — fuses ANN + behavioral decisions
- `LLMReporter` — generates a human report via OpenAI if available or a fallback
Run as a script to see a short demo of orchestration.
"""
import logging
import threading
import queue
import time
from typing import Any, Dict, Optional, List
import os
import json
import random

logging.basicConfig(level=logging.INFO)


class Agent:
    """Simple threaded agent with an inbox queue and message handler.

    Messages are dictionaries. If a message contains a `reply_to` key it should
    be a `queue.Queue` where the agent will put its response.
    """

    def __init__(self, name: str):
        self.name = name
        self._inbox: queue.Queue = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, name=self.name, daemon=True)
        self._thread.start()
        logging.info("Agent %s started", self.name)

    def stop(self, timeout: float = 1.0):
        self._running = False
        # wake the thread
        try:
            self._inbox.put_nowait(None)
        except Exception:
            pass
        if self._thread:
            self._thread.join(timeout)
            logging.info("Agent %s stopped", self.name)

    def send(self, msg: Dict[str, Any]):
        self._inbox.put(msg)

    def _run(self):
        while self._running:
            try:
                msg = self._inbox.get(timeout=0.5)
            except queue.Empty:
                continue
            if msg is None:
                continue
            try:
                self.handle_message(msg)
            except Exception:
                logging.exception("Error handling message in %s", self.name)

    def handle_message(self, msg: Dict[str, Any]):
        raise NotImplementedError()


class BehavioralRiskAgent(Agent):
    """Behavioral rules engine.

    Supports synchronous `analyze(transaction)` for direct calls and also
    handles messages of type `{'type': 'analyze', 'transaction': {...}, 'reply_to': Queue}`.
    """

    def __init__(self):
        super().__init__("BehavioralRiskAgent")

    def handle_message(self, msg: Dict[str, Any]):
        if msg.get("type") == "analyze":
            tx = msg.get("transaction", {})
            result = self.analyze(tx)
            reply_q = msg.get("reply_to")
            if isinstance(reply_q, queue.Queue):
                reply_q.put(result)

    def _to_int_flag(self, value: Any, default: int = 1) -> int:
        try:
            return int(value)
        except Exception:
            if isinstance(value, str):
                low = value.strip().lower()
                if low in ("no", "false", "0", "fail", "failed"):
                    return 0
                if low in ("yes", "true", "1", "match", "passed"):
                    return 1
            return default

    def analyze(self, transaction: Dict[str, Any]):
        reasons: List[str] = []
        recommendations: List[str] = []

        amount = float(transaction.get("amount", 0) or 0)
        avg_amount = float(transaction.get("avg_amount_user", 0) or 0)
        shipping_distance = float(transaction.get("shipping_distance_km", 0) or 0)
        avs = self._to_int_flag(transaction.get("avs_match", 1), default=1)
        cvv = self._to_int_flag(transaction.get("cvv_result", 1), default=1)
        three_ds = self._to_int_flag(transaction.get("three_ds_flag", 1), default=1)

        if avg_amount > 0 and amount > avg_amount * 3:
            reasons.append("Transaction amount is unusually high compared to user history.")
            recommendations.append("Request additional authentication.")

        if shipping_distance > 500:
            reasons.append("Shipping distance is unusually large.")
            recommendations.append("Send transaction for manual review.")

        if avs == 0:
            reasons.append("AVS verification failed.")
            recommendations.append("Verify billing address.")

        if cvv == 0:
            reasons.append("CVV verification failed.")
            recommendations.append("Decline or re-verify card.")

        if three_ds == 0:
            reasons.append("3DS authentication not completed.")
            recommendations.append("Enforce 3DS authentication.")

        if reasons:
            decision = "SUSPICIOUS"
        else:
            decision = "NORMAL"
            reasons.append("No abnormal behavioral patterns detected.")
            recommendations.append("Approve transaction.")

        return {
            "decision": decision,
            "reasons": reasons,
            "recommendations": recommendations,
        }


class CoordinatorAgent(Agent):
    """Decision fusion and orchestration agent.

    This agent can perform pure fusion via `decide(...)` or handle a
    `{'type': 'process_transaction', 'transaction': {...}, 'reply_to': Queue}` message
    and orchestrate calls to the behavioral and ANN agents, then generate an
    LLM report using a provided `LLMReporter` instance.
    """

    def __init__(self, behavioral_agent: Optional[Agent] = None, ann_agent: Optional[Agent] = None, reporter: Optional['LLMReporter'] = None, threshold: float = 0.5):
        super().__init__("CoordinatorAgent")
        self.threshold = float(threshold)
        self.behavioral = behavioral_agent
        self.ann = ann_agent
        self.reporter = reporter

    def handle_message(self, msg: Dict[str, Any]):
        mtype = msg.get("type")
        if mtype == "fusion":
            ann_probability = msg.get("ann_probability", 0.0)
            behavioral_result = msg.get("behavioral_result", {})
            result = self.decide(ann_probability=ann_probability, behavioral_result=behavioral_result)
            reply_q = msg.get("reply_to")
            if isinstance(reply_q, queue.Queue):
                reply_q.put(result)

        elif mtype == "process_transaction":
            tx = msg.get("transaction", {})
            reply_q = msg.get("reply_to")

            # Query behavioral agent
            br_q = queue.Queue()
            if self.behavioral is not None:
                try:
                    self.behavioral.send({"type": "analyze", "transaction": tx, "reply_to": br_q})
                    behavioral_result = br_q.get(timeout=5.0)
                except Exception:
                    behavioral_result = self.behavioral.analyze(tx) if self.behavioral is not None else {"decision": "NORMAL", "reasons": [], "recommendations": []}
            else:
                behavioral_result = {"decision": "NORMAL", "reasons": [], "recommendations": []}

            # Query ANN agent
            ann_q = queue.Queue()
            if self.ann is not None:
                try:
                    self.ann.send({"type": "predict", "transaction": tx, "reply_to": ann_q})
                    ann_prob = ann_q.get(timeout=5.0)
                except Exception:
                    ann_prob = self.ann.predict(tx) if self.ann is not None else 0.0
            else:
                ann_prob = 0.0

            # Fuse decisions
            fusion = self.decide(ann_probability=float(ann_prob), behavioral_result=behavioral_result)

            # Generate report using LLMReporter if available
            if self.reporter is not None:
                try:
                    report_text = self.reporter.generate({**fusion, "ann_probability": ann_prob})
                except Exception:
                    logging.exception("Reporter failed; using fallback text")
                    report_text = json.dumps({**fusion, "ann_probability": ann_prob}, indent=2)
            else:
                report_text = json.dumps({**fusion, "ann_probability": ann_prob}, indent=2)

            final = {"fusion_result": fusion, "report": report_text, "ann_probability": ann_prob}
            if isinstance(reply_q, queue.Queue):
                reply_q.put(final)

    def decide(self, ann_probability: float, behavioral_result: Dict[str, Any]):
        ml_decision = "FRAUD" if ann_probability >= self.threshold else "SAFE"
        behavior_decision = behavioral_result.get("decision", "NORMAL")

        if ml_decision == "FRAUD" and behavior_decision == "SUSPICIOUS":
            final_decision = "FRAUD"
            system_action = "Block transaction and notify fraud team"
            reason = "Both ANN model and behavioral agent indicate fraud."

        elif ml_decision == "FRAUD":
            final_decision = "REVIEW"
            system_action = "Send transaction for manual review"
            reason = "ANN detected fraud risk but behavior appears normal."

        elif behavior_decision == "SUSPICIOUS":
            final_decision = "REVIEW"
            system_action = "Apply additional verification"
            reason = "Behavioral agent detected anomalies despite ANN marking safe."

        else:
            final_decision = "SAFE"
            system_action = "Approve transaction"
            reason = "Both agents agree transaction is safe."

        return {
            "final_decision": final_decision,
            "ml_decision": ml_decision,
            "behavior_decision": behavior_decision,
            "reason": reason,
            "behavior_reasons": behavioral_result.get("reasons", []),
            "recommendations": behavioral_result.get("recommendations", []),
            "system_action": system_action,
        }


class ANNAgent(Agent):
    """Artificial Neural Network agent.

    Tries to load a Keras model from a file (default: 'ann_fraud_model (5).h5').
    If loading or prediction fails it falls back to a lightweight heuristic.
    Supports messages: {'type': 'predict', 'transaction': {...}, 'reply_to': Queue}
    """

    def __init__(self, model_path: str = "ann_fraud_model (5).h5"):
        super().__init__("ANNAgent")
        self.model_path = model_path
        self.model = None

    def _load_model(self):
        if self.model is not None:
            return
        try:
            import tensorflow as tf

            self.model = tf.keras.models.load_model(self.model_path)
            logging.info("ANN model loaded from %s", self.model_path)
        except Exception:
            logging.exception("Could not load ANN model - using fallback heuristic")
            self.model = None

    def handle_message(self, msg: Dict[str, Any]):
        if msg.get("type") == "predict":
            tx = msg.get("transaction", {})
            prob = self.predict(tx)
            reply_q = msg.get("reply_to")
            if isinstance(reply_q, queue.Queue):
                reply_q.put(prob)

    def predict(self, transaction: Dict[str, Any]) -> float:
        self._load_model()
        if self.model is not None:
            try:
                import numpy as np

                features = [
                    float(transaction.get("amount", 0) or 0),
                    float(transaction.get("avg_amount_user", 0) or 0),
                    float(transaction.get("shipping_distance_km", 0) or 0),
                ]
                arr = np.array([features])
                pred = self.model.predict(arr, verbose=0)
                prob = float(pred.ravel()[0])
                return max(0.0, min(1.0, prob))
            except Exception:
                logging.exception("ANN prediction failed - falling back")

        # Fallback heuristic: scaled ratio of amount vs user average with small noise
        try:
            avg = float(transaction.get("avg_amount_user", 1) or 1)
            amount = float(transaction.get("amount", 0) or 0)
            score = (amount / max(1.0, avg)) / 5.0
            score = max(0.0, min(1.0, score + random.uniform(-0.1, 0.1)))
            return score
        except Exception:
            return random.random()


class LLMReporter:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")  
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)  
            except Exception:
                logging.exception("openai package not available; reporter will use fallback")

    def generate(self, context: Dict[str, Any]) -> str:
        title = f"Fraud Analysis Report — Decision: {context.get('final_decision', 'UNKNOWN')}"

        if self.client is not None:
            try:
                prompt = (
                    "Write a concise professional fraud analysis report in plain text. "
                    "Include a short summary, the primary reasons, and recommended actions.\n\n"
                    "Context JSON:\n" + json.dumps(context, indent=2)
                )
                response = self.client.chat.completions.create(  
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                )
                text = response.choices[0].message.content.strip()
                return text
            except Exception:
                logging.exception("LLM call failed; using fallback reporter")


        # Fallback deterministic summarizer
        parts = [title, "", "Summary:"]
        parts.append(context.get("reason", "No single concise reason available."))
        parts.append("")
        parts.append(f"ML Decision: {context.get('ml_decision', '')}")
        parts.append(f"Behavior Decision: {context.get('behavior_decision', '')}")
        br = context.get("behavior_reasons", [])
        if br:
            parts.append("")
            parts.append("Behavioral reasons:")
            for r in br:
                parts.append(f"- {r}")
        recs = context.get("recommendations", [])
        if recs:
            parts.append("")
            parts.append("Recommended actions:")
            for r in recs:
                parts.append(f"- {r}")

        return "\n".join(parts)


def orchestrate_transaction(transaction: Dict[str, Any], behavioral: BehavioralRiskAgent, ann: ANNAgent, coordinator: CoordinatorAgent, reporter: LLMReporter) -> Dict[str, Any]:
    """Send messages to agents, fuse decisions, and generate a report string.

    Returns a dict with `fusion_result` and `report`.
    """
    reply_q = queue.Queue()

    # Ask behavioral agent
    behavioral.send({"type": "analyze", "transaction": transaction, "reply_to": reply_q})
    try:
        behavioral_result = reply_q.get(timeout=2.0)
    except queue.Empty:
        behavioral_result = behavioral.analyze(transaction)

    # Ask ANN agent
    reply_q2 = queue.Queue()
    ann.send({"type": "predict", "transaction": transaction, "reply_to": reply_q2})
    try:
        ann_prob = reply_q2.get(timeout=2.0)
    except queue.Empty:
        ann_prob = ann.predict(transaction)

    # Fuse decisions
    fusion = coordinator.decide(ann_probability=float(ann_prob), behavioral_result=behavioral_result)

    # Generate report
    report_text = reporter.generate({**fusion, "ann_probability": ann_prob})

    return {"fusion_result": fusion, "report": report_text}


if __name__ == "__main__":
    # Quick local demo when run as a script
    behavioral = BehavioralRiskAgent()
    ann = ANNAgent()
    reporter = LLMReporter()

    # Create coordinator with references so it can orchestrate autonomously
    coordinator = CoordinatorAgent(behavioral_agent=behavioral, ann_agent=ann, reporter=reporter, threshold=0.5)

    behavioral.start()
    ann.start()
    coordinator.start()

    sample_tx = {
        "amount": 1200,
        "avg_amount_user": 100,
        "shipping_distance_km": 800,
        "avs_match": "no",
        "cvv_result": "yes",
        "three_ds_flag": "no",
    }

    # Send the transaction to the coordinator to process autonomously
    main_q = queue.Queue()
    coordinator.send({"type": "process_transaction", "transaction": sample_tx, "reply_to": main_q})
    try:
        out = main_q.get(timeout=15.0)
        print("Fusion result:")
        print(json.dumps(out["fusion_result"], indent=2))
        print("\nGenerated report:\n")
        print(out["report"])
    except queue.Empty:
        print("Coordinator did not respond in time; exiting.")

    # Clean shutdown
    time.sleep(0.5)
    behavioral.stop()
    ann.stop()
    coordinator.stop()

