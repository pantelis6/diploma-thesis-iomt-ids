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
    """Schematic diagram of the integration pipeline (two-dataset scope)."""
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(16, 7.5))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#FAFAFA')
    ax.set_facecolor('#FAFAFA')

    # Colour palette
    C_SRC   = '#DBEAFE'   # source datasets
    C_SRC_E = '#1D4ED8'
    C_TOOL  = '#FEF3C7'   # MIOTTA-NPT
    C_TOOL_E = '#D97706'
    C_PIPE  = '#D1FAE5'   # pipeline stages
    C_PIPE_E = '#059669'
    C_OUT   = '#FCE7F3'   # output
    C_OUT_E = '#BE185D'
    ARROW   = '#374151'

    def draw_box(x, y, w, h, text, facecolor, edgecolor, fontsize=13, bold=False, lw=2.0):
        shadow = FancyBboxPatch(
            (x + 0.06, y - 0.06), w, h,
            boxstyle='round,pad=0.02,rounding_size=0.18',
            facecolor='#00000018', edgecolor='none', zorder=1,
        )
        ax.add_patch(shadow)
        rect = FancyBboxPatch(
            (x, y), w, h,
            boxstyle='round,pad=0.02,rounding_size=0.18',
            facecolor=facecolor, edgecolor=edgecolor, linewidth=lw, zorder=2,
        )
        ax.add_patch(rect)
        weight = 'bold' if bold else 'normal'
        ax.text(
            x + w / 2, y + h / 2, text,
            ha='center', va='center', fontsize=fontsize,
            fontweight=weight, color='#111827',
            linespacing=1.35, zorder=3,
        )

    def draw_arrow(x0, y0, x1, y1, rad=0.0):
        style = f'arc3,rad={rad}' if rad else 'arc3'
        ax.annotate(
            '', xy=(x1, y1), xytext=(x0, y0),
            arrowprops=dict(
                arrowstyle='-|>', color=ARROW, lw=2.2,
                connectionstyle=style, shrinkA=4, shrinkB=4,
            ),
            zorder=1,
        )

    # ── Section labels ───────────────────────────────────────────────────────
    ax.text(1.55, 6.95, 'Raw Inputs', ha='center', fontsize=11,
            fontweight='bold', color='#6B7280', style='italic')
    ax.text(5.05, 6.95, 'Feature Extraction', ha='center', fontsize=11,
            fontweight='bold', color='#6B7280', style='italic')
    ax.text(9.55, 6.95, 'Integration Pipeline', ha='center', fontsize=11,
            fontweight='bold', color='#6B7280', style='italic')
    ax.text(13.4, 6.95, 'Output', ha='center', fontsize=11,
            fontweight='bold', color='#6B7280', style='italic')

    # ── Source datasets ──────────────────────────────────────────────────────
    draw_box(0.3, 4.5, 2.5, 1.55, 'CICIoMT2024\n(raw PCAPs)', C_SRC, C_SRC_E, fontsize=14, bold=True)
    draw_box(0.3, 2.3, 2.5, 1.55, 'IoMT-TrafficData\n(raw PCAPs)', C_SRC, C_SRC_E, fontsize=14, bold=True)

    # ── MIOTTA-NPT ───────────────────────────────────────────────────────────
    draw_box(3.8, 3.05, 2.5, 2.25,
             'MIOTTA-NPT\n\ncombined mode\n100-pkt window\n73 features',
             C_TOOL, C_TOOL_E, fontsize=13, bold=True)

    # ── Pipeline stages ───────────────────────────────────────────────────────
    stages = [
        (7.3, 5.35, 'Label\nHarmonization'),
        (7.3, 4.05, 'Data Quality\nAssurance'),
        (7.3, 2.75, 'Feature\nScaling'),
        (7.3, 1.45, 'Stratified\nSplitting'),
    ]
    for x, y, label in stages:
        draw_box(x, y, 2.5, 1.05, label, C_PIPE, C_PIPE_E, fontsize=13, bold=True)

    # ── Output ───────────────────────────────────────────────────────────────
    draw_box(11.2, 2.85, 4.4, 1.65,
             'Unified ML-Ready Dataset\n\n8.0 M records · 58 features',
             C_OUT, C_OUT_E, fontsize=14, bold=True)

    # ── Arrows: sources → MIOTTA-NPT ────────────────────────────────────────
    draw_arrow(2.8, 5.28, 3.8, 4.55, rad=0.0)
    draw_arrow(2.8, 3.08, 3.8, 3.80, rad=0.0)

    # ── Arrow: MIOTTA-NPT → first pipeline stage ────────────────────────────
    draw_arrow(6.3, 4.18, 7.3, 5.88)

    # ── Arrows: between pipeline stages ─────────────────────────────────────
    for i in range(len(stages) - 1):
        _, y_hi, _ = stages[i]
        _, y_lo, _ = stages[i + 1]
        draw_arrow(8.55, y_hi, 8.55, y_lo + 1.05)

    # ── Arrow: last stage → output ──────────────────────────────────────────
    draw_arrow(9.8, 1.98, 11.2, 3.68, rad=-0.15)

    # ── Footer note ───────────────────────────────────────────────────────────
    ax.text(
        8.0, 0.35,
        'All datasets processed with identical MIOTTA-NPT configuration  →  identical feature spaces',
        ha='center', va='center', fontsize=10.5, color='#6B7280', style='italic',
    )

    out = os.path.join(FIG_DIR, 'pipeline_overview.png')
    fig.savefig(out, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print("  [OK] pipeline_overview.png")


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
    datasets = ['CICIoMT2024', 'IoMT-TrafficData']
    original_features = [45, 101]
    miotta_features = [73, 73]
    tools = ['CIC Internal', 'Zeek']

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(datasets))
    width = 0.32

    bars1 = ax.bar(x - width/2, original_features, width, label='Original Features',
                   color='#BBDEFB', edgecolor='#1565C0', linewidth=1.2)
    bars2 = ax.bar(x + width/2, miotta_features, width, label='MIOTTA-NPT Features',
                   color='#FFF3E0', edgecolor='#E65100', linewidth=1.2)

    for bar, val, tool in zip(bars1, original_features, tools):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1.5, f'{val}\n({tool})',
                ha='center', va='bottom', fontsize=10)
    for bar, val in zip(bars2, miotta_features):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1.5, f'{val}',
                ha='center', va='bottom', fontsize=10)

    ax.set_ylabel('Number of Features', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(datasets, fontsize=12)
    ax.set_title('Feature Count: Original vs MIOTTA-NPT Processing', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_ylim(0, 120)
    ax.axhline(y=73, color='#E65100', linestyle=':', alpha=0.6, linewidth=1.5)
    ax.text(1.5, 75.5, 'Unified: 73 features', fontsize=10, fontstyle='italic', color='#E65100', ha='right')

    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'feature_count_comparison.png'))
    plt.close(fig)
    print("  [OK] feature_count_comparison.png")


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
