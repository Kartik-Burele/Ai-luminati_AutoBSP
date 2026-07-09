import json

from agents.gemini import GeminiClient
from agents.prompts import ENGINEER_PROMPT

from models.pipeline_models import PipelineContext
from models.agent_models import EngineerAnalysis
from models.conflict_models import CandidateType


class EngineerAgent:

    def __init__(self):

        self.llm = GeminiClient()

    def analyze(
        self,
        context: PipelineContext,
    ) -> PipelineContext:

        if context.candidate.candidate_type != CandidateType.AI_REVIEW:

            context.engineer = EngineerAnalysis(
                filename=context.bundle.filename,
                summary="No AI analysis required.",
                recommendation="Auto Merge",
                risk="LOW",
                confidence=100.0,
            )

            return context

        prompt = ENGINEER_PROMPT.format(

            filename=context.bundle.filename,

            vendor_changes=context.candidate.vendor_changes,

            customer_changes=context.candidate.customer_changes,
        )

        response = self.llm.generate(prompt)

        try:

            data = json.loads(response)

        except Exception:

            context.engineer = EngineerAnalysis(
                filename=context.bundle.filename,
                summary=response,
                recommendation="Manual Review",
                risk="UNKNOWN",
                confidence=50.0,
            )

            return context

        context.engineer = EngineerAnalysis(

            filename=context.bundle.filename,

            summary=data.get("summary", ""),

            recommendation=data.get(
                "recommendation",
                "",
            ),

            risk=data.get("risk", ""),

            confidence=float(
                data.get(
                    "confidence",
                    80,
                )
            ),
        )

        return context