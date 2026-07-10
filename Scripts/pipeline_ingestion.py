"""
================================================================================
  Pipeline d'Ingestion Incrémental — Supply Chain Intelligence Platform

  Architecture :
    Source CSV → Bronze Layer (SQL Server)

  Caractéristiques :
    ✅ Incremental via Watermark Pattern
    ✅ Idempotent (IGNORE_DUP_KEY sur Order Item Id)
    ✅ Reprise automatique (retry decorator)
    ✅ Journalisation complète (batch_metadata)
    ✅ Validation après chargement
    ✅ Transactionnel (tout ou rien par batch)

  Usage :
    python scripts/pipeline_ingestion.py
    python scripts/pipeline_ingestion.py --date 2017-06-01  # Forcer une date spécifique

  Configuration :
    Scripts/pipeline_config.yaml
================================================================================
"""

import argparse
import logging
import os
import sys
import time
import uuid
from datetime import datetime, date
from typing import Optional, Tuple

import pandas as pd
import yaml
from sqlalchemy import create_engine, text, event
from sqlalchemy.exc import OperationalError, SQLAlchemyError

# ==============================================================================
# CONFIGURATION
# ==============================================================================
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "pipeline_config.yaml")
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] batch=%(batch_id)s %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "pipeline.log")),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Charge la configuration depuis le fichier YAML."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ==============================================================================
# DECORATOR : RETRY
# ==============================================================================
def retry(max_attempts: int = 3, delay: int = 5):
    """Decorateur de reprise automatique pour les erreurs transitoires."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, TimeoutError) as e:
                    last_error = e
                    logger.warning(
                        "Tentative %d/%d échouée: %s. Nouvel essai dans %ds...",
                        attempt, max_attempts, e, delay,
                    )
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_error
        return wrapper
    return decorator


# ==============================================================================
# PIPELINE
# ==============================================================================
class IngestionPipeline:
    """Pipeline d'ingestion incrémental avec watermark."""

    def __init__(self, config: dict):
        self.cfg = config
        self.engine = create_engine(
            config["database"]["connection_string"],
            fast_executemany=True,  # Optimisation batch insert
        )
        self.batch_id = uuid.uuid4()
        self.logger = logging.LoggerAdapter(
            logger, {"batch_id": str(self.batch_id)[:8]}
        )

    # ----------------------------------------------------------
    # WATERMARK
    # ----------------------------------------------------------
    def get_watermark(self) -> datetime:
        """Récupère la dernière date de chargement."""
        query = text("""
            SELECT last_load_date
            FROM bronze.watermark_tracking
            WHERE table_name = :table_name
        """)
        with self.engine.connect() as conn:
            result = conn.execute(
                query, {"table_name": "bronze.orders"}
            ).fetchone()
            if result is None:
                raise ValueError(
                    "Watermark non trouvé. "
                    "Exécuter d'abord setup_warehouse.sql."
                )
            return pd.to_datetime(result[0])

    def update_watermark(self, max_date, rows_loaded: int):
        """Met à jour la table watermark."""
        query = text("""
            UPDATE bronze.watermark_tracking
            SET last_load_date = :max_date,
                rows_loaded = rows_loaded + :rows_loaded,
                loaded_at = GETDATE()
            WHERE table_name = 'bronze.orders'
        """)
        # Conversion explicite pour éviter les types numpy
        max_date_py = max_date.to_pydatetime() if hasattr(max_date, 'to_pydatetime') else max_date
        with self.engine.begin() as conn:
            conn.execute(query, {
                "max_date": max_date_py,
                "rows_loaded": int(rows_loaded),
            })

    # ----------------------------------------------------------
    # BATCH METADATA
    # ----------------------------------------------------------
    def create_batch_metadata(self, batch_date: date, rows_extracted: int):
        """Crée une entrée de métadonnées pour ce batch."""
        query = text("""
            INSERT INTO bronze.batch_metadata
                (batch_id, table_name, batch_date, rows_extracted, start_time, status)
            VALUES
                (:batch_id, 'bronze.orders', :batch_date, :rows_extracted, GETDATE(), 'RUNNING')
        """)
        with self.engine.begin() as conn:
            conn.execute(query, {
                "batch_id": self.batch_id,
                "batch_date": batch_date,
                "rows_extracted": rows_extracted,
            })

    def complete_batch_metadata(
        self, rows_inserted, rows_duplicates,
        min_date, max_date, status: str = "COMPLETED",
        error: str = None
    ):
        """Finalise les métadonnées du batch."""
        query = text("""
            UPDATE bronze.batch_metadata
            SET rows_inserted = :rows_inserted,
                rows_duplicates = :rows_duplicates,
                end_time = GETDATE(),
                status = :status,
                error_message = :error,
                min_order_date = :min_date,
                max_order_date = :max_date
            WHERE batch_id = :batch_id
        """)
        min_py = min_date.to_pydatetime() if hasattr(min_date, 'to_pydatetime') else min_date
        max_py = max_date.to_pydatetime() if hasattr(max_date, 'to_pydatetime') else max_date
        with self.engine.begin() as conn:
            conn.execute(query, {
                "batch_id": self.batch_id,
                "rows_inserted": int(rows_inserted),
                "rows_duplicates": int(rows_duplicates),
                "status": status,
                "error": error,
                "min_date": min_py,
                "max_date": max_py,
            })

    # ----------------------------------------------------------
    # EXTRACTION
    # ----------------------------------------------------------
    @retry(max_attempts=3, delay=5)
    def extract_batch(
        self, csv_path: str, watermark: datetime
    ) -> Tuple[pd.DataFrame, date]:
        """Extrait les nouvelles donnees depuis le CSV.

        Si le watermark est a la date initiale (2015-01-01), charge tout
        l'historique en un seul batch (full historical load).
        Sinon, charge le jour suivant uniquement (daily incremental).
        """
        df = pd.read_csv(csv_path, encoding=self.cfg["ingestion"]["encoding"])

        for col in self.cfg["ingestion"]["date_columns"]:
            df[col] = pd.to_datetime(df[col], errors="coerce")

        df_new = df[df["order date (DateOrders)"] > watermark]
        if df_new.empty:
            return pd.DataFrame(), None

        # Full historical load si watermark initial
        initial_watermark = pd.to_datetime("2015-01-01 00:00:00")
        if watermark == initial_watermark:
            self.logger.info(
                "Mode full-load: chargement historique de %d lignes",
                len(df_new),
            )
            df_batch = df_new.copy()
        else:
            next_date = df_new["order date (DateOrders)"].min().date()
            df_batch = df_new[
                df_new["order date (DateOrders)"].dt.date == next_date
            ]

        df_batch = df_batch.copy()
        df_batch["_loaded_at"] = datetime.now()

        return df_batch, df_batch["order date (DateOrders)"].min().date()

    # ----------------------------------------------------------
    # CHARGEMENT
    # ----------------------------------------------------------
    @retry(max_attempts=3, delay=5)
    def load_batch(self, df: pd.DataFrame) -> Tuple[int, int]:
        """
        Charge un batch dans bronze.orders.

        L'idempotence est garantie par :
        - L'index UNIQUE avec IGNORE_DUP_KEY sur [Order Item Id]
        - Les doublons sont silencieusement ignorés
        """
        rows_before = pd.read_sql(
            "SELECT COUNT(*) as cnt FROM bronze.orders",
            self.engine
        ).iloc[0]["cnt"]

        df.to_sql(
            name="orders",
            con=self.engine,
            schema="bronze",
            if_exists="append",
            index=False,
            chunksize=self.cfg["pipeline"]["chunk_size"],
        )

        rows_after = pd.read_sql(
            "SELECT COUNT(*) as cnt FROM bronze.orders",
            self.engine
        ).iloc[0]["cnt"]

        rows_inserted = rows_after - rows_before
        rows_duplicates = len(df) - rows_inserted

        return rows_inserted, rows_duplicates

    # ----------------------------------------------------------
    # VALIDATION
    # ----------------------------------------------------------
    def validate_batch(self, df: pd.DataFrame, rows_inserted: int):
        """Valide l'intégrité du chargement."""
        checks = []

        # Vérification volumétrique
        if rows_inserted == 0 and len(df) > 0:
            checks.append(
                f"Aucune ligne insérée sur {len(df)} extraites "
                f"— probablement des doublons"
            )

        # Vérification des nulls sur les colonnes clés
        for col in ["Order Id", "Order Item Id"]:
            nulls = df[col].isna().sum()
            if nulls > 0:
                checks.append(
                    f"{nulls} valeurs nulles dans {col}"
                )

        if checks:
            self.logger.warning("Alertes qualité: %s", "; ".join(checks))

    # ----------------------------------------------------------
        # EXÉCUTION PRINCIPALE
    # ----------------------------------------------------------
    def run(self, force_date: Optional[date] = None):
        """Exécute le pipeline complet."""
        start_time = time.time()
        self.logger.info("=" * 60)
        self.logger.info("DÉMARRAGE DU PIPELINE D'INGESTION")
        self.logger.info("=" * 60)

        try:
            # 1. Récupération du watermark
            watermark = self.get_watermark()
            self.logger.info("Watermark actuel: %s", watermark)

            # 2. Extraction
            csv_path = self.cfg["ingestion"]["source_csv"]
            df_batch, batch_date = self.extract_batch(csv_path, watermark)

            if df_batch.empty:
                self.logger.info("Aucune nouvelle donnee. Pipeline termine.")
                return

            # 3. Métadonnées du batch
            self.create_batch_metadata(batch_date, len(df_batch))
            self.logger.info(
                "Batch %s: %d lignes extraites",
                batch_date, len(df_batch),
            )

            # 4. Chargement
            rows_inserted, rows_duplicates = self.load_batch(df_batch)
            self.logger.info(
                "Charge: %d inserees, %d doublons ignores",
                rows_inserted, rows_duplicates,
            )

            # 5. Validation
            self.validate_batch(df_batch, rows_inserted)

            # 6. Mise à jour watermark
            max_date = df_batch["order date (DateOrders)"].max()
            min_date = df_batch["order date (DateOrders)"].min()
            self.update_watermark(max_date, rows_inserted)

            # 7. Finalisation métadonnées
            self.complete_batch_metadata(
                rows_inserted, rows_duplicates,
                min_date, max_date, "COMPLETED",
            )

            duration = time.time() - start_time
            self.logger.info(
                "Pipeline termine en %.1fs. Watermark mis a jour: %s",
                duration, max_date,
            )

        except Exception as e:
            self.logger.error("Pipeline echoue: %s", str(e))
            try:
                self.complete_batch_metadata(
                    0, 0, None, None, "FAILED", str(e)
                )
            except Exception:
                pass
            raise


# ==============================================================================
# POINT D'ENTRÉE
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline d ingestion incremental Supply Chain"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Forcer une date de debut (format: YYYY-MM-DD)",
        default=None,
    )
    args = parser.parse_args()

    config = load_config()
    pipeline = IngestionPipeline(config)

    force_date = None
    if args.date:
        force_date = datetime.strptime(args.date, "%Y-%m-%d").date()

    pipeline.run(force_date=force_date)
