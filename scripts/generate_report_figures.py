"""
Generate all figures for the Master's Thesis report.
Figures are saved as PDF (vector) to report/figures/ for LaTeX inclusion.
"""

import os
import glob
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns

warnings.filterwarnings('ignore')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, 'report', 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

MIOTTA_CICIOMT_TRAIN_DIR = os.path.join(
    BASE, 'data', 'raw', 'CICIoMT2024', 'CICIoMT2024_MIOTTA',
    'CICIoMT2024', 'estadisticas_combinadas_train')
MIOTTA_CICIOMT_TEST_DIR = os.path.join(
    BASE, 'data', 'raw', 'CICIoMT2024', 'CICIoMT2024_MIOTTA',
    'CICIoMT2024', 'estadisticas_combinadas_window_size_100_test')
MIOTTA_IOMT_DIR = os.path.join(
    BASE, 'data', 'raw', 'IoMT-TrafficData', 'IoMT-TrafficData_MIOTTA',
    'IoMT-TrafficData', 'estadisticas_combinadas_iomt-trafficdata_window_size_100')
ORIG_IOMT_DIR = os.path.join(BASE, 'data', 'raw', 'IoMT-TrafficData', 'Flows')

plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})

COLORS = sns.color_palette("Set2", 12)
DATASET_COLORS = {'CICIoMT2024': '#2196F3', 'IoMT-TrafficData': '#FF9800'}


def load_miotta_ciciomt():
    """Load all MIOTTA-processed CICIoMT2024 CSVs (train + test) for consistency with Phase 1 pipeline."""
    frames = []
    for f in sorted(glob.glob(os.path.join(MIOTTA_CICIOMT_TRAIN_DIR, '*.csv'))):
        name = os.path.basename(f).replace('_train.csv', '')
        df = pd.read_csv(f, low_memory=False)
        df['attack_type'] = name
        frames.append(df)
    for f in sorted(glob.glob(os.path.join(MIOTTA_CICIOMT_TEST_DIR, '*.csv'))):
        name = os.path.basename(f).replace('estadisticas_combinadas_', '').replace('_test.csv', '')
        df = pd.read_csv(f, low_memory=False)
        df['attack_type'] = name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def load_miotta_iomt():
    """Load all MIOTTA-processed IoMT-TrafficData CSVs."""
    frames = []
    for f in sorted(glob.glob(os.path.join(MIOTTA_IOMT_DIR, '*.csv'))):
        name = os.path.basename(f).replace('estadisticas_combinadas_', '').replace('.csv', '')
        df = pd.read_csv(f, low_memory=False)
        df['attack_type'] = name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def load_original_iomt():
    """Load original IoMT-TrafficData Zeek flow CSVs."""
    frames = []
    for f in sorted(glob.glob(os.path.join(ORIG_IOMT_DIR, '*.csv'))):
        name = os.path.basename(f).replace('.csv', '')
        df = pd.read_csv(f, low_memory=False)
        df['attack_type'] = name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1: Integration Pipeline Overview Diagram (Chapter 3)
# ═══════════════════════════════════════════════════════════════════════════
def fig_pipeline_overview():
    """Schematic diagram of the integration pipeline."""
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')

    box_style = dict(boxstyle='round,pad=0.4', facecolor='#E3F2FD', edgecolor='#1565C0', linewidth=1.5)
    tool_style = dict(boxstyle='round,pad=0.4', facecolor='#FFF3E0', edgecolor='#E65100', linewidth=1.5)
    result_style = dict(boxstyle='round,pad=0.4', facecolor='#E8F5E9', edgecolor='#2E7D32', linewidth=1.5)
    phase_style = dict(boxstyle='round,pad=0.3', facecolor='#F3E5F5', edgecolor='#6A1B9A', linewidth=1.2)

    # Raw datasets (left)
    ax.text(1.5, 6.2, 'CICIoMT2024\n(PCAP)', ha='center', va='center', fontsize=10, fontweight='bold', bbox=box_style)
    ax.text(1.5, 5.0, 'IoMT-TrafficData\n(PCAP)', ha='center', va='center', fontsize=10, fontweight='bold', bbox=box_style)
    ax.text(1.5, 3.8, 'CICIoT2023\n(PCAP)', ha='center', va='center', fontsize=10, fontweight='bold', bbox=box_style)

    # MIOTTA-NPT (center-left)
    ax.text(4.5, 5.0, 'MIOTTA-NPT\n(combined mode\nwindow=100)', ha='center', va='center', fontsize=10, fontweight='bold', bbox=tool_style)

    # Arrows: datasets → MIOTTA
    arrow_kw = dict(arrowstyle='->', color='#555', lw=1.5)
    ax.annotate('', xy=(3.3, 5.0), xytext=(2.6, 6.2), arrowprops=arrow_kw)
    ax.annotate('', xy=(3.3, 5.0), xytext=(2.6, 5.0), arrowprops=arrow_kw)
    ax.annotate('', xy=(3.3, 5.0), xytext=(2.6, 3.8), arrowprops=dict(arrowstyle='->', color='#999', lw=1.2, linestyle='dashed'))
    ax.text(2.6, 3.4, '(planned)', ha='center', va='center', fontsize=8, fontstyle='italic', color='#999')

    # Standardized datasets (center)
    ax.text(7.0, 6.2, '73 features\nCICIoMT2024', ha='center', va='center', fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='#E3F2FD', edgecolor='#1565C0', linewidth=1))
    ax.text(7.0, 5.0, '73 features\nIoMT-TrafficData', ha='center', va='center', fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='#E3F2FD', edgecolor='#1565C0', linewidth=1))
    ax.text(7.0, 3.8, '73 features\nCICIoT2023', ha='center', va='center', fontsize=9, color='#999', bbox=dict(boxstyle='round,pad=0.3', facecolor='#F5F5F5', edgecolor='#999', linewidth=1, linestyle='dashed'))

    # Arrows: MIOTTA → standardized
    ax.annotate('', xy=(5.9, 5.6), xytext=(5.7, 5.2), arrowprops=arrow_kw)
    ax.annotate('', xy=(5.9, 5.0), xytext=(5.7, 5.0), arrowprops=arrow_kw)
    ax.annotate('', xy=(5.9, 4.1), xytext=(5.7, 4.8), arrowprops=dict(arrowstyle='->', color='#999', lw=1.2, linestyle='dashed'))

    # Pipeline stages (right column)
    stages = [
        ('Label\nHarmonization', 6.2),
        ('Data Quality\nAssurance', 5.0),
        ('Feature\nScaling', 3.8),
        ('Source Attribution\n& Stratified Split', 2.6),
    ]
    for label, y in stages:
        ax.text(9.5, y, label, ha='center', va='center', fontsize=9, fontweight='bold', bbox=phase_style)

    # Arrows: standardized → pipeline and between stages
    ax.annotate('', xy=(8.5, 5.6), xytext=(7.9, 5.8), arrowprops=arrow_kw)
    for i in range(len(stages) - 1):
        ax.annotate('', xy=(9.5, stages[i+1][1] + 0.4), xytext=(9.5, stages[i][1] - 0.4), arrowprops=arrow_kw)

    # Final output
    ax.text(9.5, 1.3, 'Unified ML-Ready\nDataset', ha='center', va='center', fontsize=11, fontweight='bold', bbox=result_style)
    ax.annotate('', xy=(9.5, 1.7), xytext=(9.5, 2.2), arrowprops=arrow_kw)

    # Phase labels
    ax.text(4.5, 6.7, 'Phase 1: IoMT Integration', ha='center', fontsize=10, fontweight='bold', color='#1565C0',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#1565C0', linewidth=1, alpha=0.8))
    ax.text(4.5, 3.3, 'Phase 2: + IoT (planned)', ha='center', fontsize=9, fontstyle='italic', color='#999')

    fig.savefig(os.path.join(FIG_DIR, 'pipeline_overview.png'))
    plt.close(fig)
    print("  [OK] pipeline_overview.pdf")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 2: CICIoMT2024 MIOTTA Attack Distribution (Chapter 4)
# ═══════════════════════════════════════════════════════════════════════════
def fig_ciciomt_attack_distribution(df):
    counts = df['attack_type'].value_counts().sort_values(ascending=True)
    n = len(counts)
    fig_height = max(8, n * 0.38)
    fig, ax = plt.subplots(figsize=(11, fig_height))
    colors = plt.cm.tab20(np.linspace(0, 1, n))
    bars = ax.barh(range(n), counts.values, color=colors, edgecolor='white', height=0.75)
    ax.set_yticks(range(n))
    ax.set_yticklabels(counts.index, fontsize=7.5)
    ax.set_xlabel('Number of Records')
    ax.set_title('CICIoMT2024 (MIOTTA-Processed) — Attack Type Distribution', fontsize=13, fontweight='bold')
    ax.set_xscale('log')
    for bar, val in zip(bars, counts.values):
        ax.text(val * 1.15, bar.get_y() + bar.get_height()/2, f'{val:,}', va='center', fontsize=7)
    ax.tick_params(axis='y', which='major', pad=2)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'ciciomt2024_miotta_attack_dist.png'))
    plt.close(fig)
    print("  [OK] ciciomt2024_miotta_attack_dist.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 3: IoMT-TrafficData MIOTTA Attack Distribution (Chapter 4)
# ═══════════════════════════════════════════════════════════════════════════
def fig_iomt_attack_distribution(df):
    counts = df['attack_type'].value_counts().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(range(len(counts)), counts.values, color=COLORS[:len(counts)], edgecolor='white')
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index, fontsize=9)
    ax.set_xlabel('Number of Records')
    ax.set_title('IoMT-TrafficData (MIOTTA-Processed) — Attack Type Distribution')
    ax.set_xscale('log')
    for bar, val in zip(bars, counts.values):
        ax.text(val * 1.1, bar.get_y() + bar.get_height()/2, f'{val:,}', va='center', fontsize=8)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'iomt_traffic_miotta_attack_dist.png'))
    plt.close(fig)
    print("  [OK] iomt_traffic_miotta_attack_dist.pdf")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 4: Feature Space Verification — Identical 73 Features (Chapter 4)
# ═══════════════════════════════════════════════════════════════════════════
def fig_feature_verification(df_cic, df_iomt):
    cic_cols = sorted([c for c in df_cic.columns if c != 'attack_type'])
    iomt_cols = sorted([c for c in df_iomt.columns if c != 'attack_type'])
    common = sorted(set(cic_cols) & set(iomt_cols))
    only_cic = sorted(set(cic_cols) - set(iomt_cols))
    only_iomt = sorted(set(iomt_cols) - set(cic_cols))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis('off')

    text = f"CICIoMT2024 features: {len(cic_cols)}\n"
    text += f"IoMT-TrafficData features: {len(iomt_cols)}\n"
    text += f"Common features: {len(common)}\n"
    text += f"Only in CICIoMT2024: {len(only_cic)}\n"
    text += f"Only in IoMT-TrafficData: {len(only_iomt)}\n\n"

    if len(only_cic) == 0 and len(only_iomt) == 0:
        text += "✓ VERIFIED: Both datasets share identical feature spaces\n"
        text += "  after MIOTTA-NPT processing (combined mode, window=100)."
        color = '#2E7D32'
    else:
        text += f"Differences found:\n  CIC-only: {only_cic}\n  IoMT-only: {only_iomt}"
        color = '#C62828'

    ax.text(0.5, 0.5, text, transform=ax.transAxes, ha='center', va='center',
            fontsize=12, fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#E8F5E9' if color == '#2E7D32' else '#FFEBEE',
                      edgecolor=color, linewidth=2))
    ax.set_title('Cross-Dataset Feature Space Verification', fontsize=14, fontweight='bold', pad=20)

    fig.savefig(os.path.join(FIG_DIR, 'feature_verification.png'))
    plt.close(fig)
    print("  [OK] feature_verification.pdf")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 5: Key Feature Distributions Comparison (Chapter 4)
# ═══════════════════════════════════════════════════════════════════════════
def fig_feature_distributions(df_cic, df_iomt):
    key_features = ['Tot_size', 'Header_Length', 'TTL', 'IAT',
                    'Rate', 'Min_Length', 'Max_Length', 'Avg_Length']
    available = [f for f in key_features if f in df_cic.columns and f in df_iomt.columns]

    n = len(available)
    ncols = 4
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 3.5 * nrows))
    axes = axes.flatten() if nrows > 1 else ([axes] if n == 1 else axes.flatten())

    for i, feat in enumerate(available):
        ax = axes[i]
        cic_vals = df_cic[feat].replace([np.inf, -np.inf], np.nan).dropna()
        iomt_vals = df_iomt[feat].replace([np.inf, -np.inf], np.nan).dropna()

        p99 = max(cic_vals.quantile(0.99) if len(cic_vals) > 0 else 0,
                  iomt_vals.quantile(0.99) if len(iomt_vals) > 0 else 0)
        if p99 > 0:
            cic_vals = cic_vals[cic_vals <= p99]
            iomt_vals = iomt_vals[iomt_vals <= p99]

        ax.hist(cic_vals, bins=50, alpha=0.6, color=DATASET_COLORS['CICIoMT2024'],
                label='CICIoMT2024', density=True, edgecolor='none')
        ax.hist(iomt_vals, bins=50, alpha=0.6, color=DATASET_COLORS['IoMT-TrafficData'],
                label='IoMT-TrafficData', density=True, edgecolor='none')
        ax.set_title(feat, fontsize=10, fontweight='bold')
        ax.set_ylabel('Density')
        if i == 0:
            ax.legend(fontsize=8)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle('Feature Distributions: CICIoMT2024 vs IoMT-TrafficData (MIOTTA-Processed)',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'feature_distributions_comparison.png'))
    plt.close(fig)
    print("  [OK] feature_distributions_comparison.pdf")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 6: Correlation Heatmap (Chapter 4)
# ═══════════════════════════════════════════════════════════════════════════
def fig_correlation_heatmap(df_cic, df_iomt):
    numeric_cols = [c for c in df_cic.columns if c != 'attack_type' and df_cic[c].dtype in ['float64', 'float32', 'int64']]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    for ax, df, title in [(axes[0], df_cic, 'CICIoMT2024'),
                           (axes[1], df_iomt, 'IoMT-TrafficData')]:
        sample = df[numeric_cols].sample(n=min(50000, len(df)), random_state=42)
        corr = sample.replace([np.inf, -np.inf], np.nan).corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, cmap='RdBu_r', vmin=-1, vmax=1,
                    square=True, linewidths=0, ax=ax,
                    xticklabels=False, yticklabels=False,
                    cbar_kws={'shrink': 0.6, 'label': 'Correlation'})
        ax.set_title(f'{title}\n(MIOTTA-Processed, {len(numeric_cols)} features)', fontsize=11, fontweight='bold')

    fig.suptitle('Feature Correlation Matrices', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'correlation_heatmaps.png'))
    plt.close(fig)
    print("  [OK] correlation_heatmaps.pdf")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 7: Missing Values Pattern (Chapter 4)
# ═══════════════════════════════════════════════════════════════════════════
def fig_missing_values(df_cic, df_iomt):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, df, title in [(axes[0], df_cic, 'CICIoMT2024'),
                           (axes[1], df_iomt, 'IoMT-TrafficData')]:
        numeric_cols = [c for c in df.columns if c != 'attack_type']
        missing = df[numeric_cols].isnull().sum()
        missing_pct = (missing / len(df) * 100).sort_values(ascending=False)
        missing_pct = missing_pct[missing_pct > 0]

        if len(missing_pct) == 0:
            ax.text(0.5, 0.5, 'No missing values', transform=ax.transAxes,
                    ha='center', va='center', fontsize=14, fontweight='bold', color='#2E7D32')
        else:
            bars = ax.barh(range(len(missing_pct)), missing_pct.values,
                          color='#FF7043', edgecolor='white')
            ax.set_yticks(range(len(missing_pct)))
            ax.set_yticklabels(missing_pct.index, fontsize=8)
            ax.set_xlabel('Missing Values (%)')
            for bar, val in zip(bars, missing_pct.values):
                ax.text(val + 0.5, bar.get_y() + bar.get_height()/2,
                       f'{val:.1f}%', va='center', fontsize=7)
        ax.set_title(f'{title} (MIOTTA-Processed)', fontsize=11, fontweight='bold')

    fig.suptitle('Missing Values Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'missing_values_analysis.png'))
    plt.close(fig)
    print("  [OK] missing_values_analysis.pdf")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 8: Combined Class Distribution (Chapter 4)
# ═══════════════════════════════════════════════════════════════════════════
def fig_combined_class_distribution(df_cic, df_iomt):
    cic_counts = df_cic['attack_type'].value_counts()
    iomt_counts = df_iomt['attack_type'].value_counts()

    all_types = sorted(set(list(cic_counts.index) + list(iomt_counts.index)))
    n_types = len(all_types)
    fig_height = max(8, n_types * 0.35)

    fig = plt.figure(figsize=(16, fig_height))
    gs = GridSpec(1, 2, width_ratios=[1, 2], wspace=0.35)
    ax_pie = fig.add_subplot(gs[0])
    ax_bar = fig.add_subplot(gs[1])

    # Pie chart — use legend instead of inline labels to avoid overlap
    cic_benign = cic_counts.get('Benign', 0)
    cic_attack = cic_counts.sum() - cic_benign
    iomt_benign = iomt_counts.get('IP-Based Normal Capture', 0)
    iomt_attack = iomt_counts.sum() - iomt_benign

    labels_binary = ['Benign\n(CICIoMT2024)', 'Attack\n(CICIoMT2024)',
                     'Benign\n(IoMT-TrafficData)', 'Attack\n(IoMT-TrafficData)']
    sizes = [cic_benign, cic_attack, iomt_benign, iomt_attack]
    colors_pie = ['#81D4FA', '#2196F3', '#FFE0B2', '#FF9800']
    explode = (0.03, 0.03, 0.03, 0.03)

    wedges, _, autotexts = ax_pie.pie(
        sizes, colors=colors_pie, explode=explode,
        autopct='', startangle=90,
        textprops={'fontsize': 8})

    total = sum(sizes)
    legend_labels = [f'{l}\n({s:,} — {s/total*100:.1f}%)' for l, s in zip(labels_binary, sizes)]
    ax_pie.legend(wedges, legend_labels, loc='upper left', bbox_to_anchor=(-0.25, -0.02),
                  fontsize=8, ncol=2, frameon=False, handletextpad=0.5,
                  columnspacing=1.5)
    ax_pie.set_title('Binary Distribution\n(Combined)', fontsize=11, fontweight='bold')

    # Bar chart — taller figure, smaller labels
    x = np.arange(n_types)
    width = 0.38

    cic_vals = [cic_counts.get(t, 0) for t in all_types]
    iomt_vals = [iomt_counts.get(t, 0) for t in all_types]

    ax_bar.barh(x - width/2, cic_vals, width, label='CICIoMT2024',
                color=DATASET_COLORS['CICIoMT2024'], edgecolor='white')
    ax_bar.barh(x + width/2, iomt_vals, width, label='IoMT-TrafficData',
                color=DATASET_COLORS['IoMT-TrafficData'], edgecolor='white')
    ax_bar.set_yticks(x)
    ax_bar.set_yticklabels(all_types, fontsize=7)
    ax_bar.set_xlabel('Number of Records (log scale)')
    ax_bar.set_xscale('log')
    ax_bar.legend(fontsize=9, loc='lower right')
    ax_bar.set_title('Records per Attack Type by Source', fontsize=11, fontweight='bold')
    ax_bar.tick_params(axis='y', which='major', pad=2)

    fig.suptitle('Class Distribution Overview — MIOTTA-Processed Datasets',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'combined_class_distribution.png'))
    plt.close(fig)
    print("  [OK] combined_class_distribution.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 9: Original vs MIOTTA Feature Count Comparison (Chapter 4)
# ═══════════════════════════════════════════════════════════════════════════
def fig_feature_count_comparison():
    datasets = ['CICIoMT2024', 'IoMT-TrafficData', 'CICIoT2023']
    original_features = [45, 101, 47]
    miotta_features = [73, 73, 73]
    tools = ['CIC Internal', 'Zeek', 'CIC Internal']

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(datasets))
    width = 0.3

    bars1 = ax.bar(x - width/2, original_features, width, label='Original Features',
                   color='#BBDEFB', edgecolor='#1565C0', linewidth=1.2)
    bars2 = ax.bar(x + width/2, miotta_features, width, label='MIOTTA-NPT Features',
                   color='#FFF3E0', edgecolor='#E65100', linewidth=1.2,
                   hatch='///' if datasets[2] == 'CICIoT2023' else '')

    ax.bar(x[2] + width/2, miotta_features[2], width, color='#FFF3E0',
           edgecolor='#E65100', linewidth=1.2, linestyle='dashed', alpha=0.5)

    for bar, val, tool in zip(bars1, original_features, tools):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1, f'{val}\n({tool})',
                ha='center', va='bottom', fontsize=8)
    for i, (bar, val) in enumerate(zip(bars2, miotta_features)):
        suffix = '\n(planned)' if i == 2 else ''
        ax.text(bar.get_x() + bar.get_width()/2, val + 1, f'{val}{suffix}',
                ha='center', va='bottom', fontsize=8)

    ax.set_ylabel('Number of Features')
    ax.set_xticks(x)
    ax.set_xticklabels(datasets, fontsize=10)
    ax.set_title('Feature Count: Original vs MIOTTA-NPT Processing', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(0, 120)
    ax.axhline(y=73, color='#E65100', linestyle=':', alpha=0.5, linewidth=1)
    ax.text(2.5, 75, 'Unified: 73 features', fontsize=9, fontstyle='italic', color='#E65100')

    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'feature_count_comparison.png'))
    plt.close(fig)
    print("  [OK] feature_count_comparison.pdf")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 10: Dataset Comparison Summary Table (Chapter 2)
# ═══════════════════════════════════════════════════════════════════════════
def fig_dataset_summary(df_cic, df_iomt):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')

    n_cic = len(df_cic)
    n_iomt = len(df_iomt)
    cic_attacks = df_cic['attack_type'].nunique()
    iomt_attacks = df_iomt['attack_type'].nunique()

    headers = ['', 'CICIoMT2024\n(MIOTTA)', 'IoMT-TrafficData\n(MIOTTA)', 'Combined']
    rows = [
        ['Records', f'{n_cic:,}', f'{n_iomt:,}', f'{n_cic + n_iomt:,}'],
        ['Features', '73', '73', '73'],
        ['Attack Types', str(cic_attacks), str(iomt_attacks), str(cic_attacks + iomt_attacks)],
        ['Window Size', '100', '100', '100'],
        ['MIOTTA Mode', 'Combined', 'Combined', 'Combined'],
    ]

    table = ax.table(cellText=rows, colLabels=headers, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#1565C0')
            cell.set_text_props(color='white', fontweight='bold')
        elif col == 0:
            cell.set_facecolor('#E3F2FD')
            cell.set_text_props(fontweight='bold')
        elif col == 3:
            cell.set_facecolor('#E8F5E9')
        else:
            cell.set_facecolor('white')
        cell.set_edgecolor('#BDBDBD')

    ax.set_title('MIOTTA-Processed Datasets: Summary Statistics', fontsize=13,
                 fontweight='bold', pad=20)
    fig.savefig(os.path.join(FIG_DIR, 'dataset_summary_table.png'))
    plt.close(fig)
    print("  [OK] dataset_summary_table.pdf")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 60)
    print("Generating report figures...")
    print("=" * 60)

    print("\n[1/10] Pipeline overview diagram...")
    fig_pipeline_overview()

    print("\n[2/10] Loading MIOTTA CICIoMT2024 data...")
    df_cic = load_miotta_ciciomt()
    print(f"  Loaded {len(df_cic):,} records, {len(df_cic.columns)} columns")

    print("\n[3/10] Loading MIOTTA IoMT-TrafficData...")
    df_iomt = load_miotta_iomt()
    print(f"  Loaded {len(df_iomt):,} records, {len(df_iomt.columns)} columns")

    print("\n[4/10] CICIoMT2024 attack distribution...")
    fig_ciciomt_attack_distribution(df_cic)

    print("\n[5/10] IoMT-TrafficData attack distribution...")
    fig_iomt_attack_distribution(df_iomt)

    print("\n[6/10] Feature verification...")
    fig_feature_verification(df_cic, df_iomt)

    print("\n[7/10] Feature distributions comparison...")
    fig_feature_distributions(df_cic, df_iomt)

    print("\n[8/10] Correlation heatmaps...")
    fig_correlation_heatmap(df_cic, df_iomt)

    print("\n[9/10] Missing values analysis...")
    fig_missing_values(df_cic, df_iomt)

    print("\n[10/10] Combined class distribution + feature count + summary...")
    fig_combined_class_distribution(df_cic, df_iomt)
    fig_feature_count_comparison()
    fig_dataset_summary(df_cic, df_iomt)

    print("\n" + "=" * 60)
    print(f"All figures saved to: {FIG_DIR}/")
    print("=" * 60)
