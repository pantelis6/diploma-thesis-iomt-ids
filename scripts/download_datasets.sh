#!/bin/bash
# =============================================================================
# Download Script for CICIoT2023 & CICIoMT2024 Datasets
# =============================================================================
#
# ΣΗΜΑΝΤΙΚΟ: Και τα δύο datasets απαιτούν εγγραφή μέσω φόρμας στο CIC website.
# Αυτό το script παρέχει οδηγίες και εναλλακτικές μεθόδους download.
#
# =============================================================================

set -e

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${PROJECT_ROOT}/data/raw"

echo "=============================================="
echo "  Dataset Download Instructions"
echo "=============================================="
echo ""
echo "Project root: ${PROJECT_ROOT}"
echo "Data directory: ${DATA_DIR}"
echo ""

# -----------------------------------------------------------------------------
# ΜΕΘΟΔΟΣ 1: CIC Website (Επίσημη πηγή - Απαιτεί εγγραφή)
# -----------------------------------------------------------------------------
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ΜΕΘΟΔΟΣ 1: CIC Website (Επίσημη πηγή)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Βήμα 1: Πήγαινε στις παρακάτω σελίδες και συμπλήρωσε τη φόρμα εγγραφής:"
echo ""
echo "  CICIoT2023:  http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/"
echo "  CICIoMT2024: http://cicresearch.ca/IOTDataset/CICIoMT2024/"
echo ""
echo "Βήμα 2: Μετά την υποβολή, θα λάβεις email με download link."
echo ""
echo "Βήμα 3: Κατέβασε τα αρχεία και τοποθέτησέ τα ως εξής:"
echo ""
echo "  CICIoT2023 CSVs → ${DATA_DIR}/CICIoT2023/"
echo "  CICIoMT2024 CSVs → ${DATA_DIR}/CICIoMT2024/"
echo ""
echo "  Για το CICIoMT2024, τα CSV αρχεία βρίσκονται στο subdirectory:"
echo "  WiFi_and_MQTT/attacks/csv/"
echo ""

# -----------------------------------------------------------------------------
# ΜΕΘΟΔΟΣ 2: Kaggle (Εναλλακτική πηγή για CICIoT2023)
# -----------------------------------------------------------------------------
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ΜΕΘΟΔΟΣ 2: Kaggle (Εναλλακτική για CICIoT2023)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Αν έχεις Kaggle account, μπορείς να κατεβάσεις το CICIoT2023 από εκεί."
echo ""
echo "Βήμα 1: Εγκατάστησε kaggle CLI (αν δεν υπάρχει ήδη):"
echo "  pip install kaggle"
echo ""
echo "Βήμα 2: Ρύθμισε Kaggle API credentials:"
echo "  - Πήγαινε στο https://www.kaggle.com/settings"
echo "  - Πάτα 'Create New Token' → κατεβαίνει kaggle.json"
echo "  - Τοποθέτησέ το: ~/.kaggle/kaggle.json"
echo "  - chmod 600 ~/.kaggle/kaggle.json"
echo ""

# Check if kaggle CLI is available
if command -v kaggle &> /dev/null; then
    echo "Kaggle CLI εντοπίστηκε! Θέλεις να κατεβάσεις το CICIoT2023 από Kaggle; (y/n)"
    read -r REPLY
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Downloading CICIoT2023 from Kaggle..."
        mkdir -p "${DATA_DIR}/CICIoT2023"
        kaggle datasets download -d madhavmalhotra/unb-cic-iot-dataset \
            -p "${DATA_DIR}/CICIoT2023" --unzip
        echo "Download ολοκληρώθηκε! Αρχεία στο: ${DATA_DIR}/CICIoT2023/"
    fi
else
    echo "Kaggle CLI δεν βρέθηκε. Για αυτόματο download, εκτέλεσε:"
    echo "  pip install kaggle"
    echo ""
    echo "Εναλλακτικά, κατέβασε χειροκίνητα από:"
    echo "  https://www.kaggle.com/datasets/madhavmalhotra/unb-cic-iot-dataset"
    echo "  https://www.kaggle.com/datasets/himadri07/ciciot2023"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ΜΕΤΑ ΤΟ DOWNLOAD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Εκτέλεσε το verification script για να ελέγξεις τα αρχεία:"
echo "  cd ${PROJECT_ROOT}"
echo "  source venv/bin/activate"
echo "  python scripts/verify_datasets.py"
echo ""
