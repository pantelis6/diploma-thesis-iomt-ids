"""
Create a beautiful, professional PowerPoint presentation about the three datasets
and the integration pipeline for the diploma thesis.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

# ── Color Palette (Modern / Professional) ──
DARK_BG = RGBColor(0x1E, 0x29, 0x3B)       # Dark navy
MEDIUM_BG = RGBColor(0x27, 0x35, 0x4A)      # Slightly lighter navy
ACCENT_BLUE = RGBColor(0x38, 0xBD, 0xF8)    # Bright cyan/blue
ACCENT_GREEN = RGBColor(0x4A, 0xDE, 0x80)   # Bright green
ACCENT_ORANGE = RGBColor(0xFB, 0x92, 0x3C)  # Bright orange
ACCENT_PURPLE = RGBColor(0xA7, 0x8B, 0xFA)  # Soft purple
ACCENT_RED = RGBColor(0xF8, 0x71, 0x71)     # Soft red
ACCENT_TEAL = RGBColor(0x2D, 0xD4, 0xBF)    # Teal
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xCB, 0xD5, 0xE1)
MEDIUM_GRAY = RGBColor(0x94, 0xA3, 0xB8)
VERY_LIGHT = RGBColor(0xF1, 0xF5, 0xF9)


def set_slide_bg(slide, color):
    """Set solid background color for a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_shape(slide, left, top, width, height, fill_color, corner_radius=None):
    """Add a rounded rectangle shape."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    if corner_radius is not None:
        shape.adjustments[0] = corner_radius
    return shape


def add_text_box(slide, left, top, width, height, text, font_size=14,
                 font_color=WHITE, bold=False, alignment=PP_ALIGN.LEFT,
                 font_name='Calibri'):
    """Add a text box with formatted text."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = font_color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def add_paragraph(text_frame, text, font_size=14, font_color=WHITE,
                  bold=False, space_before=Pt(4), space_after=Pt(2),
                  alignment=PP_ALIGN.LEFT, font_name='Calibri', level=0):
    """Add a paragraph to an existing text frame."""
    p = text_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = font_color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    p.space_before = space_before
    p.space_after = space_after
    p.level = level
    return p


def add_bullet_text(text_frame, text, font_size=13, font_color=LIGHT_GRAY,
                    bold=False, indent_level=0, bullet_char='•'):
    """Add a bullet point to text frame."""
    p = text_frame.add_paragraph()
    p.text = f"{bullet_char} {text}"
    p.font.size = Pt(font_size)
    p.font.color.rgb = font_color
    p.font.bold = bold
    p.font.name = 'Calibri'
    p.space_before = Pt(3)
    p.space_after = Pt(2)
    p.level = indent_level
    return p


def add_accent_line(slide, left, top, width, color=ACCENT_BLUE, height=Pt(3)):
    """Add a colored accent line."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def create_info_card(slide, left, top, width, height, title, items, 
                     accent_color=ACCENT_BLUE, bg_color=MEDIUM_BG):
    """Create an info card with title and bullet items."""
    card = add_shape(slide, left, top, width, height, bg_color, corner_radius=0.05)
    
    # Accent bar at top of card
    add_accent_line(slide, left + Inches(0.1), top + Inches(0.08), 
                    width - Inches(0.2), accent_color, Pt(3))
    
    # Title
    txBox = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2),
                                      width - Inches(0.4), Inches(0.4))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.color.rgb = accent_color
    p.font.bold = True
    p.font.name = 'Calibri'
    
    # Items
    for item in items:
        add_bullet_text(tf, item, font_size=11, font_color=LIGHT_GRAY)
    
    return card


def create_stat_box(slide, left, top, width, height, value, label, 
                    accent_color=ACCENT_BLUE):
    """Create a stat highlight box."""
    card = add_shape(slide, left, top, width, height, MEDIUM_BG, corner_radius=0.06)
    
    # Value
    txBox = slide.shapes.add_textbox(left, top + Inches(0.15), width, Inches(0.5))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = value
    p.font.size = Pt(24)
    p.font.color.rgb = accent_color
    p.font.bold = True
    p.font.name = 'Calibri'
    p.alignment = PP_ALIGN.CENTER
    
    # Label
    p2 = tf.add_paragraph()
    p2.text = label
    p2.font.size = Pt(10)
    p2.font.color.rgb = MEDIUM_GRAY
    p2.font.bold = False
    p2.font.name = 'Calibri'
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(4)
    
    return card


# ══════════════════════════════════════════════════════════════════════
# CREATE PRESENTATION
# ══════════════════════════════════════════════════════════════════════

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN = Inches(0.6)
CONTENT_W = SLIDE_W - 2 * MARGIN


# ══════════════════════════════════════════════════════════════════════
# SLIDE 1: TITLE
# ══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
set_slide_bg(slide, DARK_BG)

# Decorative gradient bar at top
add_shape(slide, 0, 0, SLIDE_W, Inches(0.08), ACCENT_BLUE)

# Title
add_text_box(slide, MARGIN, Inches(1.8), CONTENT_W, Inches(1.2),
             "Three Datasets & Integration Pipeline",
             font_size=40, font_color=WHITE, bold=True, 
             alignment=PP_ALIGN.CENTER)

# Subtitle
add_text_box(slide, MARGIN, Inches(3.0), CONTENT_W, Inches(0.6),
             "IoT / IoMT Network Intrusion Detection — Diploma Thesis",
             font_size=20, font_color=ACCENT_BLUE, bold=False,
             alignment=PP_ALIGN.CENTER)

# Accent line
add_accent_line(slide, Inches(4.5), Inches(3.8), Inches(4.333), ACCENT_BLUE, Pt(2))

# Description
add_text_box(slide, Inches(2), Inches(4.2), Inches(9.333), Inches(1.0),
             "A concise overview of CICIoT2023, CICIoMT2024, and IoMT-TrafficData\n"
             "with a step-by-step unification pipeline",
             font_size=16, font_color=MEDIUM_GRAY, bold=False,
             alignment=PP_ALIGN.CENTER)

# Author / Date
add_text_box(slide, MARGIN, Inches(6.2), CONTENT_W, Inches(0.5),
             "February 2026",
             font_size=14, font_color=MEDIUM_GRAY, bold=False,
             alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 2: DATASET 1 — CICIoT2023
# ══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide, DARK_BG)
add_shape(slide, 0, 0, SLIDE_W, Inches(0.08), ACCENT_BLUE)

# Section tag
add_text_box(slide, MARGIN, Inches(0.3), Inches(2), Inches(0.35),
             "DATASET 1", font_size=12, font_color=ACCENT_BLUE, bold=True)

# Title
add_text_box(slide, MARGIN, Inches(0.6), Inches(10), Inches(0.6),
             "CICIoT2023 — General IoT Attacks", 
             font_size=30, font_color=WHITE, bold=True)

# Subtitle
add_text_box(slide, MARGIN, Inches(1.1), Inches(10), Inches(0.4),
             "Neto et al. (2023)  •  Canadian Institute for Cybersecurity, UNB  •  Sensors, 23(13)",
             font_size=13, font_color=MEDIUM_GRAY, bold=False)

add_accent_line(slide, MARGIN, Inches(1.55), Inches(8), ACCENT_BLUE, Pt(2))

# Stat boxes row
stat_y = Inches(1.8)
stat_h = Inches(0.95)
stat_w = Inches(2.2)
gap = Inches(0.3)
start_x = MARGIN

create_stat_box(slide, start_x, stat_y, stat_w, stat_h,
                "~44.8M", "Total Records", ACCENT_BLUE)
create_stat_box(slide, start_x + stat_w + gap, stat_y, stat_w, stat_h,
                "39 + Label", "Features (CSV)", ACCENT_GREEN)
create_stat_box(slide, start_x + 2*(stat_w + gap), stat_y, stat_w, stat_h,
                "33 Attacks", "in 7 Categories", ACCENT_ORANGE)
create_stat_box(slide, start_x + 3*(stat_w + gap), stat_y, stat_w, stat_h,
                "105 Devices", "IoT (Smart Home)", ACCENT_PURPLE)
create_stat_box(slide, start_x + 4*(stat_w + gap), stat_y, stat_w, stat_h,
                "63 CSVs", "~9.1 GB Total", ACCENT_TEAL)

# Info cards
card_y = Inches(3.0)
card_h = Inches(4.1)
card_w = Inches(3.85)

create_info_card(slide, MARGIN, card_y, card_w, card_h,
                 "Attack Categories (7)",
                 [
                     "DDoS (12 types) — ~34.0M rows",
                     "DoS (4 types) — ~8.1M rows",
                     "Mirai (3 types) — ~2.6M rows",
                     "Benign — ~1.1M rows",
                     "Spoofing (2 types) — ~0.5M rows",
                     "Recon (5 types) — ~0.35M rows",
                     "Web-based (6 types) — ~25K rows",
                     "Brute Force (1 type) — ~13K rows",
                 ],
                 accent_color=ACCENT_ORANGE)

create_info_card(slide, MARGIN + card_w + Inches(0.25), card_y, card_w, card_h,
                 "Feature Extraction",
                 [
                     "Source: PCAP → CSV via DPKT",
                     "Window-based aggregation:",
                     "  10 packets → low-traffic attacks",
                     "  100 packets → high-volume attacks",
                     "Values = mean of packets in window",
                     "Realistic smart-home topology",
                     "7 Raspberry Pi attackers",
                     "Full-duplex capture (Gigamon tap)",
                 ],
                 accent_color=ACCENT_BLUE)

create_info_card(slide, MARGIN + 2*(card_w + Inches(0.25)), card_y, card_w, card_h,
                 "Key Characteristics",
                 [
                     "Largest public IoT IDS dataset",
                     "General IoT (not healthcare-specific)",
                     "Heavily imbalanced (DDoS dominant)",
                     "Same CIC lab as CICIoMT2024",
                     "Same DPKT extraction pipeline",
                     "Shared 39 features → easy integration",
                     "Supports 3-level classification:",
                     "  Binary / 8-class / 34-class",
                 ],
                 accent_color=ACCENT_GREEN)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 3: DATASET 2 — CICIoMT2024
# ══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide, DARK_BG)
add_shape(slide, 0, 0, SLIDE_W, Inches(0.08), ACCENT_GREEN)

add_text_box(slide, MARGIN, Inches(0.3), Inches(2), Inches(0.35),
             "DATASET 2", font_size=12, font_color=ACCENT_GREEN, bold=True)

add_text_box(slide, MARGIN, Inches(0.6), Inches(10), Inches(0.6),
             "CICIoMT2024 — IoMT Healthcare Attacks",
             font_size=30, font_color=WHITE, bold=True)

add_text_box(slide, MARGIN, Inches(1.1), Inches(10), Inches(0.4),
             "Dadkhah et al. (2024)  •  CIC, University of New Brunswick  •  Internet of Things, Elsevier",
             font_size=13, font_color=MEDIUM_GRAY, bold=False)

add_accent_line(slide, MARGIN, Inches(1.55), Inches(8), ACCENT_GREEN, Pt(2))

# Stat boxes
create_stat_box(slide, start_x, stat_y, stat_w, stat_h,
                "~1.2M", "Total Records", ACCENT_BLUE)
create_stat_box(slide, start_x + stat_w + gap, stat_y, stat_w, stat_h,
                "45 Features", "(39 shared + 6 extra)", ACCENT_GREEN)
create_stat_box(slide, start_x + 2*(stat_w + gap), stat_y, stat_w, stat_h,
                "18 Attacks", "in 5 Categories", ACCENT_ORANGE)
create_stat_box(slide, start_x + 3*(stat_w + gap), stat_y, stat_w, stat_h,
                "40 Devices", "25 real + 15 sim", ACCENT_PURPLE)
create_stat_box(slide, start_x + 4*(stat_w + gap), stat_y, stat_w, stat_h,
                "WiFi + MQTT", "Protocols", ACCENT_TEAL)

# Info cards
create_info_card(slide, MARGIN, card_y, card_w, card_h,
                 "Attack Categories (5)",
                 [
                     "DDoS TCP/IP (4 types)",
                     "DoS TCP/IP (4 types)",
                     "MQTT Attacks (5 types):",
                     "  DDoS/DoS Connect & Publish Flood",
                     "  Malformed Data",
                     "Reconnaissance (4 types)",
                     "Spoofing (ARP — 1 type)",
                     "Healthcare device-focused",
                 ],
                 accent_color=ACCENT_ORANGE)

create_info_card(slide, MARGIN + card_w + Inches(0.25), card_y, card_w, card_h,
                 "Feature Extraction",
                 [
                     "Same pipeline as CICIoT2023!",
                     "PCAP → CSV via TCPDUMP + DPKT",
                     "Window-based aggregation:",
                     "  10 pkts → Recon, Spoofing, Benign",
                     "  100 pkts → DDoS, DoS, MQTT floods",
                     "Duration col = actually TTL",
                     "6 extra features vs CICIoT2023:",
                     "  Srate, Drate, Magnitue, etc.",
                 ],
                 accent_color=ACCENT_BLUE)

create_info_card(slide, MARGIN + 2*(card_w + Inches(0.25)), card_y, card_w, card_h,
                 "Key Differences from CICIoT2023",
                 [
                     "IoMT-focused (medical devices)",
                     "5 unique MQTT attack types",
                     "Device profiling data available",
                     "Fewer general attack categories",
                     "No Web-based, Brute Force, Mirai",
                     "Same CIC lab & extraction pipeline",
                     "39 shared features → direct merge",
                     "Pre-split: train/test CSVs provided",
                 ],
                 accent_color=ACCENT_GREEN)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 4: DATASET 3 — IoMT-TrafficData
# ══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide, DARK_BG)
add_shape(slide, 0, 0, SLIDE_W, Inches(0.08), ACCENT_ORANGE)

add_text_box(slide, MARGIN, Inches(0.3), Inches(2), Inches(0.35),
             "DATASET 3", font_size=12, font_color=ACCENT_ORANGE, bold=True)

add_text_box(slide, MARGIN, Inches(0.6), Inches(10), Inches(0.6),
             "IoMT-TrafficData — ML-Based IoMT IDS",
             font_size=30, font_color=WHITE, bold=True)

add_text_box(slide, MARGIN, Inches(1.1), Inches(10), Inches(0.4),
             "Areia et al. (2024)  •  IEEE Access, Vol. 12  •  Zenodo DOI 10.5281/zenodo.8116337",
             font_size=13, font_color=MEDIUM_GRAY, bold=False)

add_accent_line(slide, MARGIN, Inches(1.55), Inches(8), ACCENT_ORANGE, Pt(2))

# Stat boxes
create_stat_box(slide, start_x, stat_y, stat_w, stat_h,
                "~969K", "Total Rows (Flows)", ACCENT_BLUE)
create_stat_box(slide, start_x + stat_w + gap, stat_y, stat_w, stat_h,
                "101 Features", "Zeek Flow-style", ACCENT_GREEN)
create_stat_box(slide, start_x + 2*(stat_w + gap), stat_y, stat_w, stat_h,
                "8 Attacks", "+ Benign", ACCENT_ORANGE)
create_stat_box(slide, start_x + 3*(stat_w + gap), stat_y, stat_w, stat_h,
                "10+ Devices", "IoMT Medical", ACCENT_PURPLE)
create_stat_box(slide, start_x + 4*(stat_w + gap), stat_y, stat_w, stat_h,
                "CoAP/MQTT/HTTP", "Protocols", ACCENT_TEAL)

# Info cards
create_info_card(slide, MARGIN, card_y, card_w, card_h,
                 "Attack Types (8)",
                 [
                     "ARP Spoofing",
                     "Apache Killer (DoS)",
                     "CAM Table Overflow (MAC flood)",
                     "MQTT Malaria (MQTT flood)",
                     "Reconnaissance (Netscan)",
                     "R-U-Dead-Yet / RUDY (slow POST)",
                     "Slow Loris (slow HTTP)",
                     "Slow Read (slow read DoS)",
                 ],
                 accent_color=ACCENT_ORANGE)

create_info_card(slide, MARGIN + card_w + Inches(0.25), card_y, card_w, card_h,
                 "Feature Extraction",
                 [
                     "Zeek (Bro) flow/conn-style features",
                     "NOT DPKT window-based!",
                     "Packet-level + Flow-level CSVs",
                     "Flow features: id.orig_h, duration,",
                     "  fwd_*, bwd_*, flow_* statistics",
                     "Flow-based ~5% better than packet",
                     "Different schema from CIC datasets",
                     "9 CSV files (per attack type)",
                 ],
                 accent_color=ACCENT_BLUE)

create_info_card(slide, MARGIN + 2*(card_w + Inches(0.25)), card_y, card_w, card_h,
                 "Integration Challenges",
                 [
                     "⚠ Different feature extraction tool",
                     "⚠ 101 features vs 39/45 (CIC)",
                     "⚠ Zeek schema ≠ DPKT schema",
                     "Options for integration:",
                     "  1. Common semantic features",
                     "  2. Feature mapping/alignment",
                     "  3. Separate models per schema",
                     "Second IoMT dataset → key for thesis",
                 ],
                 accent_color=ACCENT_RED)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 5: DATASETS COMPARISON SUMMARY
# ══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide, DARK_BG)
add_shape(slide, 0, 0, SLIDE_W, Inches(0.08), ACCENT_PURPLE)

add_text_box(slide, MARGIN, Inches(0.3), Inches(2), Inches(0.35),
             "COMPARISON", font_size=12, font_color=ACCENT_PURPLE, bold=True)

add_text_box(slide, MARGIN, Inches(0.6), Inches(10), Inches(0.6),
             "Datasets at a Glance",
             font_size=30, font_color=WHITE, bold=True)

add_accent_line(slide, MARGIN, Inches(1.2), Inches(6), ACCENT_PURPLE, Pt(2))

# Create comparison table
table_left = MARGIN
table_top = Inches(1.6)
table_width = Inches(12.133)
rows = 9
cols = 4
table_shape = slide.shapes.add_table(rows, cols, table_left, table_top, table_width, Inches(5.2))
table = table_shape.table

# Column widths
table.columns[0].width = Inches(2.5)
table.columns[1].width = Inches(3.211)
table.columns[2].width = Inches(3.211)
table.columns[3].width = Inches(3.211)

# Header row
headers = ["", "CICIoT2023", "CICIoMT2024", "IoMT-TrafficData"]
for i, h in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = h
    for paragraph in cell.text_frame.paragraphs:
        paragraph.font.size = Pt(13)
        paragraph.font.color.rgb = WHITE
        paragraph.font.bold = True
        paragraph.font.name = 'Calibri'
        paragraph.alignment = PP_ALIGN.CENTER
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0x33, 0x41, 0x55)

# Data
data = [
    ["Domain", "General IoT", "IoMT (Healthcare)", "IoMT (Healthcare)"],
    ["Source / Lab", "CIC, UNB", "CIC, UNB", "Areia et al. (IEEE)"],
    ["Total Records", "~44.8 Million", "~1.2 Million", "~969 Thousand"],
    ["Features", "39 (DPKT windows)", "45 (DPKT windows)", "101 (Zeek flows)"],
    ["Attack Types", "33 in 7 categories", "18 in 5 categories", "8 + Benign"],
    ["Devices", "105 IoT", "40 IoMT", "10+ IoMT"],
    ["Key Protocols", "TCP/IP, Smart Home", "WiFi, MQTT", "CoAP, MQTT, HTTP"],
    ["Feature Compatibility", "39 common with IoMT2024", "39 common with IoT2023", "Different schema (Zeek)"],
]

for r, row_data in enumerate(data):
    for c, val in enumerate(row_data):
        cell = table.cell(r + 1, c)
        cell.text = val
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(11)
            paragraph.font.name = 'Calibri'
            if c == 0:
                paragraph.font.color.rgb = ACCENT_BLUE
                paragraph.font.bold = True
                paragraph.alignment = PP_ALIGN.LEFT
            else:
                paragraph.font.color.rgb = LIGHT_GRAY
                paragraph.font.bold = False
                paragraph.alignment = PP_ALIGN.CENTER
        if r % 2 == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        else:
            cell.fill.solid()
            cell.fill.fore_color.rgb = MEDIUM_BG


# ══════════════════════════════════════════════════════════════════════
# SLIDE 6: PIPELINE OVERVIEW
# ══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide, DARK_BG)
add_shape(slide, 0, 0, SLIDE_W, Inches(0.08), ACCENT_TEAL)

add_text_box(slide, MARGIN, Inches(0.3), Inches(3), Inches(0.35),
             "INTEGRATION PIPELINE", font_size=12, font_color=ACCENT_TEAL, bold=True)

add_text_box(slide, MARGIN, Inches(0.6), Inches(10), Inches(0.6),
             "Two-Phase Unification Strategy",
             font_size=30, font_color=WHITE, bold=True)

add_text_box(slide, MARGIN, Inches(1.1), Inches(12), Inches(0.4),
             "Hybrid approach: Semantic integration for IoMT datasets (Phase 1) + Pipeline integration with general IoT (Phase 2)",
             font_size=14, font_color=MEDIUM_GRAY, bold=False)

add_accent_line(slide, MARGIN, Inches(1.55), Inches(8), ACCENT_TEAL, Pt(2))

# Phase 1 Box
phase1_x = MARGIN
phase1_y = Inches(1.9)
phase1_w = Inches(5.8)
phase1_h = Inches(5.0)

add_shape(slide, phase1_x, phase1_y, phase1_w, phase1_h, MEDIUM_BG, corner_radius=0.04)
add_accent_line(slide, phase1_x + Inches(0.1), phase1_y + Inches(0.08), 
                phase1_w - Inches(0.2), ACCENT_GREEN, Pt(4))

txBox = slide.shapes.add_textbox(phase1_x + Inches(0.25), phase1_y + Inches(0.25),
                                  phase1_w - Inches(0.5), Inches(0.5))
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "PHASE 1 — IoMT Unification"
p.font.size = Pt(18)
p.font.color.rgb = ACCENT_GREEN
p.font.bold = True
p.font.name = 'Calibri'

add_paragraph(tf, "CICIoMT2024 + IoMT-TrafficData", font_size=13,
              font_color=LIGHT_GRAY, bold=True, space_before=Pt(10))

add_paragraph(tf, "→ Semantic (Feature-level) Integration", font_size=11,
              font_color=ACCENT_ORANGE, bold=True, space_before=Pt(2))

add_bullet_text(tf, "Both IoMT/healthcare-specific datasets", font_size=12)
add_bullet_text(tf, "Different schemas (DPKT vs Zeek)", font_size=12)
add_bullet_text(tf, "Semantic feature mapping table:", font_size=12)
add_bullet_text(tf, "  flow_duration, pkt counts, byte counts,", font_size=11,
                font_color=MEDIUM_GRAY)
add_bullet_text(tf, "  protocol flags, inter-arrival times", font_size=11,
                font_color=MEDIUM_GRAY)
add_bullet_text(tf, "Unit/scale conversion + validation", font_size=12)
add_bullet_text(tf, "Create common IoMT feature schema", font_size=12)
add_bullet_text(tf, "Harmonize labels to shared taxonomy", font_size=12)
add_bullet_text(tf, "Add source attribute per record", font_size=12)
add_bullet_text(tf, "Result: Unified IoMT Dataset", font_size=12, 
                font_color=ACCENT_GREEN, bold=True)

# Phase 2 Box
phase2_x = MARGIN + phase1_w + Inches(0.3)
phase2_y = Inches(1.9)
phase2_w = Inches(5.8)
phase2_h = Inches(5.0)

add_shape(slide, phase2_x, phase2_y, phase2_w, phase2_h, MEDIUM_BG, corner_radius=0.04)
add_accent_line(slide, phase2_x + Inches(0.1), phase2_y + Inches(0.08),
                phase2_w - Inches(0.2), ACCENT_BLUE, Pt(4))

txBox2 = slide.shapes.add_textbox(phase2_x + Inches(0.25), phase2_y + Inches(0.25),
                                   phase2_w - Inches(0.5), Inches(0.5))
tf2 = txBox2.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]
p.text = "PHASE 2 — Full Integration"
p.font.size = Pt(18)
p.font.color.rgb = ACCENT_BLUE
p.font.bold = True
p.font.name = 'Calibri'

add_paragraph(tf2, "Unified IoMT + CICIoT2023", font_size=13,
              font_color=LIGHT_GRAY, bold=True, space_before=Pt(10))

add_paragraph(tf2, "→ Pipeline-oriented (Schema-level) Integration", font_size=11,
              font_color=ACCENT_ORANGE, bold=True, space_before=Pt(2))

add_bullet_text(tf2, "CICIoMT2024 shares 39 features with CICIoT2023", font_size=12)
add_bullet_text(tf2, "Same DPKT pipeline → near-isomorphic schema", font_size=12)
add_bullet_text(tf2, "Rename: Duration → Time_To_Live", font_size=12)
add_bullet_text(tf2, "Type normalization (numeric coercion, inf/NaN)", font_size=12)
add_bullet_text(tf2, "Feature scaling (standardize distributions)", font_size=12)
add_bullet_text(tf2, "3-level label harmonization:", font_size=12)
add_bullet_text(tf2, "  Binary / Category / Fine-grained (53 labels)", font_size=11,
                font_color=MEDIUM_GRAY)
add_bullet_text(tf2, "Source attribute + stratified split", font_size=12)
add_bullet_text(tf2, "Cross-domain evaluation design", font_size=12)
add_bullet_text(tf2, "Result: Full ML-Ready Unified Dataset", font_size=12,
                font_color=ACCENT_BLUE, bold=True)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 7: DETAILED PIPELINE STEPS
# ══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide, DARK_BG)
add_shape(slide, 0, 0, SLIDE_W, Inches(0.08), ACCENT_TEAL)

add_text_box(slide, MARGIN, Inches(0.3), Inches(3), Inches(0.35),
             "PIPELINE DETAILS", font_size=12, font_color=ACCENT_TEAL, bold=True)

add_text_box(slide, MARGIN, Inches(0.6), Inches(10), Inches(0.6),
             "Step-by-Step Integration Process",
             font_size=30, font_color=WHITE, bold=True)

add_accent_line(slide, MARGIN, Inches(1.2), Inches(6), ACCENT_TEAL, Pt(2))

# Pipeline steps as connected boxes
steps = [
    ("1", "Ingestion", "Read CSVs with chunking/\nsampling. Add source tag\n(dataset origin per row)", ACCENT_BLUE),
    ("2", "Feature Schema\nMapping", "Define canonical schema\n(common core of shared\nfeatures across datasets)", ACCENT_GREEN),
    ("3", "Column Rename\n& Type Norm.", "Duration→Time_To_Live\nNumeric coercion, inf/NaN", ACCENT_ORANGE),
    ("4", "Label\nHarmonization", "Map to 3 levels: Binary,\nCategory, Fine-grained", ACCENT_PURPLE),
    ("5", "Validation &\nCleaning", "Schema checks, duplicates,\nmissingness, range valid.", ACCENT_RED),
    ("6", "Feature\nScaling", "Standardize/normalize\nfeatures for comparable\ndistributions across sets", ACCENT_TEAL),
    ("7", "Split Strategy\n& Evaluation", "Stratified by label AND\nsource. Cross-domain\ngeneralization testing", ACCENT_BLUE),
    ("8", "Output: ML-Ready\nDataset", "Unified parquet + metadata\n(schema, label maps, stats)", ACCENT_GREEN),
]

box_w = Inches(1.35)
box_h = Inches(1.6)
total_gap = CONTENT_W - len(steps) * box_w
gap_x = total_gap / (len(steps) - 1) if len(steps) > 1 else 0
start_y = Inches(1.7)

for i, (num, title, desc, color) in enumerate(steps):
    x = MARGIN + i * (box_w + gap_x)
    
    # Number circle
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + box_w//2 - Inches(0.2),
                                     start_y, Inches(0.4), Inches(0.4))
    circle.fill.solid()
    circle.fill.fore_color.rgb = color
    circle.line.fill.background()
    circle.text_frame.paragraphs[0].text = num
    circle.text_frame.paragraphs[0].font.size = Pt(14)
    circle.text_frame.paragraphs[0].font.color.rgb = DARK_BG
    circle.text_frame.paragraphs[0].font.bold = True
    circle.text_frame.paragraphs[0].font.name = 'Calibri'
    circle.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # Box
    add_shape(slide, x, start_y + Inches(0.55), box_w, box_h, MEDIUM_BG, corner_radius=0.06)
    add_accent_line(slide, x + Inches(0.05), start_y + Inches(0.6), 
                    box_w - Inches(0.1), color, Pt(2))
    
    # Title
    add_text_box(slide, x + Inches(0.08), start_y + Inches(0.7), 
                 box_w - Inches(0.16), Inches(0.55),
                 title, font_size=10, font_color=color, bold=True,
                 alignment=PP_ALIGN.CENTER)
    
    # Desc
    add_text_box(slide, x + Inches(0.08), start_y + Inches(1.25),
                 box_w - Inches(0.16), Inches(0.9),
                 desc, font_size=8, font_color=MEDIUM_GRAY, bold=False,
                 alignment=PP_ALIGN.CENTER)
    
    # Arrow between boxes
    if i < len(steps) - 1:
        arrow_x = x + box_w
        arrow_y = start_y + Inches(0.55) + box_h // 2
        arrow_shape = slide.shapes.add_shape(
            MSO_SHAPE.RIGHT_ARROW, arrow_x, arrow_y, 
            gap_x, Inches(0.15)
        )
        arrow_shape.fill.solid()
        arrow_shape.fill.fore_color.rgb = MEDIUM_GRAY
        arrow_shape.line.fill.background()

# Key note at bottom
note_y = start_y + Inches(2.5)
add_shape(slide, MARGIN, note_y, CONTENT_W, Inches(3.3), MEDIUM_BG, corner_radius=0.03)

txBox = slide.shapes.add_textbox(MARGIN + Inches(0.3), note_y + Inches(0.15),
                                  CONTENT_W - Inches(0.6), Inches(3.0))
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Label Harmonization — 3-Level Taxonomy"
p.font.size = Pt(16)
p.font.color.rgb = ACCENT_PURPLE
p.font.bold = True
p.font.name = 'Calibri'

add_bullet_text(tf, "Binary: Benign vs Attack — simplest classification baseline", font_size=12)
add_bullet_text(tf, "Category: DDoS, DoS, Reconnaissance, Spoofing, MQTT, Mirai, Web-based, Brute Force — stable broad groups", font_size=12)
add_bullet_text(tf, "Fine-grained (Unified): 53 attack labels with unified naming across all three datasets — preserves maximum detail", font_size=12)
add_bullet_text(tf, "CICIoT2023: labels from 'Label' column  |  CICIoMT2024: from filename  |  IoMT-TrafficData: from filename + is_attack", font_size=11, font_color=MEDIUM_GRAY)
add_bullet_text(tf, "Overlapping attacks mapped to same unified name (e.g., ARP_Spoofing, Slow_Loris exist across datasets)", font_size=12)
add_bullet_text(tf, "Source attribute added to track dataset origin → enables cross-domain evaluation (train IoT, test IoMT & vice versa)", font_size=12)


# ══════════════════════════════════════════════════════════════════════
# SLIDE 8: SUMMARY & NEXT STEPS
# ══════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_slide_bg(slide, DARK_BG)
add_shape(slide, 0, 0, SLIDE_W, Inches(0.08), ACCENT_BLUE)

add_text_box(slide, MARGIN, Inches(0.3), Inches(3), Inches(0.35),
             "SUMMARY", font_size=12, font_color=ACCENT_BLUE, bold=True)

add_text_box(slide, MARGIN, Inches(0.6), Inches(10), Inches(0.6),
             "Key Takeaways & Next Steps",
             font_size=30, font_color=WHITE, bold=True)

add_accent_line(slide, MARGIN, Inches(1.2), Inches(6), ACCENT_BLUE, Pt(2))

# Left: Takeaways
left_w = Inches(5.8)
left_x = MARGIN
left_y = Inches(1.6)
left_h = Inches(5.3)

add_shape(slide, left_x, left_y, left_w, left_h, MEDIUM_BG, corner_radius=0.04)
add_accent_line(slide, left_x + Inches(0.1), left_y + Inches(0.08),
                left_w - Inches(0.2), ACCENT_GREEN, Pt(3))

txBox = slide.shapes.add_textbox(left_x + Inches(0.25), left_y + Inches(0.2),
                                  left_w - Inches(0.5), left_h - Inches(0.4))
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Key Takeaways"
p.font.size = Pt(18)
p.font.color.rgb = ACCENT_GREEN
p.font.bold = True
p.font.name = 'Calibri'

add_bullet_text(tf, "3 complementary datasets covering both general IoT and healthcare-specific IoMT domains", font_size=13)
add_bullet_text(tf, "CICIoMT2024 & CICIoT2023 share the same CIC lab origin and DPKT extraction pipeline → 39 directly compatible features", font_size=13)
add_bullet_text(tf, "IoMT-TrafficData uses Zeek features (different schema) → requires semantic feature mapping for integration", font_size=13)
add_bullet_text(tf, "Two-phase approach: first unify the IoMT domain (Phase 1), then integrate with general IoT (Phase 2)", font_size=13)
add_bullet_text(tf, "3-level label taxonomy enables flexible evaluation: from simple binary detection to fine-grained attack classification", font_size=13)
add_bullet_text(tf, "Flow-level integration is proposed (not packet-level) for efficiency and reproducibility", font_size=13)

# Right: Next Steps
right_x = left_x + left_w + Inches(0.3)
right_w = Inches(5.8)
right_h = Inches(5.3)

add_shape(slide, right_x, left_y, right_w, right_h, MEDIUM_BG, corner_radius=0.04)
add_accent_line(slide, right_x + Inches(0.1), left_y + Inches(0.08),
                right_w - Inches(0.2), ACCENT_ORANGE, Pt(3))

txBox2 = slide.shapes.add_textbox(right_x + Inches(0.25), left_y + Inches(0.2),
                                   right_w - Inches(0.5), right_h - Inches(0.4))
tf2 = txBox2.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]
p.text = "Next Steps"
p.font.size = Pt(18)
p.font.color.rgb = ACCENT_ORANGE
p.font.bold = True
p.font.name = 'Calibri'

add_bullet_text(tf2, "Phase 1: Identify & map semantically equivalent features between CICIoMT2024 (DPKT) and IoMT-TrafficData (Zeek)", font_size=13)
add_bullet_text(tf2, "Phase 1: Unify IoMT labels into a shared taxonomy covering both datasets", font_size=13)
add_bullet_text(tf2, "Phase 1: Produce a combined IoMT-only dataset as intermediate result", font_size=13)
add_bullet_text(tf2, "Phase 2: Merge the unified IoMT dataset with CICIoT2023 using the 39 shared DPKT features", font_size=13)
add_bullet_text(tf2, "Phase 2: Apply full label harmonization (53 unified labels across all 3 datasets)", font_size=13)
add_bullet_text(tf2, "Phase 2: Design cross-domain evaluation: train on IoT, test on IoMT (and vice versa) to measure generalization", font_size=13)
add_bullet_text(tf2, "Final: Build and evaluate ML/DL models on the unified dataset for network intrusion detection", font_size=13)


# ══════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'presentations', 'Three_Datasets_and_Integration_Pipeline_v2.pptx')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
prs.save(output_path)
print(f"Presentation saved to: {output_path}")
print(f"Total slides: {len(prs.slides)}")
