"""
Loader Module

Responsibilities:
-----------------
1. Scan Base BSP
2. Scan Vendor BSP
3. Scan Customer BSP
4. Match files by relative path
5. Read file contents
6. Return FileBundle objects
"""

from pathlib import Path

from models.file_models import FileBundle


SUPPORTED_EXTENSIONS = {
    ".dts",
    ".dtsi",
    ".patch",
    ".cfg",
    ".config",
    ".txt",
    ".c",
    ".h",
    ".conf",
}


class DatasetLoader:
    """
    Reads BSP datasets from disk.

    Expected structure:

    dataset/
        base/
        vendor/
        customer/
    """

    def __init__(self, dataset_root: str):

        self.dataset_root = Path(dataset_root)

        self.base_dir = self.dataset_root / "base"
        self.vendor_dir = self.dataset_root / "vendor"
        self.customer_dir = self.dataset_root / "customer"

    def load(self) -> list[FileBundle]:
        """
        Loads all supported files and returns FileBundle objects.
        """

        bundles = []

        # Walk through Base directory.
        # Base is treated as the source of truth for filenames.
        for base_file in self.base_dir.rglob("*"):

            if not base_file.is_file():
                continue

            if base_file.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            relative_path = base_file.relative_to(self.base_dir)

            vendor_file = self.vendor_dir / relative_path
            customer_file = self.customer_dir / relative_path

            bundle = FileBundle(
                filename=base_file.name,
                relative_path=str(relative_path),

                base_content=self._read_file(base_file),

                vendor_content=self._read_file(vendor_file),

                customer_content=self._read_file(customer_file),
            )

            bundles.append(bundle)

        return bundles

    @staticmethod
    def _read_file(file_path: Path) -> str:
        """
        Safely reads text file.

        Returns empty string if file doesn't exist.
        """

        if not file_path.exists():
            return ""

        try:
            return file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

        except Exception:
            return ""