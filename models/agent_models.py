from dataclasses import dataclass


@dataclass(slots=True)
class EngineerAnalysis:

    filename: str

    summary: str

    recommendation: str

    risk: str

    confidence: float


@dataclass(slots=True)
class ReviewerAnalysis:

    filename: str

    validation: str

    confidence: float

    risk: str


@dataclass(slots=True)
class ManagerAnalysis:

    filename: str

    effort: str           # LOW, MEDIUM, HIGH

    priority: str         # LOW, MEDIUM, HIGH

    business_impact: str

    estimated_hours: float