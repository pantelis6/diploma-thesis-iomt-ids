"""
Phase 1 Integration Pipeline — Dataset Export

Saves the unified dataset splits as CSV and Parquet files.
"""
import joblib
import pandas as pd

from .config import OUTPUT_DIR


def save_splits(
    splits: dict,
    scaler,
    feature_cols: list,
    near_zero_features: list,
    output_subdir: str = "phase1_iomt_unified",
    category_scheme: str = "nature",
) -> None:
    """
    Save each split as CSV and Parquet, plus metadata artifacts.
    """
    phase1_dir = OUTPUT_DIR / output_subdir
    phase1_dir.mkdir(parents=True, exist_ok=True)

    for name, split_df in splits.items():
        csv_path = phase1_dir / f"{name}.csv"
        split_df.to_csv(csv_path, index=False)
        print(f"  Saved {name}: {csv_path} ({len(split_df):,} rows)")
        try:
            parquet_path = phase1_dir / f"{name}.parquet"
            split_df.to_parquet(parquet_path, index=False)
            print(f"         + Parquet: {parquet_path}")
        except ImportError:
            pass

    scaler_path = phase1_dir / "scaler.joblib"
    joblib.dump(scaler, scaler_path)
    print(f"  Saved scaler: {scaler_path}")

    meta = {
        "feature_cols": feature_cols,
        "near_zero_variance_features": near_zero_features,
        "split_sizes": {name: len(df) for name, df in splits.items()},
        "category_scheme": category_scheme,
    }
    meta_path = phase1_dir / "metadata.joblib"
    joblib.dump(meta, meta_path)
    print(f"  Saved metadata: {meta_path}")

    print(f"\n  All Phase 1 artifacts saved to: {phase1_dir}")
