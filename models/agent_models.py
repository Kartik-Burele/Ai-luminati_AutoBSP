from dataclasses import dataclass


@dataclass(slots=True)
class EngineerAnalysis:

    filename: str

    summary: str

    recommendation: str

    risk: str

    confidence: float