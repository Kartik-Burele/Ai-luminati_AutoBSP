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

from models.file_models import DiffSummary, FileBundle
from core.dts_parser import parse_dts_nodes, get_modified_nodes


class Comparator:

    def compare(
        self,
        diff: DiffSummary,
        bundle: FileBundle = None
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

            # Check if this is a DTS/DTSI file and we have raw content to analyze nodes
            if bundle and (diff.filename.endswith(".dts") or diff.filename.endswith(".dtsi")):
                try:
                    base_nodes = parse_dts_nodes(bundle.base_content)
                    vendor_nodes = parse_dts_nodes(bundle.vendor_content)
                    customer_nodes = parse_dts_nodes(bundle.customer_content)
                    
                    vendor_mod = get_modified_nodes(base_nodes, vendor_nodes)
                    customer_mod = get_modified_nodes(base_nodes, customer_nodes)
                    
                    intersecting = vendor_mod.intersection(customer_mod)
                    if not intersecting:
                        candidate = CandidateType.AUTO_MERGE
                    else:
                        candidate = CandidateType.AI_REVIEW
                except Exception as e:
                    print(f"[Comparator] DTS parser warning for {diff.filename}: {e}")
                    candidate = CandidateType.AI_REVIEW
            else:
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