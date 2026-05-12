"""
Phase 1 Integration Pipeline — Configuration

Paths, label mappings, and pipeline parameters for the IoMT dataset unification.
"""
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

CICIOMT_TRAIN_DIR = (
    BASE_DIR / "CICIoMT2024" / "CICIoMT2024_MIOTTA" / "CICIoMT2024"
    / "estadisticas_combinadas_train"
)
CICIOMT_TEST_DIR = (
    BASE_DIR / "CICIoMT2024" / "CICIoMT2024_MIOTTA" / "CICIoMT2024"
    / "estadisticas_combinadas_window_size_100_test"
)
IOMT_DIR = (
    BASE_DIR / "IoMT-TrafficData" / "IoMT-TrafficData_MIOTTA" / "IoMT-TrafficData"
    / "estadisticas_combinadas_iomt-trafficdata_window_size_100"
)

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"

# ── Metadata columns added during loading (not part of the 73 features) ──────
META_COLS = ["attack_type", "source_file", "source_dataset"]

# ── CICIoMT2024 Label Mappings ────────────────────────────────────────────────
# Level 2 — Category (attack_group → label_category)
CICIOMT_CATEGORY_MAP = {
    "Benign":                      "Benign",
    "ARP_Spoofing":                "Spoofing",
    "MQTT-DDoS-Connect_Flood":     "DDoS",
    "MQTT-DDoS-Publish_Flood":     "DDoS",
    "MQTT-DoS-Connect_Flood":      "DoS",
    "MQTT-DoS-Publish_Flood":      "DoS",
    "MQTT-Malformed_Data":         "Injection",
    "Recon-OS_Scan":               "Reconnaissance",
    "Recon-Ping_Sweep":            "Reconnaissance",
    "Recon-Port_Scan":             "Reconnaissance",
    "Recon-VulScan":               "Reconnaissance",
    "TCP_IP-DDoS-ICMP":            "DDoS",
    "TCP_IP-DDoS-SYN":             "DDoS",
    "TCP_IP-DDoS-TCP":             "DDoS",
    "TCP_IP-DDoS-UDP":             "DDoS",
    "TCP_IP-DoS-ICMP":             "DoS",
    "TCP_IP-DoS-SYN":              "DoS",
    "TCP_IP-DoS-TCP":              "DoS",
    "TCP_IP-DoS-UDP":              "DoS",
}

# ── IoMT-TrafficData Label Mappings ───────────────────────────────────────────
# Level 2 — Category (attack_type → label_category)
IOMT_CATEGORY_MAP = {
    "IP-Based Normal Capture":     "Benign",
    "ARP Spoofing 01":             "Spoofing",
    "ARP Spoofing 02":             "Spoofing",
    "Apache Killer":               "DoS",
    "CAM Table Overflow":          "DoS",
    "MQTT Malaria":                "DoS",
    "Net Scan":                    "Reconnaissance",
    "RUDY":                        "DoS",
    "Slow Loris":                  "DoS",
    "Slow Read":                   "DoS",
}

# Level 3 — Fine-grained label normalization (original → label_fine)
IOMT_FINE_MAP = {
    "IP-Based Normal Capture":     "Benign",
    "ARP Spoofing 01":             "ARP_Spoofing",
    "ARP Spoofing 02":             "ARP_Spoofing",
    "Apache Killer":               "Apache_Killer",
    "CAM Table Overflow":          "CAM_Table_Overflow",
    "MQTT Malaria":                "MQTT_Malaria",
    "Net Scan":                    "Net_Scan",
    "RUDY":                        "RUDY",
    "Slow Loris":                  "SlowLoris",
    "Slow Read":                   "SlowRead",
}

# ── Alternative Mapping: MQTT as a distinct category ─────────────────────────
# This variant keeps all MQTT-related attacks under a dedicated "MQTT" class.
CICIOMT_CATEGORY_MAP_MQTT = {
    "Benign":                      "Benign",
    "ARP_Spoofing":                "Spoofing",
    "MQTT-DDoS-Connect_Flood":     "MQTT",
    "MQTT-DDoS-Publish_Flood":     "MQTT",
    "MQTT-DoS-Connect_Flood":      "MQTT",
    "MQTT-DoS-Publish_Flood":      "MQTT",
    "MQTT-Malformed_Data":         "MQTT",
    "Recon-OS_Scan":               "Reconnaissance",
    "Recon-Ping_Sweep":            "Reconnaissance",
    "Recon-Port_Scan":             "Reconnaissance",
    "Recon-VulScan":               "Reconnaissance",
    "TCP_IP-DDoS-ICMP":            "DDoS",
    "TCP_IP-DDoS-SYN":             "DDoS",
    "TCP_IP-DDoS-TCP":             "DDoS",
    "TCP_IP-DDoS-UDP":             "DDoS",
    "TCP_IP-DoS-ICMP":             "DoS",
    "TCP_IP-DoS-SYN":              "DoS",
    "TCP_IP-DoS-TCP":              "DoS",
    "TCP_IP-DoS-UDP":              "DoS",
}

IOMT_CATEGORY_MAP_MQTT = {
    "IP-Based Normal Capture":     "Benign",
    "ARP Spoofing 01":             "Spoofing",
    "ARP Spoofing 02":             "Spoofing",
    "Apache Killer":               "DoS",
    "CAM Table Overflow":          "DoS",
    "MQTT Malaria":                "MQTT",
    "Net Scan":                    "Reconnaissance",
    "RUDY":                        "DoS",
    "Slow Loris":                  "DoS",
    "Slow Read":                   "DoS",
}

# ── Pipeline Parameters ───────────────────────────────────────────────────────
NAN_THRESHOLD = 0.5          # drop features with NaN rate above this
NEAR_ZERO_VAR_THRESHOLD = 1e-8
SPLIT_RATIOS = (0.70, 0.15, 0.15)  # train / val / test
RANDOM_SEED = 42
