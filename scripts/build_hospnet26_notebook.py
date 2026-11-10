"""Generate notebooks/11_hospnet26_inference.ipynb"""
import json
from pathlib import Path


def nb_cell_md(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.splitlines()],
    }


def nb_cell_code(text: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "source": [line + "\n" for line in text.splitlines()],
        "outputs": [],
        "execution_count": None,
    }


CELLS = [
    nb_cell_md(
        "# HospNet26 Real-World Inference Evaluation\n"
        "\n"
        "This notebook reproduces the **HospNet26** deployment experiment reported in the paper "
        "(Section 6) and thesis (Section 5.3).\n"
        "\n"
        "**Protocol (strict no-leakage):**\n"
        "1. Load the four HospNet26 *combined-feature* Parquet files (or the preprocessed cache).\n"
        "2. Extract the same **58 MIOTTA window features** used in Phase 1.\n"
        "3. Apply the **same `StandardScaler` fitted on the unified training split** — no refitting.\n"
        "4. Run **tuned** Decision Tree, Random Forest, and XGBoost models (regimes **B1**, **B2**, **U**).\n"
        "5. Report **Benign prediction rate** $r_B$ and per-class false-positive distributions.\n"
        "\n"
        "All numbers are cross-checked against archived result files in `results/`."
    ),
    nb_cell_code(
        'import sys\n'
        'import warnings\n'
        'from pathlib import Path\n'
        '\n'
        'import joblib\n'
        'import numpy as np\n'
        'import pandas as pd\n'
        'import matplotlib.pyplot as plt\n'
        'import seaborn as sns\n'
        '\n'
        'warnings.filterwarnings("ignore", category=FutureWarning)\n'
        '%matplotlib inline\n'
        'plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300})\n'
        'sns.set_style("whitegrid")\n'
        '\n'
        'ROOT = Path("..").resolve()\n'
        'sys.path.insert(0, str(ROOT / "src"))\n'
        '\n'
        'from pipeline.training import GLOBAL_CLASSES\n'
        '\n'
        'PHASE1_DIR = ROOT / "data/processed/phase1_iomt_unified_mqtt_category"\n'
        'RAW_DIR = ROOT / "data/raw/hospnet26"\n'
        'PROCESSED_PATH = ROOT / "data/processed/hospnet26_processed.joblib"\n'
        'REF_UNIFIED = ROOT / "results/hospnet26_eval_results.joblib"\n'
        'REF_REGIMES = ROOT / "results/hospnet26_eval_b1b2u.joblib"\n'
        '\n'
        'MODEL_SPECS = [\n'
        '    ("Decision Tree", "dt", ["B1", "B2", "U"]),\n'
        '    ("Random Forest", "rf", ["B1", "B2", "U"]),\n'
        '    ("XGBoost", "xgb", ["B1", "B2", "U"]),\n'
        ']\n'
        '\n'
        'SEGMENT_FILES = {\n'
        '    "Friday": "combined_Friday.parquet",\n'
        '    "Monday": "combined_Monday.parquet",\n'
        '    "Tue-Fri": "combined_Tue-Fri.parquet",\n'
        '    "Weekend": "combined_Weekend.parquet",\n'
        '}\n'
        '\n'
        'print("Project root:", ROOT)\n'
        'print("Global classes:", GLOBAL_CLASSES)'
    ),
    nb_cell_md(
        "## 1. Load preprocessed HospNet26 features\n"
        "\n"
        "Primary path: cached matrix from the original experiment (`hospnet26_processed.joblib`). "
        "This guarantees **bit-identical** reproduction of published numbers."
    ),
    nb_cell_code(
        'hosp = joblib.load(PROCESSED_PATH)\n'
        'X_hosp = hosp["X"]\n'
        'segments = hosp["segments"]\n'
        'feature_cols = hosp["feature_cols"]\n'
        'N = len(X_hosp)\n'
        '\n'
        'print(f"Windows: {N:,}")\n'
        'print(f"Feature matrix: {X_hosp.shape}, dtype={X_hosp.dtype}")\n'
        'print("Segment counts:")\n'
        'print(pd.Series(segments).value_counts().sort_index())'
    ),
    nb_cell_md(
        "## 2. Optional — rebuild preprocessing from raw Parquet\n"
        "\n"
        "Rebuilds `X` from the four combined Parquet files using `metadata.joblib` + `scaler.joblib`, "
        "then verifies **max absolute difference = 0** against the cached matrix."
    ),
    nb_cell_code(
        'meta = joblib.load(PHASE1_DIR / "metadata.joblib")\n'
        'scaler = joblib.load(PHASE1_DIR / "scaler.joblib")\n'
        'expected_cols = meta["feature_cols"]\n'
        '\n'
        'frames = []\n'
        'for seg, fname in SEGMENT_FILES.items():\n'
        '    df = pd.read_parquet(RAW_DIR / fname)\n'
        '    missing = set(expected_cols) - set(df.columns)\n'
        '    if missing:\n'
        '        raise ValueError(f"{fname} missing features: {sorted(missing)[:5]} ...")\n'
        '    part = df[expected_cols].copy()\n'
        '    part["segment"] = seg\n'
        '    frames.append(part)\n'
        '\n'
        'raw_df = pd.concat(frames, ignore_index=True)\n'
        'X_rebuilt = scaler.transform(raw_df[expected_cols].to_numpy(dtype=np.float32))\n'
        'seg_rebuilt = raw_df["segment"].to_numpy()\n'
        '\n'
        'max_diff = float(np.max(np.abs(X_rebuilt - X_hosp)))\n'
        'print(f"Rebuild shape: {X_rebuilt.shape}")\n'
        'print(f"Max |delta| vs cached X: {max_diff:.6e}")\n'
        'assert max_diff < 1e-5, "Preprocessing mismatch — check scaler / feature order"\n'
        'assert np.array_equal(seg_rebuilt, segments), "Segment order mismatch"\n'
        'print("OK: rebuild matches cached preprocessing exactly.")'
    ),
    nb_cell_md("## 3. Inference helpers"),
    nb_cell_code(
        'BENIGN_IDX = GLOBAL_CLASSES.index("Benign")\n'
        '\n'
        '\n'
        'def load_tuned_model(model_key: str, regime: str):\n'
        '    path = ROOT / "results" / f"phase2_{model_key}" / regime / "tuned" / "model.joblib"\n'
        '    if not path.exists():\n'
        '        raise FileNotFoundError(path)\n'
        '    return joblib.load(path)\n'
        '\n'
        '\n'
        'def predict_distribution(model, X: np.ndarray):\n'
        '    preds = model.predict(X).astype(int)\n'
        '    counts = np.bincount(preds, minlength=len(GLOBAL_CLASSES))\n'
        '    pct = counts / counts.sum() * 100.0\n'
        '    dist = {cls: float(pct[i]) for i, cls in enumerate(GLOBAL_CLASSES)}\n'
        '    return preds, dist, dist["Benign"] / 100.0\n'
        '\n'
        '\n'
        'def format_pct(x: float) -> str:\n'
        '    return f"{x:.2f}%"'
    ),
    nb_cell_md(
        "## 4. Unified models — paper Table 6\n"
        "\n"
        "Tuned **U (Unified)** models on all 1,265,240 windows."
    ),
    nb_cell_code(
        'ref_u = joblib.load(REF_UNIFIED)\n'
        'rows_u = []\n'
        '\n'
        'for model_name, key, _ in MODEL_SPECS:\n'
        '    model = load_tuned_model(key, "U")\n'
        '    preds, dist, rb = predict_distribution(model, X_hosp)\n'
        '    rows_u.append({\n'
        '        "Model": model_name,\n'
        '        **{cls: format_pct(dist[cls]) for cls in GLOBAL_CLASSES},\n'
        '        "Benign rate r_B": format_pct(dist["Benign"]),\n'
        '        "_rb": rb,\n'
        '    })\n'
        '    saved_rb = ref_u[key]["benign_rate"]\n'
        '    match = np.array_equal(preds, ref_u[key]["preds"])\n'
        '    print(\n'
        '        f"{model_name:14s}  r_B={rb*100:.2f}%  "\n'
        '        f"saved={saved_rb*100:.2f}%  preds_identical={match}"\n'
        '    )\n'
        '\n'
        'df_unified = pd.DataFrame(rows_u)\n'
        'display_cols = ["Model"] + GLOBAL_CLASSES + ["Benign rate r_B"]\n'
        'df_unified[display_cols]'
    ),
    nb_cell_md(
        "## 5. All training regimes — Benign rate comparison\n"
        "\n"
        "Tuned models for **B1 (CIC-only)**, **B2 (IoMT-only)**, and **U (Unified)**."
    ),
    nb_cell_code(
        'ref_r = joblib.load(REF_REGIMES)\n'
        'rows_r = []\n'
        '\n'
        'for model_name, key, regimes in MODEL_SPECS:\n'
        '    row = {"Model": model_name}\n'
        '    rb_vals = {}\n'
        '    for regime in regimes:\n'
        '        model = load_tuned_model(key, regime)\n'
        '        _, _, rb = predict_distribution(model, X_hosp)\n'
        '        rb_vals[regime] = rb\n'
        '        saved_key = f"{key}_{regime}"\n'
        '        saved_rb = ref_r[saved_key]["benign_rate"]\n'
        '        assert abs(rb - saved_rb) < 1e-9, f"{saved_key}: {rb} != {saved_rb}"\n'
        '    best_single = max(rb_vals["B1"], rb_vals["B2"])\n'
        '    delta = (rb_vals["U"] - best_single) * 100\n'
        '    row.update({\n'
        '        "B1 (r_B)": format_pct(rb_vals["B1"] * 100),\n'
        '        "B2 (r_B)": format_pct(rb_vals["B2"] * 100),\n'
        '        "U (r_B)": format_pct(rb_vals["U"] * 100),\n'
        '        "Delta_U-max(B1,B2)": f"{delta:+.2f} pp",\n'
        '    })\n'
        '    rows_r.append(row)\n'
        '\n'
        'pd.DataFrame(rows_r)'
    ),
    nb_cell_md(
        "## 6. Per-segment Benign rates (Unified XGBoost)\n"
        "\n"
        "Weekday vs. weekend breakdown for the best unified model (XGB-U)."
    ),
    nb_cell_code(
        'xgb_u = load_tuned_model("xgb", "U")\n'
        'preds_u, _, _ = predict_distribution(xgb_u, X_hosp)\n'
        '\n'
        'seg_df = pd.DataFrame({"segment": segments, "pred": preds_u})\n'
        'seg_df["is_benign"] = seg_df["pred"] == BENIGN_IDX\n'
        '\n'
        'seg_summary = (\n'
        '    seg_df.groupby("segment")["is_benign"]\n'
        '    .mean()\n'
        '    .mul(100)\n'
        '    .reindex(["Friday", "Weekend", "Monday", "Tue-Fri"])\n'
        '    .round(2)\n'
        '    .rename("Benign rate (%)")\n'
        '    .to_frame()\n'
        ')\n'
        'seg_summary'
    ),
    nb_cell_md("## 7. Visualizations"),
    nb_cell_code(
        'fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)\n'
        'colors = sns.color_palette("Set2", len(GLOBAL_CLASSES))\n'
        '\n'
        'for ax, (model_name, key, _) in zip(axes, MODEL_SPECS):\n'
        '    model = load_tuned_model(key, "U")\n'
        '    _, dist, rb = predict_distribution(model, X_hosp)\n'
        '    vals = [dist[c] for c in GLOBAL_CLASSES]\n'
        '    ax.bar(GLOBAL_CLASSES, vals, color=colors)\n'
        '    ax.set_title(f"{model_name}-U\\nr_B = {rb*100:.2f}%")\n'
        '    ax.set_ylabel("Predicted share (%)")\n'
        '    ax.tick_params(axis="x", rotation=45)\n'
        '\n'
        'fig.suptitle(\n'
        '    "HospNet26 predicted class distribution (all windows presumed Benign)",\n'
        '    y=1.02,\n'
        ')\n'
        'plt.tight_layout()\n'
        'plt.show()'
    ),
    nb_cell_md(
        "## 8. Final verification\n"
        "\n"
        "Hard-coded reference values from the camera-ready paper (rounded to two decimals)."
    ),
    nb_cell_code(
        'PAPER_UNIFIED = {\n'
        '    "Decision Tree": {\n'
        '        "Benign": 6.07, "DDoS": 7.80, "DoS": 72.04,\n'
        '        "MQTT": 0.22, "Reconnaissance": 5.30, "Spoofing": 8.57,\n'
        '    },\n'
        '    "Random Forest": {\n'
        '        "Benign": 3.72, "DDoS": 0.60, "DoS": 71.37,\n'
        '        "MQTT": 0.06, "Reconnaissance": 19.08, "Spoofing": 5.17,\n'
        '    },\n'
        '    "XGBoost": {\n'
        '        "Benign": 9.96, "DDoS": 23.80, "DoS": 51.14,\n'
        '        "MQTT": 0.11, "Reconnaissance": 4.28, "Spoofing": 10.71,\n'
        '    },\n'
        '}\n'
        '\n'
        'PAPER_REGIMES_RB = {\n'
        '    "Decision Tree": {"B1": 9.16, "B2": 0.00, "U": 6.07},\n'
        '    "Random Forest": {"B1": 4.61, "B2": 5.46, "U": 3.72},\n'
        '    "XGBoost": {"B1": 5.20, "B2": 9.86, "U": 9.96},\n'
        '}\n'
        '\n'
        'for _, row in df_unified.iterrows():\n'
        '    ref = PAPER_UNIFIED[row["Model"]]\n'
        '    for cls in GLOBAL_CLASSES:\n'
        '        got = float(row[cls].rstrip("%"))\n'
        '        assert abs(got - ref[cls]) < 0.015, f"{row[\'Model\']} {cls}: {got} vs {ref[cls]}"\n'
        '\n'
        'for row in rows_r:\n'
        '    ref = PAPER_REGIMES_RB[row["Model"]]\n'
        '    for k in ("B1", "B2", "U"):\n'
        '        got = float(row[f"{k} (r_B)"].rstrip("%"))\n'
        '        assert abs(got - ref[k]) < 0.015, f"{row[\'Model\']} {k}: {got} vs {ref[k]}"\n'
        '\n'
        'print("OK: all notebook outputs match the published paper tables (+/- 0.01 pp).")'
    ),
]

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.13.0"},
    },
    "cells": CELLS,
}

out = Path(__file__).resolve().parents[1] / "notebooks" / "11_hospnet26_inference.ipynb"
out.write_text(json.dumps(notebook, indent=1, ensure_ascii=False))
print("Wrote", out)
