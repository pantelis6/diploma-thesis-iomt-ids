"""
Generate figures for Chapter 4 sections 4.3–4.4 (Pipeline Execution & Unified Dataset).
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE, 'report', 'figures')
PROCESSED_DIR = os.path.join(BASE, 'data', 'processed', 'phase1_iomt_unified')

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

CAT_ORDER = ['DDoS', 'DoS', 'Benign', 'Reconnaissance', 'Spoofing', 'Injection']
CAT_COLORS = {
    'DDoS': '#e74c3c', 'DoS': '#e67e22', 'Benign': '#2ecc71',
    'Reconnaissance': '#3498db', 'Spoofing': '#9b59b6', 'Injection': '#1abc9c',
}
SRC_COLORS = {'CICIoMT2024': '#2196F3', 'IoMT-TrafficData': '#FF9800'}


def load_splits():
    """Load label/source columns from all splits."""
    cols = ['label_binary', 'label_category', 'label_fine', 'source_dataset']
    splits = {}
    for name in ['train', 'val', 'test']:
        path = os.path.join(PROCESSED_DIR, f'{name}.csv')
        splits[name] = pd.read_csv(path, usecols=cols)
        print(f"  Loaded {name}: {len(splits[name]):,} rows")
    return splits


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE: Data Quality Assurance Impact Summary
# ═══════════════════════════════════════════════════════════════════════════
def fig_qa_impact():
    """Waterfall-style chart showing QA pipeline impact on row/feature counts."""
    stages = [
        'Pre-QA\n(Raw Unified)',
        'After NaN\nFeature Drop',
        'After Zero-Var\nRemoval',
        'After Duplicate\nRemoval',
        'Final\n(Post-QA)',
    ]
    rows = [8_608_196, 8_608_196, 8_608_196, 8_011_534, 8_011_534]
    features = [73, 65, 58, 58, 58]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Row counts
    colors_r = ['#BBDEFB', '#BBDEFB', '#BBDEFB', '#FFF3E0', '#C8E6C9']
    bars1 = ax1.bar(range(len(stages)), rows, color=colors_r,
                    edgecolor=['#1565C0']*3 + ['#E65100', '#2E7D32'], linewidth=1.2)
    ax1.set_xticks(range(len(stages)))
    ax1.set_xticklabels(stages, fontsize=8)
    ax1.set_ylabel('Number of Records')
    ax1.set_title('Records Through QA Pipeline', fontweight='bold')
    for bar, val in zip(bars1, rows):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 50000,
                 f'{val:,}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax1.set_ylim(0, max(rows) * 1.15)

    delta_r = rows[0] - rows[-1]
    ax1.annotate(f'-{delta_r:,}\n({100*delta_r/rows[0]:.1f}%)',
                 xy=(3, rows[3]), xytext=(2.5, rows[0]*0.85),
                 arrowprops=dict(arrowstyle='->', color='#C62828', lw=1.5),
                 fontsize=9, color='#C62828', fontweight='bold', ha='center')

    # Feature counts
    colors_f = ['#BBDEFB', '#FFF3E0', '#FFF3E0', '#FFF3E0', '#C8E6C9']
    bars2 = ax2.bar(range(len(stages)), features, color=colors_f,
                    edgecolor=['#1565C0'] + ['#E65100']*3 + ['#2E7D32'], linewidth=1.2)
    ax2.set_xticks(range(len(stages)))
    ax2.set_xticklabels(stages, fontsize=8)
    ax2.set_ylabel('Number of Features')
    ax2.set_title('Features Through QA Pipeline', fontweight='bold')
    for bar, val in zip(bars2, features):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                 str(val), ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax2.set_ylim(0, max(features) * 1.25)

    ax2.annotate(f'-8 NaN\n-7 zero-var',
                 xy=(2, features[2]+1), xytext=(1, features[0]*1.1),
                 arrowprops=dict(arrowstyle='->', color='#C62828', lw=1.5),
                 fontsize=9, color='#C62828', fontweight='bold', ha='center')

    fig.suptitle('Data Quality Assurance Pipeline Impact',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'qa_impact_summary.png'))
    plt.close(fig)
    print("  [OK] qa_impact_summary.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE: Unified Dataset — Category Distribution (post-QA)
# ═══════════════════════════════════════════════════════════════════════════
def fig_unified_category_distribution(splits):
    """Stacked horizontal bars by source for each category."""
    all_data = pd.concat(splits.values(), ignore_index=True)

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5))

    # Left: category distribution by source
    ax = axes[0]
    cat_src = all_data.groupby(['label_category', 'source_dataset']).size().unstack(fill_value=0)
    cat_src = cat_src.reindex([c for c in CAT_ORDER if c in cat_src.index])

    y = np.arange(len(cat_src))
    cic_vals = cat_src.get('CICIoMT2024', pd.Series(0, index=cat_src.index)).values
    iomt_vals = cat_src.get('IoMT-TrafficData', pd.Series(0, index=cat_src.index)).values

    ax.barh(y, cic_vals, 0.6, label='CICIoMT2024', color=SRC_COLORS['CICIoMT2024'], edgecolor='white')
    ax.barh(y, iomt_vals, 0.6, left=cic_vals, label='IoMT-TrafficData',
            color=SRC_COLORS['IoMT-TrafficData'], edgecolor='white')
    ax.set_yticks(y)
    ax.set_yticklabels(cat_src.index, fontsize=10)
    ax.set_xlabel('Number of Records')
    ax.set_xscale('log')
    ax.set_title('Category Distribution by Source', fontweight='bold')
    ax.legend(fontsize=9, loc='lower right')

    for i, (c, io) in enumerate(zip(cic_vals, iomt_vals)):
        total = c + io
        ax.text(total * 1.15, i, f'{total:,}', va='center', fontsize=8)

    # Right: fine-grained distribution (top 15)
    ax2 = axes[1]
    fine_counts = all_data['label_fine'].value_counts().head(15)
    fine_cats = [all_data[all_data['label_fine'] == l]['label_category'].iloc[0]
                 for l in fine_counts.index]
    colors = [CAT_COLORS.get(c, '#95a5a6') for c in fine_cats]

    bars = ax2.barh(range(len(fine_counts)), fine_counts.values[::-1],
                    color=colors[::-1], edgecolor='white')
    ax2.set_yticks(range(len(fine_counts)))
    ax2.set_yticklabels(fine_counts.index[::-1], fontsize=8)
    ax2.set_xlabel('Number of Records')
    ax2.set_xscale('log')
    ax2.set_title('Top 15 Fine-Grained Attack Types', fontweight='bold')

    handles = [mpatches.Patch(color=CAT_COLORS[c], label=c) for c in CAT_ORDER if c in set(fine_cats)]
    ax2.legend(handles=handles, fontsize=7, loc='lower right')

    fig.suptitle('Unified Dataset (Phase 1) — Label Distribution After QA',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'unified_category_distribution.png'))
    plt.close(fig)
    print("  [OK] unified_category_distribution.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE: Stratified Split Verification
# ═══════════════════════════════════════════════════════════════════════════
def fig_split_verification(splits):
    """Show that category and source proportions are preserved across splits."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Left: category proportions per split
    ax = axes[0]
    split_names = ['train', 'val', 'test']
    x = np.arange(len(CAT_ORDER))
    width = 0.25

    for i, name in enumerate(split_names):
        split_df = splits[name]
        cat_counts = split_df['label_category'].value_counts()
        proportions = [(cat_counts.get(c, 0) / len(split_df) * 100) for c in CAT_ORDER]
        bars = ax.bar(x + i * width, proportions, width, label=f'{name} ({len(split_df):,})',
                      alpha=0.85)

    ax.set_xticks(x + width)
    ax.set_xticklabels(CAT_ORDER, fontsize=9, rotation=15)
    ax.set_ylabel('Proportion (%)')
    ax.set_title('Category Proportions per Split', fontweight='bold')
    ax.legend(fontsize=8)
    ax.set_yscale('log')
    ax.set_ylim(0.005, 100)

    # Right: source proportions per split
    ax2 = axes[1]
    sources = ['CICIoMT2024', 'IoMT-TrafficData']
    bar_data = []
    for name in split_names:
        split_df = splits[name]
        src_pct = [(split_df['source_dataset'] == s).sum() / len(split_df) * 100 for s in sources]
        bar_data.append(src_pct)

    x2 = np.arange(len(split_names))
    width2 = 0.3
    for j, src in enumerate(sources):
        vals = [bd[j] for bd in bar_data]
        ax2.bar(x2 + j * width2, vals, width2, label=src,
                color=SRC_COLORS[src], edgecolor='white', alpha=0.85)
        for k, v in enumerate(vals):
            ax2.text(x2[k] + j * width2, v + 0.5, f'{v:.2f}%', ha='center', fontsize=8)

    ax2.set_xticks(x2 + width2 / 2)
    ax2.set_xticklabels([f'{n}\n({len(splits[n]):,})' for n in split_names], fontsize=9)
    ax2.set_ylabel('Proportion (%)')
    ax2.set_title('Source Proportions per Split', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.set_ylim(0, 105)

    fig.suptitle('Stratified Splitting Verification',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, 'split_verification.png'))
    plt.close(fig)
    print("  [OK] split_verification.png")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE: Unified Dataset Summary Table
# ═══════════════════════════════════════════════════════════════════════════
def fig_unified_summary_table(splits):
    """Table summarizing the final unified dataset characteristics."""
    all_data = pd.concat(splits.values(), ignore_index=True)
    total = len(all_data)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')

    headers = ['Property', 'Value']
    rows = [
        ['Total Records', f'{total:,}'],
        ['Features', '58'],
        ['Label Levels', '3 (binary, category, fine-grained)'],
        ['Categories', f'{all_data["label_category"].nunique()} ({", ".join(CAT_ORDER)})'],
        ['Fine-Grained Classes', str(all_data['label_fine'].nunique())],
        ['Source Datasets', '2 (CICIoMT2024, IoMT-TrafficData)'],
        ['Train / Val / Test', f'{len(splits["train"]):,} / {len(splits["val"]):,} / {len(splits["test"]):,}'],
        ['Split Ratio', '70% / 15% / 15%'],
        ['Scaling', 'StandardScaler (z-score, fitted on train)'],
        ['Provenance', 'source_dataset column preserved'],
    ]

    table = ax.table(cellText=rows, colLabels=headers, loc='center', cellLoc='left')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.3, 1.6)

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#1565C0')
            cell.set_text_props(color='white', fontweight='bold')
            cell.set_text_props(ha='center', color='white', fontweight='bold')
        elif col == 0:
            cell.set_facecolor('#E3F2FD')
            cell.set_text_props(fontweight='bold')
        else:
            cell.set_facecolor('white')
        cell.set_edgecolor('#BDBDBD')

    ax.set_title('Phase 1 Unified IoMT Dataset — Summary',
                 fontsize=13, fontweight='bold', pad=20)
    fig.savefig(os.path.join(FIG_DIR, 'unified_dataset_summary.png'))
    plt.close(fig)
    print("  [OK] unified_dataset_summary.png")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 60)
    print("Generating Chapter 4.3–4.4 figures...")
    print("=" * 60)

    print("\n[1/4] QA Impact Summary...")
    fig_qa_impact()

    print("\n[2/4] Loading split data...")
    splits = load_splits()

    print("\n[3/4] Unified category distribution...")
    fig_unified_category_distribution(splits)

    print("\n[4/4] Split verification...")
    fig_split_verification(splits)

    print("\n[5/5] Unified dataset summary table...")
    fig_unified_summary_table(splits)

    print("\n" + "=" * 60)
    print(f"All Ch.4 figures saved to: {FIG_DIR}/")
    print("=" * 60)
