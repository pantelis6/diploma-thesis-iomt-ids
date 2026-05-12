"""
Phase 2: ML Model Training & Evaluation Utilities

Reusable functions for the IDS model training pipeline.
Covers data loading, regime preparation, label encoding,
model training (baseline + tuned), cross-domain evaluation,
visualization, and experiment persistence.
"""

import time
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

# ── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIGURES_DIR = BASE_DIR / "report" / "figures"
RESULTS_DIR = BASE_DIR / "results"

RANDOM_SEED = 42

LABEL_COL = "label_category"
SOURCE_COL = "source_dataset"

NON_FEATURE_COLS = [
    "attack_type", "source_file", "source_dataset", "attack_group",
    "label_category", "label_binary", "label_fine",
]

GLOBAL_CLASSES = sorted(
    ["Benign", "DDoS", "DoS", "MQTT", "Reconnaissance", "Spoofing"]
)

REGIME_SOURCE = {
    "B1": "CICIoMT2024",
    "B2": "IoMT-TrafficData",
    "U": None,
}

REGIME_LABEL = {
    "B1": "CIC-only",
    "B2": "IoMT-only",
    "U": "Unified",
}


# ── Data Loading ─────────────────────────────────────────────────────────────


def load_phase1_splits(
    subdir: str = "phase1_iomt_unified_mqtt_category",
) -> Tuple[Dict[str, pd.DataFrame], List[str]]:
    """Load train / val / test CSVs and metadata; return (splits, feature_cols)."""
    data_dir = PROCESSED_DIR / subdir
    meta = joblib.load(data_dir / "metadata.joblib")
    feature_cols: List[str] = meta["feature_cols"]

    splits: Dict[str, pd.DataFrame] = {}
    for name in ("train", "val", "test"):
        df = pd.read_csv(data_dir / f"{name}.csv")
        splits[name] = df
        print(f"  {name}: {len(df):,} rows × {df.shape[1]} cols")

    print(f"  Feature columns: {len(feature_cols)}")
    return splits, feature_cols


def filter_by_source(
    splits: Dict[str, pd.DataFrame], source: str
) -> Dict[str, pd.DataFrame]:
    """Return copies of each split filtered to rows from *source*."""
    return {
        name: df.loc[df[SOURCE_COL] == source].reset_index(drop=True)
        for name, df in splits.items()
    }


# ── Label Encoding ───────────────────────────────────────────────────────────


def create_global_label_encoder() -> LabelEncoder:
    """LabelEncoder fitted on all six global attack categories (alphabetical)."""
    le = LabelEncoder()
    le.fit(GLOBAL_CLASSES)
    return le


# ── Class Weights ────────────────────────────────────────────────────────────


def compute_balanced_weights(y: np.ndarray) -> Dict[int, float]:
    """sklearn-style balanced weights: n_samples / (n_classes × n_samples_class)."""
    classes, counts = np.unique(y, return_counts=True)
    n, k = len(y), len(classes)
    return {int(c): n / (k * cnt) for c, cnt in zip(classes, counts)}


def compute_sample_weights(
    y: np.ndarray, class_weights: Dict[int, float]
) -> np.ndarray:
    """Per-sample weight array (for estimators that accept sample_weight)."""
    return np.array([class_weights[int(yi)] for yi in y])


# ── Regime Preparation ───────────────────────────────────────────────────────


def prepare_regime(
    splits: Dict[str, pd.DataFrame],
    feature_cols: List[str],
    regime: str = "U",
) -> Dict[str, Any]:
    """
    Build X/y arrays, encoder, and weights for a training regime.

    Parameters
    ----------
    regime : "B1" (CIC-only), "B2" (IoMT-only), or "U" (Unified).

    Returns
    -------
    dict with X_train, y_train, X_val, y_val, X_test, y_test,
    label_encoder, class_weights, sample_weights, regime_splits, train_classes.
    """
    src = REGIME_SOURCE[regime]
    label = REGIME_LABEL[regime]
    regime_splits = filter_by_source(splits, src) if src else splits

    print(f"\n{'─' * 60}")
    print(f"Regime {regime} — {label}")
    print(f"{'─' * 60}")
    for name, df in regime_splits.items():
        cats = sorted(df[LABEL_COL].unique())
        print(f"  {name:5s}: {len(df):>10,} rows | classes {cats}")

    le = create_global_label_encoder()

    X = {n: df[feature_cols].values for n, df in regime_splits.items()}
    y = {n: le.transform(df[LABEL_COL]) for n, df in regime_splits.items()}

    cw = compute_balanced_weights(y["train"])
    sw = compute_sample_weights(y["train"], cw)
    train_classes = sorted(np.unique(y["train"]).tolist())

    weight_str = {
        le.inverse_transform([c])[0]: f"{w:.2f}" for c, w in cw.items()
    }
    print(f"  Balanced weights: {weight_str}")

    return {
        "X_train": X["train"],  "y_train": y["train"],
        "X_val":   X["val"],    "y_val":   y["val"],
        "X_test":  X["test"],   "y_test":  y["test"],
        "label_encoder": le,
        "class_weights": cw,
        "sample_weights": sw,
        "regime_splits": regime_splits,
        "train_classes": train_classes,
    }


# ── Decision Tree Training ──────────────────────────────────────────────────


def train_baseline_dt(data: Dict[str, Any]) -> DecisionTreeClassifier:
    """Train a default-hyperparameter DT with balanced class weights."""
    dt = DecisionTreeClassifier(
        class_weight=data["class_weights"],
        random_state=RANDOM_SEED,
    )
    t0 = time.time()
    dt.fit(data["X_train"], data["y_train"])
    elapsed = time.time() - t0
    print(
        f"  Baseline DT trained in {elapsed:.1f}s  "
        f"(depth={dt.get_depth()}, leaves={dt.get_n_leaves():,})"
    )
    return dt


DT_PARAM_SPACE = {
    "max_depth": [5, 10, 15, 20, 25, 30, None],
    "min_samples_split": [2, 5, 10, 20, 50],
    "min_samples_leaf": [1, 2, 5, 10, 20],
    "criterion": ["gini", "entropy"],
    "max_features": ["sqrt", "log2", None],
}


def tune_dt(
    data: Dict[str, Any],
    n_iter: int = 50,
    cv: int = 3,
    n_jobs: int = 1,
    verbose: int = 1,
) -> RandomizedSearchCV:
    """RandomizedSearchCV for Decision Tree (scoring=f1_macro)."""
    dt = DecisionTreeClassifier(
        class_weight=data["class_weights"],
        random_state=RANDOM_SEED,
    )
    search = RandomizedSearchCV(
        dt,
        param_distributions=DT_PARAM_SPACE,
        n_iter=n_iter,
        cv=StratifiedKFold(n_splits=cv, shuffle=True, random_state=RANDOM_SEED),
        scoring="f1_macro",
        n_jobs=n_jobs,
        random_state=RANDOM_SEED,
        verbose=verbose,
        return_train_score=True,
    )
    t0 = time.time()
    search.fit(data["X_train"], data["y_train"])
    elapsed = time.time() - t0
    print(f"  Tuning completed in {elapsed:.1f}s ({elapsed / 60:.1f} min)")
    print(f"  Best CV macro-F1: {search.best_score_:.4f}")
    print(f"  Best params: {search.best_params_}")
    return search


# ── Random Forest Training ───────────────────────────────────────────────────


def train_baseline_rf(data: Dict[str, Any]) -> RandomForestClassifier:
    """Train a default-hyperparameter RF with balanced class weights."""
    rf = RandomForestClassifier(
        n_estimators=100,
        class_weight=data["class_weights"],
        n_jobs=1,
        random_state=RANDOM_SEED,
    )
    t0 = time.time()
    rf.fit(data["X_train"], data["y_train"])
    elapsed = time.time() - t0
    print(
        f"  Baseline RF trained in {elapsed:.1f}s  "
        f"(n_estimators=100, max_depth={rf.estimators_[0].get_depth()}..)"
    )
    return rf


RF_PARAM_SPACE = {
    "n_estimators": [100, 200, 300, 500],
    "max_depth": [10, 15, 20, 25, 30, None],
    "max_features": ["sqrt", "log2", 0.3, 0.5],
    "min_samples_split": [2, 5, 10, 20, 50],
    "min_samples_leaf": [1, 2, 5, 10, 20],
    "max_samples": [0.5, 0.7, 0.8, 1.0],
    "class_weight": ["balanced", "balanced_subsample"],
}


def tune_rf(
    data: Dict[str, Any],
    n_iter: int = 50,
    cv: int = 3,
    n_jobs: int = 1,
    verbose: int = 1,
) -> RandomizedSearchCV:
    """RandomizedSearchCV for Random Forest (scoring=f1_macro)."""
    rf = RandomForestClassifier(
        n_jobs=1,
        random_state=RANDOM_SEED,
    )
    search = RandomizedSearchCV(
        rf,
        param_distributions=RF_PARAM_SPACE,
        n_iter=n_iter,
        cv=StratifiedKFold(n_splits=cv, shuffle=True, random_state=RANDOM_SEED),
        scoring="f1_macro",
        n_jobs=n_jobs,
        random_state=RANDOM_SEED,
        verbose=verbose,
        return_train_score=True,
    )
    t0 = time.time()
    search.fit(data["X_train"], data["y_train"])
    elapsed = time.time() - t0
    print(f"  Tuning completed in {elapsed:.1f}s ({elapsed / 60:.1f} min)")
    print(f"  Best CV macro-F1: {search.best_score_:.4f}")
    print(f"  Best params: {search.best_params_}")
    return search


# ── XGBoost Training ─────────────────────────────────────────────────────────

try:
    from xgboost import XGBClassifier
    _HAS_XGB = True
except ImportError:
    _HAS_XGB = False


# Defaults aligned with XGBClassifier / search space (tunable keys = XGB_PARAM_SPACE)
_XGB_EST_DEFAULTS: Dict[str, Any] = {
    "learning_rate": 0.3,
    "n_estimators": 100,
    "max_depth": 6,
    "min_child_weight": 1,
    "subsample": 1.0,
    "colsample_bytree": 1.0,
    "gamma": 0.0,
    "reg_lambda": 1.0,
    "reg_alpha": 0.0,
}


class _XGBGlobalMulticlassEstimator(BaseEstimator, ClassifierMixin):
    """
    XGBoost softmax classifier that remaps global label indices to 0..K-1
    for the K classes actually present in *y* at fit time.

    Required for regimes such as B2 (IoMT-only) where the DDoS global class
    never appears in training: native XGBoost rejects non-contiguous labels
    when ``num_class`` is set to the full ontology size.
    """

    def __init__(self, **kwargs):
        for k, v in _XGB_EST_DEFAULTS.items():
            setattr(self, k, kwargs.get(k, v))
        self.model_: Optional[Any] = None
        self.classes_present_: Optional[np.ndarray] = None

    def get_params(self, deep=True) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in _XGB_EST_DEFAULTS}

    def set_params(self, **params) -> "_XGBGlobalMulticlassEstimator":
        for k, v in params.items():
            if k in _XGB_EST_DEFAULTS:
                setattr(self, k, v)
        return self

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
    ) -> "_XGBGlobalMulticlassEstimator":
        if not _HAS_XGB:
            raise ImportError("xgboost is not installed")
        self.classes_present_ = np.sort(np.unique(y))
        n_c = len(self.classes_present_)
        g2l = {int(g): i for i, g in enumerate(self.classes_present_)}
        y_loc = np.array([g2l[int(v)] for v in y], dtype=np.int32)
        self.model_ = XGBClassifier(
            learning_rate=self.learning_rate,
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_child_weight=self.min_child_weight,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            gamma=self.gamma,
            reg_lambda=self.reg_lambda,
            reg_alpha=self.reg_alpha,
            tree_method="hist",
            objective="multi:softmax",
            num_class=n_c,
            random_state=RANDOM_SEED,
            verbosity=0,
            n_jobs=1,
        )
        self.model_.fit(X, y_loc, sample_weight=sample_weight)
        self.classes_ = self.classes_present_
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        loc = self.model_.predict(X).astype(int)
        return self.classes_present_[loc]

    @property
    def feature_importances_(self) -> np.ndarray:
        return self.model_.feature_importances_


def fit_xgb_from_best_params(
    best_params: Dict[str, Any], data: Dict[str, Any]
) -> _XGBGlobalMulticlassEstimator:
    """Fit an XGBoost model on *data* using hyperparameters from tuning (full refit)."""
    kw = {**_XGB_EST_DEFAULTS, **best_params}
    est = _XGBGlobalMulticlassEstimator(**kw)
    est.fit(
        data["X_train"],
        data["y_train"],
        sample_weight=data["sample_weights"],
    )
    return est


def train_baseline_xgb(data: Dict[str, Any]) -> _XGBGlobalMulticlassEstimator:
    """Train a default-hyperparameter XGBoost with sample weights."""
    if not _HAS_XGB:
        raise ImportError("xgboost is not installed")
    est = _XGBGlobalMulticlassEstimator(n_estimators=100)
    t0 = time.time()
    est.fit(
        data["X_train"],
        data["y_train"],
        sample_weight=data["sample_weights"],
    )
    elapsed = time.time() - t0
    print(f"  Baseline XGBoost trained in {elapsed:.1f}s  (n_estimators=100)")
    return est


XGB_PARAM_SPACE = {
    "learning_rate": [0.01, 0.03, 0.05, 0.1, 0.2, 0.3],
    "n_estimators": [100, 200, 300, 500, 1000],
    "max_depth": [3, 5, 7, 9, 12],
    "min_child_weight": [1, 3, 5, 10, 20],
    "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
    "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
    "gamma": [0, 0.1, 0.5, 1, 5],
    "reg_lambda": [0.01, 0.1, 1, 10],
    "reg_alpha": [0, 0.01, 0.1, 1],
}


def tune_xgb(
    data: Dict[str, Any],
    n_iter: int = 50,
    cv: int = 3,
    n_jobs: int = 1,
    verbose: int = 1,
) -> RandomizedSearchCV:
    """RandomizedSearchCV for XGBoost (scoring=f1_macro, with sample_weight)."""
    if not _HAS_XGB:
        raise ImportError("xgboost is not installed")
    base = _XGBGlobalMulticlassEstimator()
    search = RandomizedSearchCV(
        base,
        param_distributions=XGB_PARAM_SPACE,
        n_iter=n_iter,
        cv=StratifiedKFold(n_splits=cv, shuffle=True, random_state=RANDOM_SEED),
        scoring="f1_macro",
        n_jobs=n_jobs,
        random_state=RANDOM_SEED,
        verbose=verbose,
        return_train_score=True,
    )
    t0 = time.time()
    search.fit(data["X_train"], data["y_train"],
               sample_weight=data["sample_weights"])
    elapsed = time.time() - t0
    print(f"  Tuning completed in {elapsed:.1f}s ({elapsed / 60:.1f} min)")
    print(f"  Best CV macro-F1: {search.best_score_:.4f}")
    print(f"  Best params: {search.best_params_}")
    return search


# ── Evaluation ───────────────────────────────────────────────────────────────


def evaluate_model(
    model,
    X: np.ndarray,
    y_true: np.ndarray,
    le: LabelEncoder,
    dataset_name: str = "",
) -> Dict[str, Any]:
    """
    Predict and compute metrics, classification report, and confusion matrix.

    The confusion matrix always has shape (n_global_classes, n_global_classes)
    so that matrices from different regimes are directly comparable.
    """
    y_pred = model.predict(X)
    all_labels = list(range(len(le.classes_)))

    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_macro": float(
            f1_score(y_true, y_pred, average="macro",
                     labels=all_labels, zero_division=0)
        ),
        "f1_weighted": float(
            f1_score(y_true, y_pred, average="weighted",
                     labels=all_labels, zero_division=0)
        ),
        "precision_macro": float(
            precision_score(y_true, y_pred, average="macro",
                            labels=all_labels, zero_division=0)
        ),
        "recall_macro": float(
            recall_score(y_true, y_pred, average="macro",
                         labels=all_labels, zero_division=0)
        ),
    }

    present = sorted(set(np.unique(y_true)) | set(np.unique(y_pred)))
    report = classification_report(
        y_true, y_pred,
        labels=present,
        target_names=[le.classes_[i] for i in present],
        zero_division=0,
        output_dict=True,
    )
    cm = confusion_matrix(y_true, y_pred, labels=all_labels)

    if dataset_name:
        print(
            f"  [{dataset_name}]  acc={metrics['accuracy']:.4f}  "
            f"F1m={metrics['f1_macro']:.4f}  "
            f"F1w={metrics['f1_weighted']:.4f}"
        )
    return {"metrics": metrics, "report": report, "cm": cm, "y_pred": y_pred}


def evaluate_cross_domain(
    model,
    full_splits: Dict[str, pd.DataFrame],
    feature_cols: List[str],
    le: LabelEncoder,
    regime: str,
) -> Dict[str, Dict[str, Any]]:
    """
    Evaluate a model on the full test set and on per-source slices.

    Returns dict keyed by "full", "CICIoMT2024", "IoMT-TrafficData".
    """
    results: Dict[str, Dict[str, Any]] = {}
    test_df = full_splits["test"]

    X_full = test_df[feature_cols].values
    y_full = le.transform(test_df[LABEL_COL])
    results["full"] = evaluate_model(
        model, X_full, y_full, le, f"{regime}→Full"
    )

    for src in ("CICIoMT2024", "IoMT-TrafficData"):
        mask = test_df[SOURCE_COL] == src
        if mask.sum() == 0:
            continue
        X_src = test_df.loc[mask, feature_cols].values
        y_src = le.transform(test_df.loc[mask, LABEL_COL])
        tag = "CIC" if "CIC" in src else "IoMT"
        results[src] = evaluate_model(model, X_src, y_src, le, f"{regime}→{tag}")

    return results


def build_eval_matrix(
    all_results: Dict[str, Dict[str, Dict[str, Any]]],
) -> pd.DataFrame:
    """
    Flatten cross-domain results into a tidy DataFrame.

    Parameters
    ----------
    all_results : {model_key: {test_slice: eval_dict}}
    """
    rows = []
    for model_key, slices in all_results.items():
        for slice_key, res in slices.items():
            m = res["metrics"]
            rows.append({"Model": model_key, "Test slice": slice_key, **m})
    return pd.DataFrame(rows)


# ── Visualization ────────────────────────────────────────────────────────────


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str],
    title: str = "Confusion Matrix",
    normalize: bool = True,
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
):
    """Normalized or absolute confusion-matrix heatmap."""
    fig, ax = plt.subplots(figsize=figsize)

    if normalize:
        row_sums = cm.sum(axis=1, keepdims=True).astype(float)
        row_sums[row_sums == 0] = 1
        data = cm.astype(float) / row_sums
        fmt = ".1%"
    else:
        data = cm
        fmt = ",d"

    sns.heatmap(
        data, annot=True, fmt=fmt, cmap="Blues",
        xticklabels=class_names, yticklabels=class_names,
        linewidths=0.5, ax=ax,
    )
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("True", fontsize=12)
    ax.set_title(title, fontsize=14)
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    return fig


def plot_feature_importance(
    model,
    feature_names: List[str],
    top_n: int = 20,
    title: str = "Top Feature Importances",
    figsize: Tuple[int, int] = (10, 8),
    save_path: Optional[str] = None,
):
    """Horizontal bar chart of the *top_n* most important features."""
    imp = model.feature_importances_
    idx = np.argsort(imp)[::-1][:top_n]

    fig, ax = plt.subplots(figsize=figsize)
    y_pos = np.arange(top_n)
    ax.barh(y_pos, imp[idx[::-1]], align="center", color="steelblue")
    ax.set_yticks(y_pos)
    ax.set_yticklabels([feature_names[i] for i in idx[::-1]])
    ax.set_xlabel("Gini Importance")
    ax.set_title(title, fontsize=14)
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    return fig


def plot_regime_comparison(
    eval_df: pd.DataFrame,
    metric: str = "f1_macro",
    title: str = "Macro-F1 Comparison Across Regimes",
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None,
):
    """Grouped bar chart comparing regimes across test slices for one metric."""
    fig, ax = plt.subplots(figsize=figsize)
    pivot = eval_df.pivot(index="Model", columns="Test slice", values=metric)
    pivot.plot(kind="bar", ax=ax, rot=0, edgecolor="black", linewidth=0.5)
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title(title, fontsize=14)
    ax.legend(title="Test Slice", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.set_ylim(0, 1.05)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", fontsize=8, padding=2)
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    return fig


def plot_per_class_f1(
    all_results: Dict[str, Dict[str, Any]],
    le: LabelEncoder,
    test_slice: str = "full",
    title: str = "Per-Class F1 by Regime",
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None,
):
    """Grouped bar chart of per-class F1 scores for each regime on a given slice."""
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(le.classes_))
    width = 0.8 / len(all_results)

    for i, (regime_key, slices) in enumerate(all_results.items()):
        if test_slice not in slices:
            continue
        report = slices[test_slice]["report"]
        f1s = [
            report.get(cls, {}).get("f1-score", 0.0) for cls in le.classes_
        ]
        ax.bar(x + i * width, f1s, width, label=regime_key)

    ax.set_xticks(x + width * (len(all_results) - 1) / 2)
    ax.set_xticklabels(le.classes_, rotation=30, ha="right")
    ax.set_ylabel("F1-Score")
    ax.set_title(title, fontsize=14)
    ax.set_ylim(0, 1.05)
    ax.legend()
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    return fig


# ── Persistence ──────────────────────────────────────────────────────────────


def save_experiment(
    regime: str,
    model_name: str,
    stage: str,
    model: Any,
    eval_results: Dict[str, Any],
    params: Optional[Dict] = None,
    output_dir: Optional[Path] = None,
) -> Path:
    """Save model, evaluation results, and hyper-parameters."""
    if output_dir is None:
        output_dir = RESULTS_DIR / f"phase2_{model_name}" / regime / stage
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, output_dir / "model.joblib")
    joblib.dump(eval_results, output_dir / "eval_results.joblib")
    if params:
        joblib.dump(params, output_dir / "params.joblib")
    print(f"  Experiment saved → {output_dir}")
    return output_dir


def load_experiment(
    regime: str,
    model_name: str,
    stage: str,
    output_dir: Optional[Path] = None,
) -> Tuple[Any, Dict, Optional[Dict]]:
    """Load a previously saved experiment."""
    if output_dir is None:
        output_dir = RESULTS_DIR / f"phase2_{model_name}" / regime / stage
    output_dir = Path(output_dir)
    model = joblib.load(output_dir / "model.joblib")
    results = joblib.load(output_dir / "eval_results.joblib")
    params_path = output_dir / "params.joblib"
    params = joblib.load(params_path) if params_path.exists() else None
    return model, results, params
