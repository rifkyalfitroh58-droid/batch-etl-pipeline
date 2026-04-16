import pandas as pd
import logging
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Schema yang diharapkan: {nama_kolom: tipe_data}
EXPECTED_SCHEMA = {
    "transaction_id": "object",
    "customer_id":    "object",
    "amount":         "float64",
    "transaction_date": "object",
    "status":         "object",
}

VALID_STATUSES = {"completed", "pending", "failed", "refunded"}


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


class FileValidator:
    """Validasi schema dan kualitas data sebelum diproses."""

    def validate(self, df: pd.DataFrame, file_name: str) -> ValidationResult:
        errors = []

        # 1. Cek kolom wajib ada
        missing_cols = set(EXPECTED_SCHEMA.keys()) - set(df.columns)
        if missing_cols:
            errors.append(f"Kolom tidak ditemukan: {missing_cols}")

        # 2. Cek tidak ada baris kosong di kolom kritis
        for col in ["transaction_id", "customer_id", "amount"]:
            if col in df.columns and df[col].isnull().any():
                null_count = df[col].isnull().sum()
                errors.append(f"Kolom '{col}' punya {null_count} nilai null")

        # 3. Cek nilai status valid
        if "status" in df.columns:
            invalid_status = set(df["status"].unique()) - VALID_STATUSES
            if invalid_status:
                errors.append(f"Nilai status tidak valid: {invalid_status}")

        # 4. Cek amount tidak negatif
        if "amount" in df.columns:
            try:
                df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
                if (df["amount"] < 0).any():
                    errors.append("Ditemukan nilai amount negatif")
            except Exception:
                errors.append("Kolom amount tidak bisa dikonversi ke angka")

        if errors:
            logger.warning(f"[{file_name}] Validasi GAGAL: {errors}")
        else:
            logger.info(f"[{file_name}] Validasi BERHASIL")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)