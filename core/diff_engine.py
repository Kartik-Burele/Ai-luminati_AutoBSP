"""
Diff Engine

Responsibilities
----------------
1. Generate Base -> Vendor diff
2. Generate Base -> Customer diff
3. Count additions
4. Count deletions
5. Return structured DiffSummary
"""

from difflib import unified_diff
from models.file_models import Change

from models.file_models import (
    FileBundle,
    DiffSummary,
)


class DiffEngine:

    def generate_diff(self, bundle: FileBundle) -> DiffSummary:

        vendor_diff = self._create_diff(
            bundle.base_content,
            bundle.vendor_content,
        )

        customer_diff = self._create_diff(
            bundle.base_content,
            bundle.customer_content,
        )

        vendor_add, vendor_del = self._count_changes(
            vendor_diff
        )

        customer_add, customer_del = self._count_changes(
            customer_diff
        )

        vendor_changes = self._extract_changes(
            vendor_diff
        )

        customer_changes = self._extract_changes(
            customer_diff
        )

        return DiffSummary(
            filename=bundle.filename,
            relative_path=bundle.relative_path,

            vendor_diff=vendor_diff,
            customer_diff=customer_diff,

            vendor_additions=vendor_add,
            vendor_deletions=vendor_del,

            customer_additions=customer_add,
            customer_deletions=customer_del,

            vendor_changes=vendor_changes,
            customer_changes=customer_changes,
        )

    @staticmethod
    def _create_diff(base: str, target: str) -> str:

        diff = unified_diff(
            base.splitlines(),
            target.splitlines(),

            fromfile="BASE",
            tofile="TARGET",

            lineterm=""
        )

        return "\n".join(diff)

    @staticmethod
    def _count_changes(diff_text: str):

        additions = 0
        deletions = 0

        for line in diff_text.splitlines():

            if line.startswith("+++") or line.startswith("---"):
                continue

            if line.startswith("+"):
                additions += 1

            elif line.startswith("-"):
                deletions += 1

        return additions, deletions

    def _extract_changes(self, diff_text: str):

        changes = []

        removed = None

        for line in diff_text.splitlines():

            if (
                line.startswith("---")
                or line.startswith("+++")
                or line.startswith("@@")
            ):
                continue

            if line.startswith("-"):

                removed = line[1:]

                continue

            if line.startswith("+"):

                added = line[1:]

                if removed:

                    changes.append(
                        Change(
                            change_type="MODIFIED",
                            old_line=removed.strip(),
                            new_line=added.strip(),
                        )
                    )

                    removed = None

                else:

                    changes.append(
                        Change(
                            change_type="ADDED",
                            old_line="",
                            new_line=added.strip(),
                        )
                    )

                continue

            if removed:

                changes.append(
                    Change(
                        change_type="REMOVED",
                        old_line=removed.strip(),
                        new_line="",
                    )
                )

                removed = None

        return changes