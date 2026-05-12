"""
Phase 1 Integration Pipeline — Data Loading

Loads MIOTTA-processed CSV files and infers attack labels from filenames.
"""
import re
from pathlib import Path
from typing import Tuple

import pandas as pd

from .config import (
    CICIOMT_TRAIN_DIR, CICIOMT_TEST_DIR, IOMT_DIR, META_COLS,
)


def _infer_label(filename: str, prefix_to_strip: str = "", suffix_to_strip: str = "") -> str:
    """Extract an attack label from a MIOTTA CSV filename."""
    name = Path(filename).stem
    if prefix_to_strip:
        name = name.replace(prefix_to_strip, "")
    if suffix_to_strip:
        name = name.replace(suffix_to_strip, "")
    return name.strip("_").strip()


def _normalize_attack_group(label: str) -> str:
    """Collapse sub-variant suffixes (e.g. TCP_IP-DDoS-ICMP3 → TCP_IP-DDoS-ICMP)."""
    return re.sub(r"\d+$", "", label).rstrip("_").rstrip("-")


def _load_directory(directory: Path, source_dataset: str,
                    prefix_to_strip: str = "", suffix_to_strip: str = "") -> pd.DataFrame:
    """Load every CSV in *directory*, tag rows with attack_type and source."""
    frames = []
    for csv_path in sorted(directory.glob("*.csv")):
        label = _infer_label(csv_path.name, prefix_to_strip, suffix_to_strip)
        df = pd.read_csv(csv_path, low_memory=False)
        df["attack_type"] = label
        df["source_file"] = csv_path.name
        df["source_dataset"] = source_dataset
        frames.append(df)
        print(f"  {csv_path.name:60s} → label='{label:25s}' rows={len(df):>8,}")
    return pd.concat(frames, ignore_index=True)


def load_ciciomt2024() -> pd.DataFrame:
    """Load both train and test MIOTTA-processed CICIoMT2024 CSVs."""
    print("Loading CICIoMT2024-MIOTTA (train)...")
    train = _load_directory(CICIOMT_TRAIN_DIR, "CICIoMT2024", suffix_to_strip="_train")

    print("\nLoading CICIoMT2024-MIOTTA (test)...")
    test = _load_directory(CICIOMT_TEST_DIR, "CICIoMT2024",
                           prefix_to_strip="estadisticas_combinadas_", suffix_to_strip="_test")

    combined = pd.concat([train, test], ignore_index=True)
    combined["attack_group"] = combined["attack_type"].apply(_normalize_attack_group)
    print(f"\nCICIoMT2024 total: {len(combined):,} rows × {combined.shape[1]} columns")
    return combined


def load_iomt_trafficdata() -> pd.DataFrame:
    """Load MIOTTA-processed IoMT-TrafficData CSVs."""
    print("Loading IoMT-TrafficData-MIOTTA...")
    df = _load_directory(IOMT_DIR, "IoMT-TrafficData",
                         prefix_to_strip="estadisticas_combinadas_")
    df["attack_group"] = df["attack_type"]
    print(f"\nIoMT-TrafficData total: {len(df):,} rows × {df.shape[1]} columns")
    return df


def get_feature_columns(df: pd.DataFrame) -> list:
    """Return the list of numeric feature columns (excluding metadata)."""
    return [c for c in df.columns if c not in META_COLS + ["attack_group"]]
