"""
Run Decision Tree hyperparameter tuning for B1 and U regimes.
Memory-optimized for machines with ≤ 18 GB RAM:
  - n_jobs=2 (avoid per-worker data duplication)
  - float32 X arrays (halves memory)
  - explicit gc.collect() between regimes
"""
import gc
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import joblib
import numpy as np
from pipeline.training import (
    load_phase1_splits,
    prepare_regime,
    tune_dt,
    evaluate_cross_domain,
    save_experiment,
    RESULTS_DIR,
)


def main():
    t_global = time.time()

    print("Loading data...")
    splits, feature_cols = load_phase1_splits()

    for regime in ("B1", "U"):
        out_dir = RESULTS_DIR / "phase2_dt" / regime / "tuned"
        if (out_dir / "model.joblib").exists():
            print(f"\n>>> {regime} tuned already exists — skipping.")
            continue

        print(f"\n{'='*60}")
        print(f"Preparing regime {regime}")
        print(f"{'='*60}")
        data = prepare_regime(splits, feature_cols, regime=regime)

        # Cast to float32 to halve memory
        data["X_train"] = data["X_train"].astype(np.float32)
        data["X_val"] = data["X_val"].astype(np.float32)
        data["X_test"] = data["X_test"].astype(np.float32)

        # Drop regime_splits (duplicate DataFrames) to save RAM
        del data["regime_splits"]
        gc.collect()

        mem_gb = data["X_train"].nbytes / 1e9
        print(f"  X_train memory: {mem_gb:.2f} GB (float32)")

        print(f"\n{'='*60}")
        print(f"Tuning DT — {regime}  (n_jobs=1, sequential CV)")
        print(f"{'='*60}")
        search = tune_dt(data, n_iter=50, cv=3, n_jobs=1, verbose=1)

        # Cross-domain eval needs regime_splits but we deleted it;
        # use the full splits directly
        le = data["label_encoder"]
        print(f"\nCross-domain evaluation — Tuned {regime}:")
        xd = evaluate_cross_domain(
            search.best_estimator_, splits, feature_cols, le, f"Tuned-{regime}"
        )

        save_experiment(
            regime, "dt", "tuned",
            search.best_estimator_, xd, search.best_params_,
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(search, out_dir / "search_cv.joblib")

        # Free memory before next regime
        del data, search, xd
        gc.collect()
        print(f"  Memory freed for regime {regime}.")

    elapsed = time.time() - t_global
    print(f"\n{'='*60}")
    print(f"All done in {elapsed:.1f}s ({elapsed / 60:.1f} min)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
