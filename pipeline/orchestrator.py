import logging
import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime

from config import DatabaseConfig, PathConfig
from watcher import FileWatcher
from validator import FileValidator
from transformer import DataTransformer
from loader import DataLoader

# Setup logging ke file + console sekaligus
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(
            PathConfig.LOG_DIR / f"pipeline_{datetime.now():%Y%m%d}.log"
        ),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """
    Mengorkestrasi seluruh pipeline:
    watcher → validator → transformer → loader
    """

    def __init__(self):
        PathConfig.ensure_dirs()
        self.watcher     = FileWatcher(PathConfig.INPUT_DIR)
        self.validator   = FileValidator()
        self.transformer = DataTransformer()
        self.loader      = DataLoader(DatabaseConfig.get_connection_string())
        self.loader.create_table_if_not_exists()

    def _read_file(self, file_path: Path) -> pd.DataFrame:
        """Baca file CSV atau JSON."""
        if file_path.suffix.lower() == ".csv":
            return pd.read_csv(file_path)
        elif file_path.suffix.lower() == ".json":
            return pd.read_json(file_path)
        raise ValueError(f"Format tidak didukung: {file_path.suffix}")

    def _move_to_archive(self, file_path: Path) -> None:
        dest = PathConfig.ARCHIVE_DIR / file_path.name
        shutil.move(str(file_path), str(dest))
        logger.info(f"Arsip: {file_path.name} → archive/")

    def _move_to_quarantine(self, file_path: Path, errors: list[str]) -> None:
        dest = PathConfig.QUARANTINE_DIR / file_path.name
        shutil.move(str(file_path), str(dest))
        logger.warning(f"Karantina: {file_path.name} → quarantine/ | Alasan: {errors}")

    def run(self) -> None:
        logger.info("=" * 50)
        logger.info("Pipeline dimulai")

        files = self.watcher.get_pending_files()

        if not files:
            logger.info("Tidak ada file baru. Pipeline selesai.")
            return

        success, failed = 0, 0

        for file_path in files:
            logger.info(f"Memproses: {file_path.name}")
            try:
                # 1. Baca file
                df = self._read_file(file_path)

                # 2. Validasi
                result = self.validator.validate(df, file_path.name)
                if not result.is_valid:
                    self._move_to_quarantine(file_path, result.errors)
                    failed += 1
                    continue

                # 3. Transform
                df = self.transformer.transform(df)

                # 4. Load
                self.loader.upsert(df)

                # 5. Arsipkan file yang berhasil
                self._move_to_archive(file_path)
                success += 1

            except Exception as e:
                logger.error(f"Error tak terduga saat proses {file_path.name}: {e}")
                self._move_to_quarantine(file_path, [str(e)])
                failed += 1

        logger.info(f"Pipeline selesai — Berhasil: {success} | Gagal: {failed}")
        logger.info("=" * 50)


if __name__ == "__main__":
    PipelineOrchestrator().run()