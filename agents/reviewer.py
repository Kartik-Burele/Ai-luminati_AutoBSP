import json
from dataclasses import asdict

from agents.gemini import GeminiClient
from agents.gpt import GPTClient
from agents.prompts import REVIEWER_PROMPT
from utils.json_cleaner import clean_json_response

from models.pipeline_models import PipelineContext
from models.agent_models import ReviewerAnalysis
from models.conflict_models import CandidateType


class ReviewerAgent:

    def __init__(self):
        # self.llm = GeminiClient()
        self.llm = GPTClient()

    def analyze_batch(
        self,
        contexts: list[PipelineContext],
    ) -> list[PipelineContext]:
        # Filter contexts that require AI analysis and have engineer analysis populated
        ai_review_contexts = [
            ctx for ctx in contexts
            if ctx.candidate.candidate_type == CandidateType.AI_REVIEW
        ]

        # Initialize non-conflict files with defaults
        for ctx in contexts:
            if ctx.candidate.candidate_type != CandidateType.AI_REVIEW:
                ctx.reviewer = ReviewerAnalysis(
                    filename=ctx.bundle.filename,
                    validation="Validation passed. Code changes do not conflict.",
                    confidence=100.0,
                    risk="LOW",
                )

        if not ai_review_contexts:
            return contexts

        # Prepare payload
        payload = []
        for ctx in ai_review_contexts:
            eng_summary = ctx.engineer.summary if ctx.engineer else ""
            eng_rec = ctx.engineer.recommendation if ctx.engineer else ""
            
            payload.append({
                "filename": ctx.bundle.filename,
                "vendor_changes": [asdict(c) for c in ctx.candidate.vendor_changes],
                "customer_changes": [asdict(c) for c in ctx.candidate.customer_changes],
                "engineer_summary": eng_summary,
                "engineer_recommendation": eng_rec,
            })

        # Format prompt
        prompt = REVIEWER_PROMPT.format(input_json=json.dumps(payload, indent=2))

        # Query LLM
        response = self.llm.generate(prompt, mime_type="application/json")


        # Parse JSON
        results = {}
        try:
            cleaned_response = clean_json_response(response)

            data = json.loads(cleaned_response)
            if isinstance(data, dict):
                if "filename" in data:
                    data = [data]
                else:
                    for val in data.values():
                        if isinstance(val, list):
                            data = val
                            break
            
            if isinstance(data, list):
                for item in data:
                    filename = item.get("filename")
                    if filename:
                        results[filename] = ReviewerAnalysis(
                            filename=filename,
                            validation=item.get("validation", ""),
                            confidence=float(item.get("confidence", 80.0)),
                            risk=item.get("risk", "HIGH"),
                        )
        except Exception as e:
            print(f"[ReviewerAgent] Error parsing LLM response: {e}")
            print(f"[ReviewerAgent] Raw response: {response}")

        # Map results back to contexts
        for ctx in ai_review_contexts:
            filename = ctx.bundle.filename
            if filename in results:
                ctx.reviewer = results[filename]
            else:
                ctx.reviewer = ReviewerAnalysis(
                    filename=filename,
                    validation="Failed to parse reviewer verification. Manual review required.",
                    confidence=50.0,
                    risk="HIGH",
                )

        return contexts
