import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    HOST: str     = os.getenv("DB_HOST", "localhost")
    PORT: int     = int(os.getenv("DB_PORT", 5432))
    NAME: str     = os.getenv("DB_NAME", "batch_etl_db")
    USER: str     = os.getenv("DB_USER", "postgres")
    PASSWORD: str = os.getenv("DB_PASSWORD", "")

    @classmethod
    def get_connection_string(cls) -> str:
        return (
            f"postgresql://{cls.USER}:{cls.PASSWORD}"
            f"@{cls.HOST}:{cls.PORT}/{cls.NAME}"
        )


class PathConfig:
    BASE_DIR    = Path(__file__).resolve().parent.parent
    INPUT_DIR   = BASE_DIR / "input"
    ARCHIVE_DIR = BASE_DIR / "archive"
    QUARANTINE_DIR = BASE_DIR / "quarantine"
    LOG_DIR     = BASE_DIR / "logs"

    @classmethod
    def ensure_dirs(cls) -> None:
        """Buat semua folder jika belum ada."""
        for d in [cls.INPUT_DIR, cls.ARCHIVE_DIR, cls.QUARANTINE_DIR, cls.LOG_DIR]:
            d.mkdir(parents=True, exist_ok=True)