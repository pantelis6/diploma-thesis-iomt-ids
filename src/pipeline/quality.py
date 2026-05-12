"""
Phase 1 Integration Pipeline — Data Quality Assurance

Missing-value treatment, infinity handling, zero-variance removal,
duplicate detection, and type consistency checks.
"""
import numpy as np
import pandas as pd

from .config import NAN_THRESHOLD, NEAR_ZERO_VAR_THRESHOLD


def _report(msg: str) -> None:
    print(f"  [QA] {msg}")


def treat_missing_values(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """
    Handle NaN values:
      - Drop features with NaN rate > NAN_THRESHOLD
      - Impute remaining NaNs with 0 (protocol-absence pattern)
    """
    df = df.copy()
    nan_rates = df[feature_cols].isna().mean()
    high_nan = nan_rates[nan_rates > NAN_THRESHOLD]

    if len(high_nan) > 0:
        _report(f"Dropping {len(high_nan)} features with NaN rate > {NAN_THRESHOLD}:")
        for col, rate in high_nan.items():
            _report(f"    {col}: {rate:.2%}")
        df = df.drop(columns=high_nan.index.tolist())
        feature_cols = [c for c in feature_cols if c not in high_nan.index]

    remaining_nan = df[feature_cols].isna().sum().sum()
    if remaining_nan > 0:
        _report(f"Imputing {remaining_nan:,} remaining NaN values with 0")
        df[feature_cols] = df[feature_cols].fillna(0)
    else:
        _report("No remaining NaN values")

    return df, feature_cols


def handle_infinity_values(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """Replace ±inf with per-column finite max/min."""
    df = df.copy()
    inf_count = np.isinf(df[feature_cols].select_dtypes(include=[np.number])).sum().sum()
    if inf_count > 0:
        _report(f"Replacing {inf_count:,} infinity values")
        for col in feature_cols:
            if df[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
                mask_pos = df[col] == np.inf
                mask_neg = df[col] == -np.inf
                if mask_pos.any():
                    finite_max = df.loc[~mask_pos & ~mask_neg, col].max()
                    df.loc[mask_pos, col] = finite_max
                if mask_neg.any():
                    finite_min = df.loc[~mask_pos & ~mask_neg, col].min()
                    df.loc[mask_neg, col] = finite_min
    else:
        _report("No infinity values found")
    return df


def remove_zero_variance(df: pd.DataFrame, feature_cols: list) -> tuple:
    """Remove features with exactly zero variance."""
    variances = df[feature_cols].var(numeric_only=True)
    zero_var = variances[variances == 0].index.tolist()

    if zero_var:
        _report(f"Removing {len(zero_var)} zero-variance features: {zero_var}")
        df = df.drop(columns=zero_var)
        feature_cols = [c for c in feature_cols if c not in zero_var]
    else:
        _report("No zero-variance features found")

    return df, feature_cols


def detect_near_zero_variance(df: pd.DataFrame, feature_cols: list) -> list:
    """Flag features with variance below NEAR_ZERO_VAR_THRESHOLD."""
    variances = df[feature_cols].var(numeric_only=True)
    near_zero = variances[
        (variances > 0) & (variances < NEAR_ZERO_VAR_THRESHOLD)
    ].index.tolist()

    if near_zero:
        _report(f"Near-zero-variance features ({len(near_zero)} flagged): {near_zero}")
    else:
        _report("No near-zero-variance features detected")

    return near_zero


def remove_duplicates(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """Remove exact duplicate rows based on feature columns only."""
    before = len(df)
    df = df.drop_duplicates(subset=feature_cols, keep="first")
    removed = before - len(df)
    pct = 100 * removed / before if before > 0 else 0
    _report(f"Removed {removed:,} duplicate rows ({pct:.2f}%)")
    return df


def ensure_type_consistency(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """Cast all numeric features to float32 for memory efficiency and consistency."""
    df = df.copy()
    converted = 0
    for col in feature_cols:
        if df[col].dtype != np.float32:
            df[col] = df[col].astype(np.float32)
            converted += 1
    _report(f"Converted {converted} columns to float32")
    return df


def run_full_qa(df: pd.DataFrame, feature_cols: list) -> tuple:
    """Execute the complete quality assurance pipeline."""
    print("\n" + "=" * 60)
    print("Data Quality Assurance Pipeline")
    print("=" * 60)

    print("\n--- Step 1: Missing Value Treatment ---")
    df, feature_cols = treat_missing_values(df, feature_cols)

    print("\n--- Step 2: Infinity Value Handling ---")
    df = handle_infinity_values(df, feature_cols)

    print("\n--- Step 3: Zero-Variance Feature Removal ---")
    df, feature_cols = remove_zero_variance(df, feature_cols)

    print("\n--- Step 4: Near-Zero-Variance Detection ---")
    near_zero = detect_near_zero_variance(df, feature_cols)

    print("\n--- Step 5: Duplicate Removal ---")
    df = remove_duplicates(df, feature_cols)

    print("\n--- Step 6: Type Consistency ---")
    df = ensure_type_consistency(df, feature_cols)

    print(f"\n--- QA Complete ---")
    print(f"  Final shape: {df.shape[0]:,} rows × {len(feature_cols)} features")
    return df, feature_cols, near_zero
