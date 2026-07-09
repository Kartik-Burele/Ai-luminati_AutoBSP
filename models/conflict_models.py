from dataclasses import dataclass
from enum import Enum

from models.file_models import Change


class CandidateType(Enum):
    NO_CHANGE = "NO_CHANGE"
    AUTO_MERGE = "AUTO_MERGE"
    AI_REVIEW = "AI_REVIEW"


@dataclass(slots=True)
class ConflictCandidate:

    filename: str
    relative_path: str

    vendor_changed: bool
    customer_changed: bool

    vendor_changes: list[Change]
    customer_changes: list[Change]

    candidate_type: CandidateType