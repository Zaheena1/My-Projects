from openai import OpenAI
import os

class LLMDecisionAgent:
    def __init__(self):
        # Read API key from environment variable
        self.client = OpenAI(api_key=os.getenv("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"))

    def decide(self, ann_probability, behavioral_result, transaction_data):
        prompt = f"""
You are an AI fraud analysis agent.

ANN fraud probability: {ann_probability}

Behavioral agent result:
{behavioral_result}

Transaction data:
{transaction_data}

Explain whether the transaction is SAFE, FRAUD, or needs REVIEW.
Give a short human-style explanation.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert fraud analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content
