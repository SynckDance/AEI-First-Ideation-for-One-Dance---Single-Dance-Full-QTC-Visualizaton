# Ekombi Single-Dance QTC Viewer — Production Build

## Overview

This is the **production build** of the Single-Dance QTC/SAM Viewer for the Ekombi dance, using **real motion capture data** from the Captury Live system.

---

## Data Source

- **Source File:** `Sinclair_Ekombi_csv_1.csv`
- **Capture Date:** October 17, 2024
- **Capture System:** Captury Live 1.0.263f
- **Total Frames:** 9,485 frames
- **Frame Rate:** 60.0024 fps
- **Duration:** 158.08 seconds (2:38)
- **Performer:** Sinclair
- **Tradition:** Efik/Ibibio (Cross River, Nigeria)

---

## Real QTC Analysis Results

The QTC sequences were computed from actual joint trajectory data with a threshold of 2.5mm:

| Joint Pair | Approach | Diverge | Stationary | Cross |
|------------|----------|---------|------------|-------|
| **L Hand ↔ Head** | 30.7% | 28.1% | 39.8% | 1.5% |
| **R Hand ↔ Head** | 26.3% | 27.8% | 44.7% | 1.2% |
| **L Hand ↔ R Hand** | 33.7% | 35.6% | 25.0% | 5.6% |
| **L Hand ↔ Pelvis** | 33.1% | 32.5% | 31.6% | 2.8% |
| **R Hand ↔ Pelvis** | 28.8% | 29.7% | 39.1% | 2.4% |
| **L Foot ↔ Pelvis** | 19.4% | 19.1% | 61.3% | 0.3% |
| **R Foot ↔ Pelvis** | 23.2% | 21.6% | 54.9% | 0.3% |
| **Head ↔ Pelvis** | 2.8% | 2.4% | 94.9% | 0.0% |

### Movement Signature Interpretation

The QTC distributions reveal Ekombi's characteristic movement qualities:

1. **Active Upper Body** — Hand-head pairs show ~30% approach and ~28% diverge, indicating the continuous graceful arm gestures reaching toward and away from the head.

2. **Bilateral Coordination** — L Hand ↔ R Hand shows the highest cross percentage (5.6%) among all pairs, reflecting the coordinated wave-like arm patterns.

3. **Grounded Lower Body** — Foot-pelvis pairs are predominantly stationary (55-61%), confirming Ekombi's characteristic grounded quality with subtle footwork.

4. **Stable Spine** — Head ↔ Pelvis is 94.9% stationary, showing the upright, stable torso that serves as the anchor for arm expression.

---

## Files

```
ekombi-production/
├── ekombi-qtc-viewer.html    # Full interactive viewer (35KB)
├── ekombi_full_data.json     # Complete motion + QTC data (5.8MB)
└── parse_ekombi.py           # Python parser/QTC computer
```

---

## Usage

1. **Place both files in the same directory**
2. **Serve via HTTP** (required for JSON loading):
   ```bash
   python3 -m http.server 8000
   ```
3. **Open in browser:** `http://localhost:8000/ekombi-qtc-viewer.html`

Or deploy to GitHub Pages alongside the GMR site.

---

## Features

### Left Panel: The Points
- Click joints to see their relationships
- Real-time QTC state indicators (colored dots)
- Distribution histograms for each pair

### Center Panel: The Body  
- Real skeleton playback from Captury Live data
- Active pair highlighted with QTC-colored connection
- Front view projection (X horizontal, Y vertical)

### Right Panel: Views
- **QTC Tab:** Time-aligned state strip with distribution percentages
- **Story Tab:** Natural language description of current motion
- **Motifs Tab:** 15 detected movement patterns (click to jump)

### Bottom: Timeline
- Full transport controls with speed adjustment
- Motif markers showing where patterns occur
- Scrub to any point in the 2:38 dance

---

## Detected Motifs

The SAM analysis identified 80 approach-diverge patterns across all joint pairs. The top 15 motifs are displayed in the viewer, including:

- Reaching Gestures (hand approaching head)
- Wave Patterns (bilateral hand coordination)
- Cascading Arms (hands diverging from pelvis)
- Grounded Steps (subtle foot-pelvis movements)

---

## Technical Notes

### Coordinate System
- Captury Live uses: X = left/right, Y = up/down, Z = front/back
- Positions in millimeters, normalized to 0-1 range for visualization
- Front view projection displayed in canvas

### QTC Computation
- Threshold: 2.5mm per frame
- States: +0 (approach), 0- (diverge), 00 (stationary), 0c (cross)
- Cross detection: direction reversal between consecutive frames

### Data Sampling
- Raw frames: 9,485 at 60fps
- Sampled for output: every 2nd frame (4,742 frames)
- QTC sequences also sampled 2x for file size optimization

---

## Integration with GMR Site

To add this viewer to the GMR site:

1. Copy files to `gmr-site/qtc-lab/`
2. Add navigation link from dances.html
3. Consider adding a "QTC Analysis" button to each dance card

---

## Next Steps

1. **Apply to all 33 dances** — Run the parser on each CSV to build a library of QTC viewers
2. **Cross-dance comparison** — Use SAM alignment to compare QTC sequences between dances
3. **3D upgrade** — Replace 2D canvas with Three.js for full orbit/pan/zoom
4. **AEI narrative** — Expand story text with deeper movement interpretation

---

*Built with real Captury Live motion capture data*  
*Global Movement Research • Sinclair Emoghene • UT Austin*
