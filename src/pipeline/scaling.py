"""
Phase 1 Integration Pipeline — Feature Scaling & Stratified Splitting

Standardization (z-score) applied after the split to prevent data leakage.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from .config import SPLIT_RATIOS, RANDOM_SEED


def stratified_split(df: pd.DataFrame, feature_cols: list) -> dict:
    """
    Split into train / val / test using stratification by
    label_category × source_dataset.

    Returns a dict with keys 'train', 'val', 'test', each containing a DataFrame.
    """
    train_ratio, val_ratio, test_ratio = SPLIT_RATIOS
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6

    strat_key = df["label_category"] + "__" + df["source_dataset"]

    min_count = strat_key.value_counts().min()
    if min_count < 2:
        print(f"  [SPLIT] Warning: smallest stratum has {min_count} samples; "
              "using label_category only for stratification")
        strat_key = df["label_category"]

    train_df, temp_df = train_test_split(
        df, test_size=(val_ratio + test_ratio),
        stratify=strat_key, random_state=RANDOM_SEED,
    )
    val_relative = val_ratio / (val_ratio + test_ratio)
    strat_key_temp = temp_df["label_category"] + "__" + temp_df["source_dataset"]
    min_count_temp = strat_key_temp.value_counts().min()
    if min_count_temp < 2:
        strat_key_temp = temp_df["label_category"]

    val_df, test_df = train_test_split(
        temp_df, test_size=(1 - val_relative),
        stratify=strat_key_temp, random_state=RANDOM_SEED,
    )

    splits = {"train": train_df, "val": val_df, "test": test_df}

    print(f"\n--- Stratified Split ---")
    for name, split_df in splits.items():
        print(f"  {name:5s}: {len(split_df):>10,} rows ({100*len(split_df)/len(df):.1f}%)")

    return splits


def apply_scaling(splits: dict, feature_cols: list) -> dict:
    """
    Apply z-score standardization.  Fit on train only, transform all partitions.
    """
    scaler = StandardScaler()
    scaler.fit(splits["train"][feature_cols])

    scaled_splits = {}
    for name, split_df in splits.items():
        split_df = split_df.copy()
        split_df[feature_cols] = scaler.transform(split_df[feature_cols])
        scaled_splits[name] = split_df

    print(f"\n--- Scaling (StandardScaler fitted on train) ---")
    print(f"  Train mean ≈ {scaled_splits['train'][feature_cols].mean().mean():.6f}")
    print(f"  Train std  ≈ {scaled_splits['train'][feature_cols].std().mean():.6f}")

    return scaled_splits, scaler


def print_split_distribution(splits: dict) -> None:
    """Show label and source distributions per split."""
    for name, split_df in splits.items():
        print(f"\n  [{name.upper()}] label_category distribution:")
        for label, count in split_df["label_category"].value_counts().items():
            pct = 100 * count / len(split_df)
            print(f"    {label:20s} {count:>8,}  ({pct:5.1f}%)")

        print(f"  [{name.upper()}] source_dataset distribution:")
        for src, count in split_df["source_dataset"].value_counts().items():
            pct = 100 * count / len(split_df)
            print(f"    {src:20s} {count:>8,}  ({pct:5.1f}%)")
