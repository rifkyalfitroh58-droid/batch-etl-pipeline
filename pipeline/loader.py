import pandas as pd
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Load data ke PostgreSQL dengan metode upsert."""

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)

    def create_table_if_not_exists(self) -> None:
        """Buat tabel jika belum ada."""
        query = """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id   VARCHAR PRIMARY KEY,
            customer_id      VARCHAR NOT NULL,
            amount           NUMERIC(12, 2),
            transaction_date TIMESTAMP,
            status           VARCHAR,
            loaded_at        TIMESTAMP DEFAULT NOW()
        );
        """
        with self.engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()
        logger.info("Tabel 'transactions' siap.")

    def upsert(self, df: pd.DataFrame) -> int:
        """
        Upsert data — update jika sudah ada, insert jika belum.
        Return jumlah baris yang berhasil diproses.
        """
        if df.empty:
            logger.warning("DataFrame kosong, skip upsert.")
            return 0

        # Load ke staging table dulu
        df.to_sql(
            "transactions_staging",
            con=self.engine,
            if_exists="replace",
            index=False
        )

        # Upsert dari staging ke tabel utama
        upsert_query = """
        INSERT INTO transactions (
            transaction_id, customer_id, amount,
            transaction_date, status
        )
        SELECT
            transaction_id, customer_id, amount,
            transaction_date, status
        FROM transactions_staging
        ON CONFLICT (transaction_id)
        DO UPDATE SET
            amount           = EXCLUDED.amount,
            status           = EXCLUDED.status,
            transaction_date = EXCLUDED.transaction_date,
            loaded_at        = NOW();
        """
        with self.engine.connect() as conn:
            conn.execute(text(upsert_query))
            conn.commit()

        logger.info(f"Upsert {len(df)} baris ke tabel transactions.")
        return len(df)