import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataTransformer:
    """Membersihkan dan menormalisasi data."""

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Memulai transformasi data...")
        df = df.copy()

        df = self._normalize_text(df)
        df = self._cast_types(df)
        df = self._remove_duplicates(df)

        logger.info(f"Transformasi selesai: {len(df)} baris")
        return df

    def _normalize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalisasi kolom teks."""
        if "status" in df.columns:
            df["status"] = df["status"].str.lower().str.strip()
        if "customer_id" in df.columns:
            df["customer_id"] = df["customer_id"].str.strip()
        return df

    def _cast_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cast tipe data yang benar."""
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        if "transaction_date" in df.columns:
            df["transaction_date"] = pd.to_datetime(
                df["transaction_date"], errors="coerce"
            )
        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Hapus baris duplikat berdasarkan transaction_id."""
        before = len(df)
        if "transaction_id" in df.columns:
            df = df.drop_duplicates(subset=["transaction_id"], keep="first")
        after = len(df)
        if before != after:
            logger.warning(f"Hapus {before - after} baris duplikat")
        return df