
import logging
import os
from pathlib import Path
from datetime import datetime

from api_pipeline.dummyjson_client import (
    fetch_products,
    fetch_users,
    fetch_carts
)

from api_pipeline.transform import transform_all
from api_pipeline.data_quality import check_data_quality
from api_pipeline.load_mysql import load_data


# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Log directory
LOG_DIR = BASE_DIR / "jobs" / "scheduler_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "daily_api_job.log"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True
)

logger = logging.getLogger("QueryPilotDailyJob")


def run_daily_job():

    start_time = datetime.now()

    logger.info("=" * 60)
    logger.info("QueryPilot daily API job started")

    try:

        # STEP 1: Fetch API data
        logger.info("Fetching DummyJSON data...")

        products = fetch_products()
        users = fetch_users()
        carts = fetch_carts()

        logger.info(
            "Fetched products=%s, users=%s, carts=%s",
            len(products),
            len(users),
            len(carts)
        )

        # STEP 2: Transform data
        logger.info("Transforming API data...")

        transformed = transform_all(
            products,
            users,
            carts
        )

        # STEP 3: Data quality checks
        logger.info("Running data quality checks...")

        report = check_data_quality(transformed)

        if report["status"] != "PASSED":
            raise ValueError(
                f"Data quality checks failed: {report['errors']}"
            )

        logger.info("Data quality checks passed")

        # STEP 4: Load into MySQL
        logger.info("Loading data into MySQL...")

        load_data(transformed)

        # STEP 5: Execution summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("Job completed successfully")
        logger.info("Execution duration: %.2f seconds", duration)
        logger.info("=" * 60)

        return True

    except Exception:

        logger.exception("Daily API job failed")
        logger.info("=" * 60)

        return False


if __name__ == "__main__":

    success = run_daily_job()

    if not success:
        raise SystemExit(1)
