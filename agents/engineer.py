import json
from dataclasses import asdict

from agents.gemini import GeminiClient
from agents.gpt import GPTClient
from agents.prompts import ENGINEER_PROMPT
from utils.json_cleaner import clean_json_response

from models.pipeline_models import PipelineContext
from models.agent_models import EngineerAnalysis
from models.conflict_models import CandidateType


class EngineerAgent:

    def __init__(self):
        # self.llm = GeminiClient()
        self.llm = GPTClient()

    def analyze_batch(
        self,
        contexts: list[PipelineContext],
    ) -> list[PipelineContext]:
        # Filter contexts that require AI analysis
        ai_review_contexts = [
            ctx for ctx in contexts
            if ctx.candidate.candidate_type == CandidateType.AI_REVIEW
        ]

        # Initialize non-conflict files with defaults
        for ctx in contexts:
            if ctx.candidate.candidate_type != CandidateType.AI_REVIEW:
                ctx.engineer = EngineerAnalysis(
                    filename=ctx.bundle.filename,
                    summary="No AI analysis required. File changes do not conflict.",
                    recommendation="Auto Merge",
                    risk="LOW",
                    confidence=100.0,
                )

        if not ai_review_contexts:
            return contexts

        # Prepare payload
        payload = []
        for ctx in ai_review_contexts:
            payload.append({
                "filename": ctx.bundle.filename,
                "vendor_changes": [asdict(c) for c in ctx.candidate.vendor_changes],
                "customer_changes": [asdict(c) for c in ctx.candidate.customer_changes],
            })

        # Format prompt
        prompt = ENGINEER_PROMPT.format(input_json=json.dumps(payload, indent=2))

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
                        results[filename] = EngineerAnalysis(
                            filename=filename,
                            summary=item.get("summary", ""),
                            recommendation=item.get("recommendation", "Manual Review"),
                            risk=item.get("risk", "HIGH"),
                            confidence=float(item.get("confidence", 80.0)),
                        )
        except Exception as e:
            # Fallback for parsing error
            print(f"[EngineerAgent] Error parsing LLM response: {e}")
            print(f"[EngineerAgent] Raw response: {response}")

        # Map results back to contexts
        for ctx in ai_review_contexts:
            filename = ctx.bundle.filename
            if filename in results:
                ctx.engineer = results[filename]
            else:
                ctx.engineer = EngineerAnalysis(
                    filename=filename,
                    summary="Failed to parse AI analysis result. Please review manually.",
                    recommendation="Manual Review",
                    risk="HIGH",
                    confidence=50.0,
                )

        return contexts
