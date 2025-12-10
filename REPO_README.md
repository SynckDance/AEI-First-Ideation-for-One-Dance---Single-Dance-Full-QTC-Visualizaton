# AEI First Ideation — Single-Dance Full QTC Visualization

**Live Demo:** [https://synckdance.github.io/AEI-First-Ideation-for-One-Dance---Single-Dance-Full-QTC-Visualizaton/](https://synckdance.github.io/AEI-First-Ideation-for-One-Dance---Single-Dance-Full-QTC-Visualizaton/)

---

## Overview

This is the first AEI (Artificial Embodied Intelligence) prototype for single-dance analysis, featuring the **Ekombi** dance from the GMR archive.

The viewer implements:
- **Real motion capture playback** from Captury Live data (9,485 frames at 60fps)
- **QTC (Qualitative Trajectory Calculus)** analysis for 8 joint pairs
- **SAM (Sequence Alignment Method)** motif detection
- **Interactive timeline** with play/pause and speed control

---

## Dance Information

| Attribute | Value |
|-----------|-------|
| **Dance** | Ekombi |
| **Tradition** | Efik/Ibibio |
| **Region** | Cross River, Nigeria |
| **Performer** | Sinclair |
| **Duration** | 2:38 (158 seconds) |
| **Capture Date** | October 17, 2024 |

---

## QTC Analysis Results

| Joint Pair | Approach | Diverge | Stationary | Cross |
|------------|----------|---------|------------|-------|
| L Hand ↔ Head | 30.7% | 28.1% | 39.8% | 1.5% |
| R Hand ↔ Head | 26.3% | 27.8% | 44.7% | 1.2% |
| L Hand ↔ R Hand | 33.7% | 35.6% | 25.0% | 5.6% |
| L Foot ↔ Pelvis | 19.4% | 19.1% | 61.3% | 0.3% |
| Head ↔ Pelvis | 2.8% | 2.4% | 94.9% | 0.0% |

The QTC distribution reveals Ekombi's characteristic movement qualities:
- **Active upper body** — frequent approach/diverge in hand-head relationships
- **Bilateral coordination** — highest crossing rate in hand-to-hand pair
- **Grounded lower body** — predominantly stationary foot-pelvis relationships
- **Stable spine** — near-total stability in head-pelvis relationship

---

## Features

- **Left Panel:** Joint selector with real-time QTC state indicators
- **Center Panel:** Skeleton visualization with highlighted active pair
- **Right Panel:** QTC strip, narrative story, and detected motifs
- **Bottom:** Full transport controls with timeline scrubbing

---

## Part of Global Movement Research

This viewer is part of the GMR (Global Movement Research) project investigating dance traditions across geography and history.

**Principal Investigator:** Sinclair Emoghene, University of Texas at Austin

---

## Technical Notes

- Self-contained HTML (no external dependencies except Google Fonts)
- Data embedded directly in the file
- Frame sampling: every 4th frame for optimal file size
- QTC threshold: 2.5mm per frame

---

*© 2024 Global Movement Research*
