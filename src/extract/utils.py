from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

RAW_FOLDER = PROJECT_ROOT / "data" / "raw"
PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"

RAW_FOLDER.mkdir(parents=True, exist_ok=True)
PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)


def save_raw(df, filename):
    df.to_csv(RAW_FOLDER / filename, index=False)


def save_processed(df, filename):
    df.to_csv(PROCESSED_FOLDER / filename, index=False)