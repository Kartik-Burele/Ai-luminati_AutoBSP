from dataclasses import dataclass

from models.file_models import FileBundle, DiffSummary
from models.conflict_models import ConflictCandidate
from models.agent_models import EngineerAnalysis, ReviewerAnalysis, ManagerAnalysis


@dataclass(slots=True)
class PipelineContext:

    bundle: FileBundle

    diff: DiffSummary

    candidate: ConflictCandidate

    engineer: EngineerAnalysis | None = None

    reviewer: ReviewerAnalysis | None = None

    manager: ManagerAnalysis | None = None