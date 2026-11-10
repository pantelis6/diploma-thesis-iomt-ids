"""
Generate evaluation tables and report figures from saved DT experiments.
Loads only the saved joblib artifacts — no CSV reload needed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from pipeline.training import (
    RESULTS_DIR, FIGURES_DIR, GLOBAL_CLASSES,
    REGIME_LABEL, build_eval_matrix,
    plot_confusion_matrix, plot_feature_importance,
    plot_regime_comparison, plot_per_class_f1,
    create_global_label_encoder,
)

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
le = create_global_label_encoder()


def load_all_results():
    """Load baseline + tuned eval_results for B1, B2, U."""
    all_results = {}
    for regime in ("B1", "B2", "U"):
        for stage in ("baseline", "tuned"):
            d = RESULTS_DIR / "phase2_dt" / regime / stage
            if not d.exists():
                print(f"  SKIP {regime}/{stage} — not found")
                continue
            res = joblib.load(d / "eval_results.joblib")
            key = f"{'BL' if stage == 'baseline' else 'Tuned'}-{regime}"
            all_results[key] = res
            print(f"  Loaded {key}")
    return all_results


def load_tuned_models():
    """Load tuned model objects for feature importance."""
    models = {}
    for regime in ("B1", "B2", "U"):
        d = RESULTS_DIR / "phase2_dt" / regime / "tuned"
        if (d / "model.joblib").exists():
            models[regime] = joblib.load(d / "model.joblib")
            print(f"  Loaded tuned model {regime}")
    return models


def load_tuned_params():
    """Load best hyperparameters."""
    params = {}
    for regime in ("B1", "B2", "U"):
        d = RESULTS_DIR / "phase2_dt" / regime / "tuned"
        if (d / "params.joblib").exists():
            params[regime] = joblib.load(d / "params.joblib")
    return params


def main():
    print("=" * 60)
    print("Loading saved experiments")
    print("=" * 60)
    all_results = load_all_results()
    models = load_tuned_models()
    params = load_tuned_params()

    # ── 1. Evaluation matrix ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Evaluation Matrix")
    print("=" * 60)

    eval_df = build_eval_matrix(all_results)
    print(eval_df.round(4).to_string(index=False))

    # LaTeX table
    latex_cols = ["Model", "Test slice", "f1_macro", "f1_weighted", "accuracy"]
    latex_df = eval_df[latex_cols].copy()
    latex_df.columns = ["Model", "Test Slice", "Macro-F1", "Weighted-F1", "Accuracy"]
    print("\n--- LaTeX ---")
    print(latex_df.to_latex(index=False, float_format="%.4f"))

    # Best params table
    print("\n--- Best Hyperparameters ---")
    for r in ("B1", "B2", "U"):
        if r in params:
            print(f"  {r}: {params[r]}")

    # ── 2. Feature columns (read from metadata) ─────────────────────────
    meta = joblib.load(
        Path(__file__).resolve().parents[1]
        / "data" / "processed" / "phase1_iomt_unified_mqtt_category"
        / "metadata.joblib"
    )
    feature_cols = meta["feature_cols"]

    # ── 3. Confusion matrices ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Generating confusion matrix figures")
    print("=" * 60)

    # Tuned models on full test
    for regime in ("B1", "B2", "U"):
        key = f"Tuned-{regime}"
        if key not in all_results or "full" not in all_results[key]:
            continue
        cm = all_results[key]["full"]["cm"]
        plot_confusion_matrix(
            cm, GLOBAL_CLASSES,
            title=f"Tuned DT — {regime} ({REGIME_LABEL[regime]}) → Full Test",
            save_path=str(FIGURES_DIR / f"ch5_dt_cm_{regime.lower()}_full.png"),
        )
        plt.close("all")

    # Cross-domain CMs
    xd_pairs = [("B1", "IoMT-TrafficData", "IoMT"),
                ("B2", "CICIoMT2024", "CIC")]
    for regime, src, tag in xd_pairs:
        key = f"Tuned-{regime}"
        if key in all_results and src in all_results[key]:
            cm = all_results[key][src]["cm"]
            plot_confusion_matrix(
                cm, GLOBAL_CLASSES,
                title=f"Tuned DT — {regime} → {tag} (cross-domain)",
                save_path=str(FIGURES_DIR / f"ch5_dt_cm_{regime.lower()}_xd_{tag.lower()}.png"),
            )
            plt.close("all")

    # ── 4. Feature importance ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Generating feature importance figures")
    print("=" * 60)

    if "U" in models:
        plot_feature_importance(
            models["U"], feature_cols, top_n=20,
            title="Top-20 Feature Importances — Tuned DT (Unified)",
            save_path=str(FIGURES_DIR / "ch5_dt_feature_importance_unified.png"),
        )
        plt.close("all")

    # Comparison: B1 vs B2 vs U
    available = [r for r in ("B1", "B2", "U") if r in models]
    if len(available) == 3:
        fig, axes = plt.subplots(1, 3, figsize=(22, 9))
        for ax, r in zip(axes, available):
            imp = models[r].feature_importances_
            idx = np.argsort(imp)[::-1][:15]
            ax.barh(range(15), imp[idx[::-1]], align="center", color="steelblue")
            ax.set_yticks(range(15))
            ax.set_yticklabels([feature_cols[i] for i in idx[::-1]], fontsize=13)
            ax.set_xlabel("Importance", fontsize=13)
            ax.tick_params(axis='x', labelsize=12)
            ax.set_title(f"{r} ({REGIME_LABEL[r]})", fontsize=14)
        plt.suptitle("Top-15 Feature Importances by Regime (Tuned DT)", fontsize=14)
        plt.tight_layout()
        path = FIGURES_DIR / "ch5_dt_feature_importance_comparison.png"
        fig.savefig(path, dpi=300, bbox_inches="tight")
        print(f"  Saved: {path}")
        plt.close("all")

    # ── 5. Regime comparison bar charts ──────────────────────────────────
    print("\n" + "=" * 60)
    print("Generating comparison figures")
    print("=" * 60)

    tuned_results = {k: v for k, v in all_results.items() if k.startswith("Tuned")}
    tuned_df = build_eval_matrix(tuned_results)

    plot_regime_comparison(
        tuned_df, metric="f1_macro",
        title="Macro-F1 Comparison — Tuned Decision Trees",
        save_path=str(FIGURES_DIR / "ch5_dt_regime_comparison_f1macro.png"),
    )
    plt.close("all")

    # ── 6. Per-class F1 chart ────────────────────────────────────────────
    plot_per_class_f1(
        tuned_results, le, test_slice="full",
        title="Per-Class F1 — Tuned DT (Full Test Set)",
        save_path=str(FIGURES_DIR / "ch5_dt_per_class_f1.png"),
    )
    plt.close("all")

    print("\n" + "=" * 60)
    print("All figures generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
