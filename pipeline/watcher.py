import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileWatcher:
    """
    Memindai folder input dan mengembalikan
    daftar file yang siap diproses.
    """

    SUPPORTED_EXTENSIONS = {".csv", ".json"}

    def __init__(self, input_dir: Path):
        self.input_dir = input_dir

    def get_pending_files(self) -> list[Path]:
        """Kembalikan semua file CSV/JSON di folder input."""
        files = [
            f for f in self.input_dir.iterdir()
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]
        logger.info(f"Ditemukan {len(files)} file di {self.input_dir}")
        return sorted(files)