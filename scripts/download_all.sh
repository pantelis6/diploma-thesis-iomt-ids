#!/bin/bash
# =============================================================================
# Automated Download Script - CICIoT2023 & CICIoMT2024 CSV Datasets
# =============================================================================
# Κατεβάζει τα CSV αρχεία από τον CIC server.
# Απαιτεί: curl (προεγκατεστημένο σε macOS)
#
# Χρήση:
#   bash scripts/download_all.sh
#
# Τα αρχεία κατεβαίνουν 4 ταυτόχρονα (parallel) για ταχύτητα.
# =============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${PROJECT_ROOT}/data/raw"
MAX_PARALLEL=4

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ---------------------------------------------------------------------------
# Helper: Download a single file with resume support
# ---------------------------------------------------------------------------
download_file() {
    local url="$1"
    local dest="$2"
    local filename
    filename=$(basename "$dest")

    if [[ -f "$dest" ]]; then
        # Check if file is complete by comparing size
        local remote_size
        remote_size=$(curl -sI "$url" | grep -i content-length | awk '{print $2}' | tr -d '\r')
        local local_size
        local_size=$(stat -f%z "$dest" 2>/dev/null || stat --printf="%s" "$dest" 2>/dev/null)

        if [[ "$local_size" == "$remote_size" ]]; then
            echo -e "  ${GREEN}[SKIP]${NC} ${filename} (ήδη υπάρχει, ${local_size} bytes)"
            return 0
        else
            echo -e "  ${YELLOW}[RESUME]${NC} ${filename} (${local_size}/${remote_size} bytes)"
        fi
    else
        echo -e "  [DL] ${filename}"
    fi

    curl -s -C - -o "$dest" "$url"
    echo -e "  ${GREEN}[OK]${NC} ${filename}"
}

export -f download_file
export GREEN YELLOW RED NC

# ---------------------------------------------------------------------------
# CICIoT2023 - MERGED CSV (63 files)
# ---------------------------------------------------------------------------
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CICIoT2023 - Downloading MERGED CSV files"
echo "  Source: cicresearch.ca/.../MERGED_CSV/"
echo "  Destination: ${DATA_DIR}/CICIoT2023/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CICIOT2023_BASE="http://cicresearch.ca/IOTDataset/CIC_IOT_Dataset2023/Dataset/CSV/MERGED_CSV"
CICIOT2023_DIR="${DATA_DIR}/CICIoT2023"
mkdir -p "${CICIOT2023_DIR}"

# Generate file list
for i in $(seq -w 1 63); do
    # Remove leading zeros for numbers > 9 (files are Merged01..Merged63 with zero-padded 01-09)
    num=$(echo "$i" | sed 's/^0//')
    if [ "$num" -lt 10 ]; then
        fname="Merged0${num}.csv"
    else
        fname="Merged${num}.csv"
    fi
    echo "${CICIOT2023_BASE}/${fname} ${CICIOT2023_DIR}/${fname}"
done | xargs -P ${MAX_PARALLEL} -L 1 bash -c 'download_file $0 $1'

echo ""
echo -e "${GREEN}CICIoT2023 download ολοκληρώθηκε!${NC}"

# ---------------------------------------------------------------------------
# CICIoMT2024 - WiFi/MQTT attacks CSV (train + test)
# ---------------------------------------------------------------------------
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CICIoMT2024 - Downloading WiFi/MQTT CSV files"
echo "  Source: cicresearch.ca/.../WiFI_and_MQTT/attacks/CSV/"
echo "  Destination: ${DATA_DIR}/CICIoMT2024/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CICIOMT2024_BASE="http://cicresearch.ca/IOTDataset/CICIoMT2024/Dataset/WiFI_and_MQTT/attacks/CSV"
CICIOMT2024_DIR="${DATA_DIR}/CICIoMT2024"
mkdir -p "${CICIOMT2024_DIR}/train"
mkdir -p "${CICIOMT2024_DIR}/test"

# Train files
TRAIN_FILES=(
    "ARP_Spoofing_train.pcap.csv"
    "Benign_train.pcap.csv"
    "MQTT-DDoS-Connect_Flood_train.pcap.csv"
    "MQTT-DDoS-Publish_Flood_train.pcap.csv"
    "MQTT-DoS-Connect_Flood_train.pcap.csv"
    "MQTT-DoS-Publish_Flood_train.pcap.csv"
    "MQTT-Malformed_Data_train.pcap.csv"
    "Recon-OS_Scan_train.pcap.csv"
    "Recon-Ping_Sweep_train.pcap.csv"
    "Recon-Port_Scan_train.pcap.csv"
    "Recon-VulScan_train.pcap.csv"
    "TCP_IP-DDoS-ICMP1_train.pcap.csv"
    "TCP_IP-DDoS-ICMP2_train.pcap.csv"
    "TCP_IP-DDoS-ICMP3_train.pcap.csv"
    "TCP_IP-DDoS-ICMP4_train.pcap.csv"
    "TCP_IP-DDoS-ICMP5_train.pcap.csv"
    "TCP_IP-DDoS-ICMP6_train.pcap.csv"
    "TCP_IP-DDoS-ICMP7_train.pcap.csv"
    "TCP_IP-DDoS-ICMP8_train.pcap.csv"
    "TCP_IP-DDoS-SYN1_train.pcap.csv"
    "TCP_IP-DDoS-SYN2_train.pcap.csv"
    "TCP_IP-DDoS-SYN3_train.pcap.csv"
    "TCP_IP-DDoS-SYN4_train.pcap.csv"
    "TCP_IP-DDoS-TCP1_train.pcap.csv"
    "TCP_IP-DDoS-TCP2_train.pcap.csv"
    "TCP_IP-DDoS-TCP3_train.pcap.csv"
    "TCP_IP-DDoS-TCP4_train.pcap.csv"
    "TCP_IP-DDoS-UDP1_train.pcap.csv"
    "TCP_IP-DDoS-UDP2_train.pcap.csv"
    "TCP_IP-DDoS-UDP3_train.pcap.csv"
    "TCP_IP-DDoS-UDP4_train.pcap.csv"
    "TCP_IP-DDoS-UDP5_train.pcap.csv"
    "TCP_IP-DDoS-UDP6_train.pcap.csv"
    "TCP_IP-DDoS-UDP7_train.pcap.csv"
    "TCP_IP-DDoS-UDP8_train.pcap.csv"
    "TCP_IP-DoS-ICMP1_train.pcap.csv"
    "TCP_IP-DoS-ICMP2_train.pcap.csv"
    "TCP_IP-DoS-ICMP3_train.pcap.csv"
    "TCP_IP-DoS-ICMP4_train.pcap.csv"
    "TCP_IP-DoS-SYN1_train.pcap.csv"
    "TCP_IP-DoS-SYN2_train.pcap.csv"
    "TCP_IP-DoS-SYN3_train.pcap.csv"
    "TCP_IP-DoS-SYN4_train.pcap.csv"
    "TCP_IP-DoS-TCP1_train.pcap.csv"
    "TCP_IP-DoS-TCP2_train.pcap.csv"
    "TCP_IP-DoS-TCP3_train.pcap.csv"
    "TCP_IP-DoS-TCP4_train.pcap.csv"
    "TCP_IP-DoS-UDP1_train.pcap.csv"
    "TCP_IP-DoS-UDP2_train.pcap.csv"
    "TCP_IP-DoS-UDP3_train.pcap.csv"
    "TCP_IP-DoS-UDP4_train.pcap.csv"
)

# Test files
TEST_FILES=(
    "ARP_Spoofing_test.pcap.csv"
    "Benign_test.pcap.csv"
    "MQTT-DDoS-Connect_Flood_test.pcap.csv"
    "MQTT-DDoS-Publish_Flood_test.pcap.csv"
    "MQTT-DoS-Connect_Flood_test.pcap.csv"
    "MQTT-DoS-Publish_Flood_test.pcap.csv"
    "MQTT-Malformed_Data_test.pcap.csv"
    "Recon-OS_Scan_test.pcap.csv"
    "Recon-Ping_Sweep_test.pcap.csv"
    "Recon-Port_Scan_test.pcap.csv"
    "Recon-VulScan_test.pcap.csv"
    "TCP_IP-DDoS-ICMP1_test.pcap.csv"
    "TCP_IP-DDoS-ICMP2_test.pcap.csv"
    "TCP_IP-DDoS-SYN_test.pcap.csv"
    "TCP_IP-DDoS-TCP_test.pcap.csv"
    "TCP_IP-DDoS-UDP1_test.pcap.csv"
    "TCP_IP-DDoS-UDP2_test.pcap.csv"
    "TCP_IP-DoS-ICMP_test.pcap.csv"
    "TCP_IP-DoS-SYN_test.pcap.csv"
    "TCP_IP-DoS-TCP_test.pcap.csv"
    "TCP_IP-DoS-UDP_test.pcap.csv"
)

echo "  Train files (${#TRAIN_FILES[@]} αρχεία)..."
for f in "${TRAIN_FILES[@]}"; do
    echo "${CICIOMT2024_BASE}/train/${f} ${CICIOMT2024_DIR}/train/${f}"
done | xargs -P ${MAX_PARALLEL} -L 1 bash -c 'download_file $0 $1'

echo ""
echo "  Test files (${#TEST_FILES[@]} αρχεία)..."
for f in "${TEST_FILES[@]}"; do
    echo "${CICIOMT2024_BASE}/test/${f} ${CICIOMT2024_DIR}/test/${f}"
done | xargs -P ${MAX_PARALLEL} -L 1 bash -c 'download_file $0 $1'

echo ""
echo -e "${GREEN}CICIoMT2024 download ολοκληρώθηκε!${NC}"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ΣΥΝΟΨΗ DOWNLOADS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

CICIOT_COUNT=$(find "${CICIOT2023_DIR}" -name "*.csv" | wc -l | tr -d ' ')
CICIOT_SIZE=$(du -sh "${CICIOT2023_DIR}" 2>/dev/null | cut -f1)
echo "  CICIoT2023:  ${CICIOT_COUNT} CSV files (${CICIOT_SIZE})"

CICIOMT_COUNT=$(find "${CICIOMT2024_DIR}" -name "*.csv" | wc -l | tr -d ' ')
CICIOMT_SIZE=$(du -sh "${CICIOMT2024_DIR}" 2>/dev/null | cut -f1)
echo "  CICIoMT2024: ${CICIOMT_COUNT} CSV files (${CICIOMT_SIZE})"

echo ""
echo "  Εκτέλεσε verification:"
echo "  python scripts/verify_datasets.py"
echo ""
