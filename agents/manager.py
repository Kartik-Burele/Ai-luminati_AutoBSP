import json

from agents.gemini import GeminiClient
from agents.gpt import GPTClient
from agents.prompts import MANAGER_PROMPT
from utils.json_cleaner import clean_json_response

from models.pipeline_models import PipelineContext
from models.agent_models import ManagerAnalysis
from models.conflict_models import CandidateType


class ManagerAgent:

    def __init__(self):
        # self.llm = GeminiClient()
        self.llm = GPTClient()

    def analyze_batch(
        self,
        contexts: list[PipelineContext],
    ) -> list[PipelineContext]:
        # Filter contexts that require AI analysis and have engineer/reviewer analysis populated
        ai_review_contexts = [
            ctx for ctx in contexts
            if ctx.candidate.candidate_type == CandidateType.AI_REVIEW
        ]

        # Initialize non-conflict files with defaults
        for ctx in contexts:
            if ctx.candidate.candidate_type != CandidateType.AI_REVIEW:
                ctx.manager = ManagerAnalysis(
                    filename=ctx.bundle.filename,
                    effort="LOW",
                    priority="LOW",
                    business_impact="No impact. Automatic merge possible.",
                    estimated_hours=0.0,
                )

        if not ai_review_contexts:
            return contexts

        # Prepare payload
        payload = []
        for ctx in ai_review_contexts:
            eng_rec = ctx.engineer.recommendation if ctx.engineer else ""
            eng_risk = ctx.engineer.risk if ctx.engineer else ""
            rev_val = ctx.reviewer.validation if ctx.reviewer else ""
            rev_risk = ctx.reviewer.risk if ctx.reviewer else ""
            
            payload.append({
                "filename": ctx.bundle.filename,
                "engineer_recommendation": eng_rec,
                "engineer_risk": eng_risk,
                "reviewer_validation": rev_val,
                "reviewer_risk": rev_risk,
            })

        # Format prompt
        prompt = MANAGER_PROMPT.format(input_json=json.dumps(payload, indent=2))

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
                        results[filename] = ManagerAnalysis(
                            filename=filename,
                            effort=item.get("effort", "HIGH"),
                            priority=item.get("priority", "HIGH"),
                            business_impact=item.get("business_impact", ""),
                            estimated_hours=float(item.get("estimated_hours", 2.0)),
                        )
        except Exception as e:
            print(f"[ManagerAgent] Error parsing LLM response: {e}")
            print(f"[ManagerAgent] Raw response: {response}")

        # Map results back to contexts
        for ctx in ai_review_contexts:
            filename = ctx.bundle.filename
            if filename in results:
                ctx.manager = results[filename]
            else:
                ctx.manager = ManagerAnalysis(
                    filename=filename,
                    effort="HIGH",
                    priority="HIGH",
                    business_impact="Failed to parse PM metrics. Requires manual estimation.",
                    estimated_hours=4.0,
                )

        return contexts
