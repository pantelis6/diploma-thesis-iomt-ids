"""
Phase 1 Integration Pipeline — Label Harmonization

Applies the three-level labeling scheme defined in Chapter 3.
"""
import pandas as pd

from .config import (
    CICIOMT_CATEGORY_MAP,
    CICIOMT_CATEGORY_MAP_MQTT,
    IOMT_CATEGORY_MAP,
    IOMT_CATEGORY_MAP_MQTT,
    IOMT_FINE_MAP,
)


def _binary_label(category: str) -> str:
    return "Benign" if category == "Benign" else "Attack"


def _resolve_maps(category_scheme: str):
    """Return category maps for the selected scheme."""
    if category_scheme == "nature":
        return CICIOMT_CATEGORY_MAP, IOMT_CATEGORY_MAP
    if category_scheme == "mqtt":
        return CICIOMT_CATEGORY_MAP_MQTT, IOMT_CATEGORY_MAP_MQTT
    raise ValueError(f"Unknown category scheme: {category_scheme}")


def harmonize_ciciomt2024(df: pd.DataFrame, category_scheme: str = "nature") -> pd.DataFrame:
    """Add label_binary, label_category, label_fine to CICIoMT2024 data."""
    ciciomt_map, _ = _resolve_maps(category_scheme)
    unmapped = set(df["attack_group"].unique()) - set(ciciomt_map.keys())
    if unmapped:
        raise ValueError(f"Unmapped CICIoMT2024 attack groups: {unmapped}")

    df = df.copy()
    df["label_category"] = df["attack_group"].map(ciciomt_map)
    df["label_binary"] = df["label_category"].apply(_binary_label)
    df["label_fine"] = df["attack_group"]
    return df


def harmonize_iomt_trafficdata(df: pd.DataFrame, category_scheme: str = "nature") -> pd.DataFrame:
    """Add label_binary, label_category, label_fine to IoMT-TrafficData."""
    _, iomt_map = _resolve_maps(category_scheme)
    unmapped = set(df["attack_type"].unique()) - set(iomt_map.keys())
    if unmapped:
        raise ValueError(f"Unmapped IoMT-TrafficData attack types: {unmapped}")

    df = df.copy()
    df["label_category"] = df["attack_type"].map(iomt_map)
    df["label_binary"] = df["label_category"].apply(_binary_label)
    df["label_fine"] = df["attack_type"].map(IOMT_FINE_MAP)
    return df


def print_label_summary(df: pd.DataFrame, dataset_name: str) -> None:
    """Print a summary of the three-level label distribution."""
    print(f"\n{'='*60}")
    print(f"Label Summary: {dataset_name}")
    print(f"{'='*60}")

    print(f"\n--- Level 1: Binary ---")
    for label, count in df["label_binary"].value_counts().items():
        pct = 100 * count / len(df)
        print(f"  {label:15s} {count:>10,}  ({pct:6.2f}%)")

    print(f"\n--- Level 2: Category ---")
    for label, count in df["label_category"].value_counts().items():
        pct = 100 * count / len(df)
        print(f"  {label:20s} {count:>10,}  ({pct:6.2f}%)")

    print(f"\n--- Level 3: Fine-grained ---")
    for label, count in df["label_fine"].value_counts().items():
        pct = 100 * count / len(df)
        print(f"  {label:30s} {count:>10,}  ({pct:6.2f}%)")
