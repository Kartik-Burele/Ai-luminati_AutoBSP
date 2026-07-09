"""
Comparator

Determines whether a file should be sent to AI.

AI should only analyze files modified by BOTH
Vendor and Customer.
"""

from models.conflict_models import (
    ConflictCandidate,
    CandidateType,
)

from models.file_models import DiffSummary


class Comparator:

    def compare(
        self,
        diff: DiffSummary
    ) -> ConflictCandidate:

        vendor_changed = (
            diff.vendor_additions > 0
            or diff.vendor_deletions > 0
        )

        customer_changed = (
            diff.customer_additions > 0
            or diff.customer_deletions > 0
        )

        if not vendor_changed and not customer_changed:

            candidate = CandidateType.NO_CHANGE

        elif vendor_changed and customer_changed:

            candidate = CandidateType.AI_REVIEW

        else:

            candidate = CandidateType.AUTO_MERGE

        return ConflictCandidate(

            filename=diff.filename,

            relative_path=diff.relative_path,

            vendor_changed=vendor_changed,

            customer_changed=customer_changed,

            vendor_changes=diff.vendor_changes,
            
            customer_changes=diff.customer_changes,

            candidate_type=candidate,
        )