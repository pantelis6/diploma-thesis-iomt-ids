# Diploma Thesis: IoT & IoMT Network Intrusion Detection

## Overview

Diploma thesis project focused on building a unified ML-based intrusion detection system (IDS) by integrating two major CIC datasets:

- **CICIoT2023** — General IoT dataset with 33 attack types across 105 devices
- **CICIoMT2024** — IoMT-specific dataset with 18 attack types across 40 medical devices

The goal is to propose and implement a data integration pipeline that merges these datasets into a unified, ML-ready dataset for training and evaluating intrusion detection models.

## Project Structure

```
diploma_thesis/
├── data/
│   ├── raw/
│   │   ├── CICIoT2023/          # Raw CSV files from CICIoT2023 dataset
│   │   └── CICIoMT2024/         # Raw CSV files from CICIoMT2024 dataset
│   └── processed/               # Merged/cleaned data (generated)
├── notebooks/
│   ├── 01_CICIoT2023_exploration.ipynb
│   ├── 02_CICIoMT2024_exploration.ipynb
│   ├── 03_comparative_analysis.ipynb
│   └── 04_pipeline_proposal.ipynb
├── src/                         # Reusable Python modules
├── docs/                        # Pipeline proposal document
├── references/                  # Research papers (PDFs)
├── scripts/                     # Data download & utility scripts
├── requirements.txt
└── README.md
```

## Datasets

### CICIoT2023

- **Source**: [CIC Research - IoT Dataset 2023](https://www.unb.ca/cic/datasets/iomt-dataset-2024.html)
- **Contents**: Network traffic from 105 IoT devices, 33 attack types
- **Format**: CSV files with ~46 flow-level features (window-based aggregation)
- **Labels**: Binary (Benign/Attack), 8-class, and 34-class taxonomies

### CICIoMT2024

- **Source**: [CIC Research - IoMT Dataset 2024](https://www.unb.ca/cic/datasets/iomt-dataset-2024.html)
- **Contents**: Network traffic from 40 IoMT (medical) devices, 18 attack types
- **Format**: CSV files with flow-level features (WiFi/MQTT and BLE protocols)
- **Labels**: DDoS, DoS, Recon, MQTT attacks, Spoofing, Profiling

## Setup

### Prerequisites

- Python >= 3.10
- pip

### Installation

```bash
# Clone or navigate to the project directory
cd diploma_thesis

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Download Datasets

See `scripts/download_datasets.sh` for instructions and automated download scripts.

## Phase 1: Dataset Understanding, Analysis & Pipeline Proposal

1. **Dataset Exploration**: Individual analysis of each dataset (features, labels, distributions)
2. **Comparative Analysis**: Feature mapping, label overlap, statistical comparison
3. **Pipeline Proposal**: Justified data integration pipeline (flow-level, CSV-based)

## Proposed Integration Pipeline

```
CICIoT2023 CSVs ──┐
                   ├─→ Feature Schema Mapping → Feature Alignment → Label Harmonization
CICIoMT2024 CSVs ─┘     → Data Cleaning → Class Balance Analysis → Train/Test Split
                           → Integrated ML-Ready Dataset
```

## Supervisors

- Prof. Josep Pegueroles (UPC)
- PhD Candidate Doménech (UPC)

## Repository Contents and Data Availability

This Git repository contains only the **code, notebooks, documentation, paper, report and small research artifacts** (preprocessing scalers, metadata, README/abstract files).

The following content is **intentionally excluded** from the repository (see `.gitignore`):

- `data/raw/` — Raw CIC datasets. These are licensed by the Canadian Institute for Cybersecurity and cannot be redistributed. Download them through the official CIC portal.
- `data/processed/*.csv` and `data/processed/*.parquet` — Large preprocessed splits (>13 GB). They can be regenerated from the raw data using the pipeline notebooks (`07_phase1_iomt_unification.ipynb`).
- `results/` — Trained model files and evaluation artifacts (some individual files exceed 10 GB, far above GitHub's 100 MB per-file limit). Run the training notebooks (`08_*`, `09_*`, `10_*`) to recreate them.
- `venv/` — Local Python virtual environment (recreate with `python3 -m venv venv && pip install -r requirements.txt`).

## License

This project is part of a diploma thesis. All datasets are provided by the Canadian Institute for Cybersecurity (CIC).
