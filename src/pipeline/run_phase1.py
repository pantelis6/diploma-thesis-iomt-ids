"""
Phase 1 Integration Pipeline — Main Runner

Execute the complete Phase 1 unification pipeline for CICIoMT2024 + IoMT-TrafficData.
"""
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from pipeline.loader import load_ciciomt2024, load_iomt_trafficdata, get_feature_columns
from pipeline.harmonizer import harmonize_ciciomt2024, harmonize_iomt_trafficdata, print_label_summary
from pipeline.quality import run_full_qa
from pipeline.scaling import stratified_split, apply_scaling, print_split_distribution
from pipeline.exporter import save_splits


def parse_args():
    parser = argparse.ArgumentParser(description="Run Phase 1 IoMT unification pipeline.")
    parser.add_argument(
        "--category-scheme",
        choices=["nature", "mqtt"],
        default="nature",
        help="Label category strategy: 'nature' (existing) or 'mqtt' (dedicated MQTT category).",
    )
    parser.add_argument(
        "--output-subdir",
        default=None,
        help="Output subdirectory under data/processed/. If omitted, derived from category scheme.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    category_scheme = args.category_scheme
    output_subdir = args.output_subdir or (
        "phase1_iomt_unified" if category_scheme == "nature"
        else "phase1_iomt_unified_mqtt_category"
    )

    t0 = time.time()
    print("=" * 70)
    print("PHASE 1: IoMT Dataset Unification Pipeline")
    print("=" * 70)
    print(f"Category scheme: {category_scheme}")
    print(f"Output subdir:   {output_subdir}")

    # ── Stage 1: Load ─────────────────────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("STAGE 1: Data Loading & Source Attribution")
    print("=" * 70)
    cic = load_ciciomt2024()
    iomt = load_iomt_trafficdata()

    # ── Stage 2: Feature Verification ─────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("STAGE 2: Cross-Dataset Feature Verification")
    print("=" * 70)
    cic_feats = get_feature_columns(cic)
    iomt_feats = get_feature_columns(iomt)
    print(f"CICIoMT2024 features:      {len(cic_feats)}")
    print(f"IoMT-TrafficData features: {len(iomt_feats)}")
    if set(cic_feats) == set(iomt_feats):
        print("✓ Feature sets are IDENTICAL")
    else:
        diff = set(cic_feats).symmetric_difference(set(iomt_feats))
        print(f"✗ MISMATCH: {diff}")
    if list(cic_feats) == list(iomt_feats):
        print("✓ Column ORDER is identical")

    # ── Stage 3: Label Harmonization ──────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("STAGE 3: Label Harmonization (3-level scheme)")
    print("=" * 70)
    cic = harmonize_ciciomt2024(cic, category_scheme=category_scheme)
    print_label_summary(cic, "CICIoMT2024")
    iomt = harmonize_iomt_trafficdata(iomt, category_scheme=category_scheme)
    print_label_summary(iomt, "IoMT-TrafficData")

    # ── Stage 4: Concatenation ────────────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("STAGE 4: Dataset Concatenation")
    print("=" * 70)
    unified = pd.concat([cic, iomt], ignore_index=True)
    print(f"Unified dataset: {len(unified):,} rows × {unified.shape[1]} columns")
    print(f"\nSource distribution:")
    for src, count in unified["source_dataset"].value_counts().items():
        pct = 100 * count / len(unified)
        print(f"  {src:20s} {count:>10,}  ({pct:5.1f}%)")
    print_label_summary(unified, "Unified (Phase 1)")

    # ── Stage 5: Quality Assurance ────────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("STAGE 5: Data Quality Assurance")
    print("=" * 70)
    feature_cols = get_feature_columns(unified)
    feature_cols = [c for c in feature_cols
                    if c not in ["label_binary", "label_category", "label_fine"]]
    print(f"Starting QA with {len(feature_cols)} features and {len(unified):,} rows")
    unified_qa, feature_cols_qa, near_zero = run_full_qa(unified, feature_cols)

    # ── Stage 6: Split & Scale ────────────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("STAGE 6: Stratified Splitting & Feature Scaling")
    print("=" * 70)
    splits = stratified_split(unified_qa, feature_cols_qa)
    print_split_distribution(splits)
    scaled_splits, scaler = apply_scaling(splits, feature_cols_qa)

    # ── Stage 7: Export ───────────────────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("STAGE 7: Export")
    print("=" * 70)
    save_splits(
        scaled_splits,
        scaler,
        feature_cols_qa,
        near_zero,
        output_subdir=output_subdir,
        category_scheme=category_scheme,
    )

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"Pipeline completed in {elapsed:.1f} seconds ({elapsed/60:.1f} min)")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
