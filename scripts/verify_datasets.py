#!/usr/bin/env python3
"""
Dataset Verification & Organization Script
===========================================

Αυτό το script ελέγχει ότι τα datasets έχουν κατέβει σωστά,
εμφανίζει πληροφορίες για τα αρχεία, και βοηθά στην οργάνωσή τους.

Χρήση:
    python scripts/verify_datasets.py
"""

import os
import sys
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

CICIOT2023_DIR = DATA_DIR / "CICIoT2023"
CICIOMT2024_DIR = DATA_DIR / "CICIoMT2024"

# Expected features for CICIoT2023 (46 features + label)
CICIOT2023_EXPECTED_FEATURES = [
    'flow_duration', 'Header_Length', 'Protocol Type', 'Duration',
    'Rate', 'Srate', 'Drate', 'fin_flag_number', 'syn_flag_number',
    'rst_flag_number', 'psh_flag_number', 'ack_flag_number',
    'ece_flag_number', 'cwr_flag_number', 'ack_count',
    'syn_count', 'fin_count', 'urg_count', 'rst_count',
    'HTTP', 'HTTPS', 'DNS', 'Telnet', 'SMTP', 'SSH', 'IRC', 'TCP',
    'UDP', 'DHCP', 'ARP', 'ICMP', 'IPv', 'LLC', 'Tot sum', 'Min',
    'Max', 'AVG', 'Std', 'Tot size', 'IAT', 'Number', 'Magnitue',
    'Radius', 'Covariance', 'Variance', 'Weight', 'label',
]

# Expected CICIoT2023 attack labels (34-class taxonomy)
CICIOT2023_EXPECTED_LABELS = [
    'BenignTraffic',
    # DDoS
    'DDoS-RSTFINFlood', 'DDoS-PSHACK_Flood', 'DDoS-SYN_Flood',
    'DDoS-UDP_Flood', 'DDoS-TCP_Flood', 'DDoS-ICMP_Flood',
    'DDoS-SynonymousIP_Flood', 'DDoS-ACK_Fragmentation',
    'DDoS-UDP_Fragmentation', 'DDoS-ICMP_Fragmentation',
    'DDoS-SlowLoris', 'DDoS-HTTP_Flood',
    # DoS
    'DoS-UDP_Flood', 'DoS-SYN_Flood', 'DoS-TCP_Flood', 'DoS-HTTP_Flood',
    # Mirai
    'Mirai-greeth_flood', 'Mirai-greip_flood', 'Mirai-udpplain',
    # Recon
    'Recon-PingSweep', 'Recon-OSScan', 'Recon-PortScan',
    'VulnerabilityScan', 'Recon-HostDiscovery',
    # Spoofing
    'DNS_Spoofing', 'MITM-ArpSpoofing',
    # Web
    'BrowserHijacking', 'Backdoor_Malware', 'XSS',
    'Uploading_Attack', 'SqlInjection', 'CommandInjection',
    # Brute Force
    'DictionaryBruteForce',
]

# Expected CICIoMT2024 attack categories
CICIOMT2024_EXPECTED_CATEGORIES = [
    'Benign',
    # DDoS
    'DDoS-SYN_Flood', 'DDoS-TCP_Flood', 'DDoS-ICMP_Flood', 'DDoS-UDP_Flood',
    # DoS
    'DoS-SYN_Flood', 'DoS-TCP_Flood', 'DoS-ICMP_Flood', 'DoS-UDP_Flood',
    # Recon
    'Recon-PingSweep', 'Recon-VulnerabilityScan', 'Recon-OSScan', 'Recon-PortScan',
    # Spoofing
    'ARP_Spoofing',
    # MQTT
    'MQTT-Malformed_Data', 'MQTT-DoS-Connect_Flood',
    'MQTT-DDoS-Connect_Flood', 'MQTT-DoS-Publish_Flood',
    'MQTT-DDoS-Publish_Flood',
]


def _hr(char: str = "─", width: int = 60) -> str:
    return char * width


def _size_fmt(num_bytes: int) -> str:
    """Format file size in human-readable form."""
    for unit in ("B", "KB", "MB", "GB"):
        if abs(num_bytes) < 1024:
            return f"{num_bytes:,.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:,.1f} TB"


def scan_csv_files(directory: Path) -> list[Path]:
    """Recursively find all CSV files in a directory."""
    if not directory.exists():
        return []
    return sorted(directory.rglob("*.csv"))


def verify_dataset(name: str, directory: Path, expected_features: list[str] | None = None) -> bool:
    """Verify a dataset directory and its CSV files."""
    print(f"\n{'━' * 60}")
    print(f"  {name}")
    print(f"{'━' * 60}")

    if not directory.exists():
        print(f"  [ΛΕΙΠΕΙ] Ο φάκελος δεν υπάρχει: {directory}")
        print(f"  Κατέβασε τα δεδομένα ακολουθώντας τις οδηγίες στο:")
        print(f"  scripts/download_datasets.sh")
        return False

    csv_files = scan_csv_files(directory)

    if not csv_files:
        print(f"  [ΚΕΝΟ] Ο φάκελος υπάρχει αλλά δεν περιέχει CSV αρχεία.")
        print(f"  Τοποθέτησε τα CSV αρχεία στο: {directory}/")
        return False

    # Report file inventory
    total_size = sum(f.stat().st_size for f in csv_files)
    print(f"  Βρέθηκαν {len(csv_files)} CSV αρχεία ({_size_fmt(total_size)} συνολικά)")
    print(f"  {_hr()}")

    for csv_file in csv_files:
        rel_path = str(csv_file.relative_to(directory))
        size = _size_fmt(csv_file.stat().st_size)
        print(f"  {rel_path:<50s} {size:>10s}")

    # Quick inspection of first CSV file
    print(f"\n  {_hr()}")
    print(f"  Γρήγορος έλεγχος πρώτου αρχείου: {csv_files[0].name}")
    print(f"  {_hr()}")

    try:
        # Read just a small sample
        df_sample = pd.read_csv(csv_files[0], nrows=5)
        print(f"  Στήλες ({len(df_sample.columns)}):")
        for i, col in enumerate(df_sample.columns):
            marker = ""
            if expected_features and col in expected_features:
                marker = " ✓"
            print(f"    {i+1:2d}. {col}{marker}")

        print(f"\n  Πρώτες 3 γραμμές:")
        print(df_sample.head(3).to_string(index=False, max_cols=8))

        # Check for label column
        label_col = None
        for candidate in ['label', 'Label', 'class', 'Class', 'attack', 'Attack']:
            if candidate in df_sample.columns:
                label_col = candidate
                break

        if label_col:
            # Read more rows to get label distribution
            df_labels = pd.read_csv(csv_files[0], usecols=[label_col], nrows=100_000)
            unique_labels = df_labels[label_col].unique()
            print(f"\n  Label column: '{label_col}'")
            print(f"  Μοναδικά labels (πρώτες 100K γραμμές): {len(unique_labels)}")
            for lbl in sorted(unique_labels, key=str)[:15]:
                print(f"    - {lbl}")
            if len(unique_labels) > 15:
                print(f"    ... και {len(unique_labels) - 15} ακόμα")

        # Verify against expected features if provided
        if expected_features:
            actual_cols = set(df_sample.columns)
            expected_set = set(expected_features)
            missing = expected_set - actual_cols
            extra = actual_cols - expected_set
            if missing:
                print(f"\n  [ΠΡΟΣΟΧΗ] Λείπουν αναμενόμενες στήλες: {missing}")
            if extra:
                print(f"\n  [INFO] Επιπλέον στήλες: {extra}")
            if not missing:
                print(f"\n  [OK] Όλες οι αναμενόμενες στήλες υπάρχουν!")

    except Exception as e:
        print(f"  [ΣΦΑΛΜΑ] Αδυναμία ανάγνωσης: {e}")
        return False

    return True


def main():
    print("=" * 60)
    print("  Dataset Verification Tool")
    print("  Diploma Thesis - IoT/IoMT Intrusion Detection")
    print("=" * 60)
    print(f"\n  Data directory: {DATA_DIR}")

    results = {}

    # Verify CICIoT2023
    results['CICIoT2023'] = verify_dataset(
        name="CICIoT2023 (General IoT - 33 attacks, 105 devices)",
        directory=CICIOT2023_DIR,
        expected_features=CICIOT2023_EXPECTED_FEATURES,
    )

    # Verify CICIoMT2024
    results['CICIoMT2024'] = verify_dataset(
        name="CICIoMT2024 (IoMT Medical - 18 attacks, 40 devices)",
        directory=CICIOMT2024_DIR,
        expected_features=None,  # Feature names may differ, will check manually
    )

    # Summary
    print(f"\n{'=' * 60}")
    print(f"  ΣΥΝΟΨΗ")
    print(f"{'=' * 60}")
    for name, ok in results.items():
        status = "[OK]" if ok else "[ΛΕΙΠΕΙ/ΚΕΝΟ]"
        print(f"  {status} {name}")

    all_ok = all(results.values())
    if all_ok:
        print(f"\n  Όλα τα datasets είναι έτοιμα! Μπορείς να προχωρήσεις")
        print(f"  στα exploration notebooks.")
    else:
        print(f"\n  Ορισμένα datasets λείπουν. Ακολούθησε τις οδηγίες παραπάνω.")
        print(f"\n  ΟΔΗΓΙΕΣ DOWNLOAD:")
        print(f"  1. CIC Website (επίσημο): Εκτέλεσε bash scripts/download_datasets.sh")
        print(f"  2. Kaggle (εναλλακτικό CICIoT2023):")
        print(f"     kaggle datasets download -d madhavmalhotra/unb-cic-iot-dataset \\")
        print(f"       -p data/raw/CICIoT2023 --unzip")

    print()
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
