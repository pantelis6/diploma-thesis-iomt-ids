# Unifying Heterogeneous IoMT Datasets for Intrusion Detection

> *From laboratory testbeds to real hospital network evaluation.*

Machine-learning intrusion detection for the Internet of Medical Things (IoMT): a reproducible pipeline that unifies two public IoMT datasets into **8 million ML-ready records**, tree-based classifiers that reach **Macro-F1 0.95** on the unified data, and the first evaluation of such models on **real hospital network traffic**.

| | |
|---|---|
| **Paper** | *Unifying Heterogeneous IoMT Datasets for Intrusion Detection: From Laboratory Testbeds to Real Hospital Network Evaluation*, SecHealth workshop @ ARES 2026, Springer LNCS vol. 16901 — [doi.org/10.1007/978-3-032-35579-9_7](https://doi.org/10.1007/978-3-032-35579-9_7) · [author's accepted manuscript (PDF)](paper/main.pdf) |
| **Dataset** | *CICIoMT2024 + IoMT-TrafficData: a unified heterogeneous IoMT dataset for intrusion detection*, CORA Research Data Repository, CC BY 4.0 — [doi.org/10.34810/DATA3305](https://doi.org/10.34810/DATA3305) |
| **Thesis** | [UPC edition (PDF)](report/main.pdf) · [NTUA edition with Greek summary (PDF)](report/ntua/main_ntua_final.pdf) |

**Author:** Pantelis Petrakis

Diploma thesis (Integrated Master) of the School of Electrical and Computer Engineering, National Technical University of Athens (NTUA), carried out at the Facultat d'Informàtica de Barcelona (FIB), Universitat Politècnica de Catalunya (UPC), under the Erasmus+ programme.

* **UPC:** René Serral Gracià (supervisor, Department of Computer Architecture), Josep Pegueroles (co-supervisor, Department of Network Engineering), Jordi Doménech (advisor)
* **NTUA:** Emmanouil Varvarigos (supervisor)

---

## 1. Overview

The Internet of Medical Things (IoMT) has dramatically expanded the attack surface of healthcare networks: smart infusion pumps, vital-sign monitors, imaging systems and other clinical devices now coexist with traditional IT assets on the same network and are exposed to the full spectrum of cyber threats. Machine-learning (ML) based Intrusion Detection Systems (IDS) are a leading approach to defending IoMT environments, but their practical deployment is limited by two interconnected problems:

1. **Dataset isolation and feature heterogeneity.** Existing public IoMT benchmarks (CICIoMT2024, IoMT-TrafficData) were built independently, with different testbeds, attack catalogues and — most importantly — different feature-extraction tools (CICFlowMeter, Zeek). Their feature spaces are *structurally incompatible*, which makes direct concatenation impossible and forces every cross-dataset study to use heuristic feature mapping.
2. **Absence of real-world evaluation.** To the best of our knowledge, no prior ML-based IoMT IDS has been rigorously evaluated on *real* clinical network traffic. All evaluations to date are confined to laboratory testbeds, leaving the operational behaviour of these models effectively unknown.

This thesis addresses both problems. It contributes a complete, reproducible PCAP-level **dataset-unification pipeline** for IoMT, trains and tunes three tree-based classifiers on the resulting unified data, performs a rigorous cross-domain study, and provides the **first quantitative measurement of the laboratory-to-clinic gap** for IoMT IDS by deploying the unified models on the **HospNet26** real-hospital reference dataset.

---

## 2. Research Question and Contributions

> *"How can the integration of multiple heterogeneous datasets improve the performance and generalizability of a machine learning model in detecting intrusions in IoMT environments?"*

The work delivers three principal contributions:

1. **Systematic PCAP-level dataset unification via MIOTTA-NPT.** Two heterogeneous public IoMT datasets (**CICIoMT2024** and **IoMT-TrafficData**) are reprocessed from their original raw packet captures using the **MIOTTA-NPT** preprocessing tool with an identical configuration (combined mode, window size *W = 100* packets). This yields a structurally identical 73-feature representation across sources, eliminating tool-induced heterogeneity at the root. A three-level label-harmonization scheme (binary, 6-class categorical, 26-class fine-grained), an explicit quality-assurance stage and provenance tracking produce a single ML-ready dataset of **8,011,534 records × 58 features** after cleaning.

2. **Quantification of single-source collapse versus unified generalizability.** Three classifiers (Decision Tree, Random Forest, XGBoost) are tuned under three training regimes — **B1** (CIC-only), **B2** (IoMT-only), **U** (Unified) — sharing identical splits, preprocessing and hyperparameter budgets. Single-source models *collapse* under cross-domain transfer (Macro-F1 as low as **0.0523** for B2 → CIC), whereas unified-trained models reach **Macro-F1 ≥ 0.926** on each source slice simultaneously, with XGBoost-U at **0.952** on the full mixed test set. Pairwise McNemar tests confirm both statistical and practical significance.

3. **First real-world evaluation on HospNet26.** The tuned unified models are deployed (no retraining) on **HospNet26**, a publicly released dataset of *real* internal traffic from a Helios hospital (Germany), 2025: **1,265,240 unlabelled windows of legitimate clinical traffic**. The Benign prediction rate is only **3.72 %–9.96 %**, with the bulk of windows misrouted to DoS — a clear case of laboratory-to-clinic covariate shift. The thesis discusses two concrete recalibration strategies (few-shot benign fine-tuning, post-hoc threshold calibration) as practical paths to close the gap.

---

## 3. Datasets

This repository describes work on three datasets. **The raw data itself is not included in the repository** (see Section 7); it must be obtained from the original sources.

| Dataset | Role | Domain | Records used | Source |
|---|---|---|---|---|
| **CICIoMT2024** | Training + testing (laboratory) | IoMT (multi-protocol) | 7,827,293 windows | Canadian Institute for Cybersecurity, U. of New Brunswick |
| **IoMT-TrafficData** | Training + testing (laboratory) | IoMT (hospital testbed) | 184,241 windows | INESC TEC / U. of Coimbra |
| **HospNet26** | Real-world evaluation (no training) | Real hospital network, Germany | 1,265,240 windows | Public release, 2025 |

**Note on CICIoT2023.** The original two-phase plan in this thesis envisaged a follow-up integration with **CICIoT2023** (a large general-IoT dataset) as a hypothetical *Phase 2*. **CICIoT2023 was ultimately not used** in any part of the final pipeline, in the trained models, or in the experimental evaluation reported in this work. Notebook `01_CICIoT2023_exploration.ipynb` is retained as an early exploratory artifact only, and is not part of the validated pipeline; it can be ignored by anyone interested solely in the final IoMT work. Extending the pipeline to a third source remains an item of future work.

---

## 4. Methodology

### 4.1 Unification pipeline (`src/pipeline/`)

The pipeline applies five stages to each source dataset, implemented as a reusable Python package and orchestrated by `src/pipeline/run_phase1.py`:

```
   CICIoMT2024 (raw PCAPs)        IoMT-TrafficData (raw PCAPs)
              |                             |
              +-------------+---------------+
                            v
   (i)   PCAP collection from each original source
   (ii)  MIOTTA-NPT feature extraction (combined mode, W = 100)
                 -> 73 statistical features per window
   (iii) Three-level label harmonization
                 -> label_binary (2)
                 -> label_category (6: Benign, DDoS, DoS, MQTT, Reconnaissance, Spoofing)
                 -> label_fine (26 attack sub-types)
   (iv)  Quality assurance
                 -> NaN / infinity check, type consistency
                 -> near-zero-variance feature removal -> 58 features
   (v)   Provenance-aware concatenation
                 -> source_dataset, source_file, attack_type, attack_group
                 -> stratified 70/15/15 split (by category)
                 -> StandardScaler fitted on train ONLY, applied to val/test
                            |
                            v
   Unified ML-ready dataset (8,011,534 rows x 58 features) + scaler + metadata
```

Module map (`src/pipeline/`):

| File | Responsibility |
|---|---|
| `loader.py` | Reads MIOTTA-processed CSVs, infers attack labels from filenames, attaches source-attribution metadata. |
| `harmonizer.py` | Implements the three-level label-harmonization scheme; supports two category strategies (`nature`, `mqtt`). |
| `quality.py` | NaN/infinity audit, type consistency check, near-zero-variance feature removal. |
| `scaling.py` | Stratified 70/15/15 split, `StandardScaler` (fitted on train, applied to all). |
| `exporter.py` | Persists final splits as CSV and saves the fitted scaler + run metadata to `data/processed/`. |
| `training.py` | Model training, randomized hyperparameter search, evaluation and plotting helpers shared by notebooks 08–10. |
| `config.py` | Centralised paths and metadata-column lists. |
| `run_phase1.py` | CLI entry point: `python src/pipeline/run_phase1.py --category-scheme {nature,mqtt}`. |

Two parameterised category schemes are supported:

* `nature` — groups MQTT attacks under the closest behavioural class (DoS/Reconnaissance). Outputs to `data/processed/phase1_iomt_unified/`.
* `mqtt` — keeps MQTT as a dedicated category (used in the paper). Outputs to `data/processed/phase1_iomt_unified_mqtt_category/`.

### 4.2 IDS model training and evaluation

Three classifiers are trained per regime (B1, B2, U), giving a 3 × 3 grid of tuned models:

| Notebook | Model | Tuned hyperparameters |
|---|---|---|
| `notebooks/08_phase2_model_training.ipynb` | Decision Tree | `max_depth`, `min_samples_split/leaf`, `criterion`, `max_features` |
| `notebooks/09_phase2_rf_training.ipynb`    | Random Forest | `n_estimators`, `max_depth`, `max_features`, `max_samples`, `class_weight` |
| `notebooks/10_phase2_xgb_training.ipynb`   | XGBoost       | `learning_rate`, `n_estimators`, `max_depth`, `min_child_weight`, `subsample`, `colsample_bytree`, `gamma`, `reg_lambda`, `reg_alpha` |

Tuning protocol:

* Randomized search, *n* = 50 trials, 3-fold cross-validation, scored by **Macro-F1**, fixed random seed 42.
* Class imbalance handled by `class_weight='balanced'` (DT/RF) or explicit `sample_weight` (XGBoost). No SMOTE/oversampling: with > 8 × 10⁶ records, class weights provide sufficient gradient signal for minority classes.
* For each (model, regime) pair a *baseline* (default hyperparameters) and a *tuned* model are saved, together with full evaluation artifacts.

Evaluation suite (per model & regime):

* Macro-F1 on the full mixed test set and on each source slice independently.
* Per-class precision/recall/F1, normalized confusion matrices.
* Pairwise **McNemar tests** with Yates continuity correction + **Relative Error Reduction (RER)** for practical-significance estimation.
* Cross-domain transfer matrix (e.g., B1 → IoMT slice, B2 → CIC slice) to measure single-source collapse.

### 4.3 Real-world evaluation on HospNet26

* Reads HospNet26 *combined-feature* Parquet files (Friday, Weekend, Monday, Monday-to-Friday).
* Selects the strict subset of 58 MIOTTA window-based columns matching the unified training schema.
* Applies the **same** `StandardScaler` fitted on the unified training split — *no refitting* on HospNet26 (strict no-leakage protocol).
* Runs inference with the three tuned Unified models.
* Reports the **Benign prediction rate** *r_B* (= specificity on real clinical traffic, since every window is documented as benign by construction) and the false-positive class distribution.

---

## 5. Key Results

### 5.1 Single-source models collapse cross-domain (Macro-F1)

| Regime | Model | CIC slice | IoMT slice | Full test |
|---|---|---:|---:|---:|
| B1 (CIC-only)  | DT  | 0.9226 (in) | 0.2474 (cross) | 0.6959 |
| B1 (CIC-only)  | RF  | 0.9149 (in) | 0.3423 (cross) | 0.7395 |
| B1 (CIC-only)  | XGB | 0.9410 (in) | 0.2724 (cross) | 0.7199 |
| B2 (IoMT-only) | DT  | 0.0523 (cross) | 0.8332 (in) | 0.3284 |
| B2 (IoMT-only) | RF  | 0.0586 (cross) | 0.8333 (in) | 0.2029 |
| B2 (IoMT-only) | XGB | 0.1079 (cross) | 0.8333 (in) | 0.3708 |

### 5.2 Unified-trained models resolve the cross-domain gap

| Model | CIC slice | IoMT slice* | Full test |
|---|---:|---:|---:|
| Decision Tree | 0.9262 | 0.9990 | 0.9480 |
| Random Forest | 0.9285 | 0.9995 | 0.9487 |
| XGBoost       | 0.9382 | 0.9999 | **0.9522** |

*IoMT slice F1 computed over the 5 classes actually present (no DDoS in IoMT-TrafficData).*

→ Switching from the best single-source baseline (0.7395) to the weakest unified model (0.9480) yields **+20.85 percentage points**, *much* larger than any model-choice effect (≤ 0.42 pp).

### 5.3 Laboratory-to-clinic gap on HospNet26 (1.26 × 10⁶ real-hospital windows)

| Model | Benign | DDoS | DoS | MQTT | Recon. | Spoofing |
|---|---:|---:|---:|---:|---:|---:|
| Decision Tree | 6.07 % | 7.80 % | 72.04 % | 0.22 % | 5.30 % | 8.57 % |
| Random Forest | 3.72 % | 0.60 % | 71.37 % | 0.06 % | 19.08 % | 5.17 % |
| XGBoost       | 9.96 % | 23.80 % | 51.14 % | 0.11 % | 4.28 % | 10.71 % |

The same models that achieve Macro-F1 ≥ 0.948 on the laboratory test set correctly recognise only **3.72 %–9.96 %** of legitimate clinical traffic as Benign. The dominant false-positive class is DoS, consistent with the bursty packet-rate signatures of medical-imaging (DICOM/PACS) and bulk EMR synchronisation traffic. Weekend windows yield *lower* Benign rates than weekdays, hinting at additional temporally non-stationary shift.

This is **not** model failure but **covariate shift**: the conditional distribution *p(x | y = Benign)* in the laboratory training data differs systematically from the real clinical distribution. The thesis discusses two practical recalibration strategies (few-shot benign fine-tuning, post-hoc threshold calibration) that require only benign hospital traffic — abundant in any live network — and avoid the ethical issues of labelled attack collection in production.

---

## 6. Repository Structure

```
diploma-thesis-iomt-ids/
├── README.md
├── requirements.txt                   # Python dependencies (>= 3.10)
│
├── src/pipeline/                      # Reusable unification + training package
│   ├── config.py                      # Paths and metadata-column lists
│   ├── loader.py                      # MIOTTA CSV loading + provenance
│   ├── harmonizer.py                  # 3-level label harmonization
│   ├── quality.py                     # NaN/inf / near-zero-variance audit
│   ├── scaling.py                     # Stratified split + StandardScaler
│   ├── exporter.py                    # Splits + scaler + metadata persistence
│   ├── training.py                    # Training, tuning and evaluation helpers
│   └── run_phase1.py                  # CLI entry point
│
├── notebooks/
│   ├── 01_CICIoT2023_exploration.ipynb            # Early exploration only, not used in the final pipeline
│   ├── 02_CICIoMT2024_exploration.ipynb           # Dataset profiling: CICIoMT2024
│   ├── 03_comparative_analysis.ipynb              # Early comparative analysis (exploratory)
│   ├── 04_pipeline_proposal.ipynb                 # Early pipeline proposal (exploratory)
│   ├── 05_IoMT-TrafficData_exploration.ipynb      # Dataset profiling: IoMT-TrafficData
│   ├── 06_MIOTTA_datasets_exploration.ipynb       # Profiling of MIOTTA-processed datasets
│   ├── 07_phase1_iomt_unification.ipynb           # Phase 1: unification pipeline
│   ├── 08_phase2_model_training.ipynb             # Phase 2: Decision Tree
│   ├── 09_phase2_rf_training.ipynb                # Phase 2: Random Forest
│   ├── 10_phase2_xgb_training.ipynb               # Phase 2: XGBoost
│   └── 11_hospnet26_inference.ipynb               # Real-hospital evaluation on HospNet26
│
├── scripts/
│   ├── download_datasets.sh           # Dataset download instructions
│   ├── download_all.sh                # All-in-one download script
│   ├── verify_datasets.py             # Checksums and structural verification
│   ├── run_dt_tuning.py               # Stand-alone Decision Tree randomized search
│   ├── build_hospnet26_notebook.py    # Generates notebook 11
│   ├── generate_report_figures.py     # Thesis figures
│   ├── generate_ch4_figures.py        # Chapter 4 figures
│   └── generate_dt_figures.py         # Decision Tree figures
│
├── paper/                             # Research paper (LNCS format)
│   ├── main.pdf                       # Author's accepted manuscript
│   ├── main.tex, references.bib
│   └── figures/
│
├── report/                            # Thesis (LaTeX)
│   ├── main.tex / main.pdf            # UPC edition
│   ├── main_ntua.tex                  # NTUA edition (same chapters, Greek front matter)
│   ├── ntua/main_ntua_final.pdf       # NTUA edition, compiled
│   ├── frontmatter/, chapters/, backmatter/, figures/
│   └── references.bib
│
├── docs/
│   └── dataset_metadata.json          # Column dictionary of the unified dataset
│
└── data/processed/                    # Only small reproducibility artifacts are kept in Git
    ├── phase1_iomt_unified/
    │   ├── metadata.joblib            # Feature list, dropped features, label maps
    │   └── scaler.joblib              # Fitted StandardScaler
    └── phase1_iomt_unified_mqtt_category/
        ├── metadata.joblib
        ├── scaler.joblib              # Scaler reused for HospNet26 inference
        ├── abstract_for_Dataverse_EN.txt
        └── ReadmeCSUC_ENG (1).txt     # README of the published dataset
```

---

## 7. What Is and Is NOT in This Repository (and Why)

This Git repository contains **only the code, notebooks, paper, thesis and small reproducibility artifacts** (preprocessing scalers, metadata, dataset README). It does **not** contain the raw or processed network data, nor the trained model files. The unified dataset itself is published separately at [doi.org/10.34810/DATA3305](https://doi.org/10.34810/DATA3305). The exclusions, configured in `.gitignore`, are:

| Path | Approx. size | Reason for exclusion |
|---|---:|---|
| `data/raw/`                                       | ~17 GB | CIC datasets and HospNet26 are licensed by their respective providers (Canadian Institute for Cybersecurity, INESC TEC, the HospNet26 release). Redistribution via a third-party Git repository is not permitted. The data must be downloaded from the official sources. |
| `data/processed/**/*.csv`, `**/*.parquet`         | ~13 GB | Large preprocessed splits exceed GitHub's 100 MB per-file limit (single files reach ~4.4 GB). Available from the dataset DOI above, or regenerable from the raw data using `src/pipeline/run_phase1.py` (or notebook 07). |
| `data/processed/hospnet26_processed.joblib`       | 298 MB | Above GitHub's 100 MB per-file limit. Regenerable from HospNet26's combined Parquet files via the inference notebook. |
| `results/`                                        | ~23 GB | Trained `.joblib` model files (some single files exceed **11 GB**). Beyond the size limit, serialized tree models can expose sensitive properties of the training data. Fully regenerable by running notebooks `08`/`09`/`10`. |
| `venv/`                                           | ~750 MB | Local Python virtual environment, machine-specific. Recreate with the steps in Section 8. |
| `*.env`, `*.key`, `*.pem`, `credentials.json`, `.DS_Store` | — | Defensive defaults to prevent accidental secret or OS-metadata commits. |

Everything required to **rebuild the unified dataset and reproduce every result** is present in the repository in the form of source code, notebooks and small artifacts (scaler, metadata). The only step that requires external action is obtaining the raw datasets from their original providers.

---

## 8. Setup and Reproduction

### 8.1 Prerequisites

* Python **>= 3.10**
* Roughly 100 GB free disk space if you intend to materialise the raw + processed data + trained models
* (Optional) A workstation or HPC node with at least 32 GB RAM for the unification step on full data, and a machine with enough memory for Random Forest training on > 5 M rows

### 8.2 Environment

```bash
git clone https://github.com/pantelis6/diploma-thesis-iomt-ids.git
cd diploma-thesis-iomt-ids

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 8.3 Data acquisition

The raw datasets are not redistributed here. Obtain them from the official sources:

* **CICIoMT2024** — https://www.unb.ca/cic/datasets/iomt-dataset-2024.html
* **IoMT-TrafficData** — see the original release (INESC TEC / U. of Coimbra)
* **HospNet26** — https://doi.org/10.34810/data3050

After downloading, place the CSV/Parquet files under `data/raw/` following the layout expected by `src/pipeline/config.py`.

The two IoMT datasets must additionally be reprocessed through **MIOTTA-NPT** before the unification pipeline can consume them. MIOTTA-NPT is an external tool maintained by the MIOTTA research group: https://github.com/miotta2025/network-preprocessing-tool. The required configuration is:

```
mode        = combined (flow + window)
window size = 100 packets
```

Helper scripts under `scripts/` (`download_datasets.sh`, `download_all.sh`, `verify_datasets.py`) document and automate parts of this acquisition step.

### 8.4 Reproducing the unified dataset

```bash
python src/pipeline/run_phase1.py --category-scheme mqtt
```

This will:

1. Load the MIOTTA-processed CSVs of both IoMT datasets.
2. Verify cross-source feature alignment.
3. Apply three-level label harmonization.
4. Concatenate with provenance tracking.
5. Run the QA stage (NaN/inf check, near-zero-variance removal → 58 features).
6. Perform stratified 70/15/15 split.
7. Fit `StandardScaler` on the training split and apply it to all partitions.
8. Persist final splits, scaler and metadata under `data/processed/phase1_iomt_unified_mqtt_category/`.

Use `--category-scheme nature` for the alternative grouping (no dedicated MQTT class).

Equivalent notebook entry point: `notebooks/07_phase1_iomt_unification.ipynb`.

### 8.5 Reproducing the IDS experiments

Run the three model-specific notebooks in order:

```
notebooks/08_phase2_model_training.ipynb    # Decision Tree (B1, B2, U; baseline + tuned)
notebooks/09_phase2_rf_training.ipynb       # Random Forest (B1, B2, U; baseline + tuned)
notebooks/10_phase2_xgb_training.ipynb      # XGBoost (B1, B2, U; baseline + tuned)
```

Each notebook performs randomized hyperparameter search, refits on the full training split, computes Macro-F1 / per-class metrics / normalized confusion matrices on the three test slices, and (for selected pairs) runs paired McNemar tests with Relative Error Reduction.

### 8.6 Reproducing the HospNet26 evaluation

Run `notebooks/11_hospnet26_inference.ipynb` (generated by `scripts/build_hospnet26_notebook.py`). The inference step reuses the saved `scaler.joblib` and the tuned Unified models. It applies the *same* fitted scaler — without refitting — and runs inference on the four HospNet26 combined-feature Parquet files. The Benign prediction rate and per-class false-positive distribution reproduce the numbers in Section 5.3 of this document and Section 6 of the paper.

---

## 9. Limitations and Future Work

The paper and the thesis explicitly acknowledge three threats to validity:

1. **Tree-based models only.** Deep architectures on per-packet representations (e.g., nPrint-style) may interact differently with covariate shift; this is left as future work.
2. **Two-source integration.** Extending the pipeline to a third source — for example, CICIoT2023 via the same MIOTTA-NPT route — may reveal attack-class-coverage gaps that are not visible with two sources only.
3. **Recalibration strategies are described but not yet empirically validated.** Quantifying how many supervised benign hospital windows are required to push the Benign prediction rate above 0.90 on HospNet26 is the natural next experimental step.

Additional future directions:

* Sequence and packet-level deep architectures on raw or per-packet representations.
* Feature engineering targeted at the DDoS ↔ DoS boundary (e.g., source-address diversity, flow-volume asymmetry).
* Operational deployment study tracking concept drift and alert fatigue with recalibrated models.

---

## 10. Citation

If you use this code or refer to the methodology, please cite the paper:

> P. Petrakis, J. Doménech, O. León, I. V. Martin-Faus and J. Pegueroles.
> *Unifying Heterogeneous IoMT Datasets for Intrusion Detection: From Laboratory Testbeds to Real Hospital Network Evaluation.*
> In: Afzal, Z., Kochberger, P., Atli, B., Asplund, M. (eds) Availability, Reliability and Security. ARES 2026 International Workshops. Lecture Notes in Computer Science, vol 16901. Springer, Cham.
> https://doi.org/10.1007/978-3-032-35579-9_7

```bibtex
@inproceedings{petrakis_unifying_iomt,
  author    = {Petrakis, Pantelis and Dom{\'e}nech, Jordi and Le{\'o}n, Olga and Martin-Faus, Isabel V. and Pegueroles, Josep},
  title     = {Unifying Heterogeneous {IoMT} Datasets for Intrusion Detection: From Laboratory Testbeds to Real Hospital Network Evaluation},
  booktitle = {Availability, Reliability and Security. {ARES} 2026 International Workshops},
  editor    = {Afzal, Zeeshan and Kochberger, Patrick and Atli, Buse and Asplund, Mikael},
  series    = {Lecture Notes in Computer Science},
  volume    = {16901},
  publisher = {Springer, Cham},
  doi       = {10.1007/978-3-032-35579-9_7}
}
```

For the publication year and page numbers, use the citation export on the publisher's page.

If you use the unified dataset, please also cite it:

> P. Petrakis, J. Doménech Fons, O. León, I. V. Martin-Faus and J. Pegueroles. *CICIoMT2024 + IoMT-TrafficData: a unified heterogeneous IoMT dataset for intrusion detection.* CORA Research Data Repository, 2026. https://doi.org/10.34810/DATA3305

`paper/main.pdf` is the author-created accepted manuscript. The final authenticated version is available online at https://doi.org/10.1007/978-3-032-35579-9_7.

---

## 11. Acknowledgements

This work was carried out at the **Information Security Group / Mathematics Applied to Cryptography (ISG-MAK)**, Universitat Politècnica de Catalunya (UPC). Partial support is acknowledged from the **INCIBE CARISMATICA Chair of Cybersecurity** and the Generalitat de Catalunya grant **2024 FI-1 00643**.

The CICIoMT2024 dataset is provided by the **Canadian Institute for Cybersecurity** (University of New Brunswick). IoMT-TrafficData is provided by **INESC TEC / University of Coimbra**. HospNet26 is published by its authors on the CORA Research Data Repository. All datasets remain the property of their respective providers and are subject to their original licensing terms. This repository contains no third-party data, only the code and documentation produced by the author for the purposes of this thesis.
