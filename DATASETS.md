# Datasets manifest

Every known public dataset for hair-follicle detection, with license status. **A dataset is only usable if this file says its license is compatible.** Add entries by PR.

Legend: ✅ license-clean and redistributable · ⚠️ usable, conditions apply · ❌ research-only / do not merge

---

## ✅ Clean (CC BY 4.0) — merged into `follicle` releases

### 1. ranaudio / hair-follicle-detection-gjgak

- **Source:** https://universe.roboflow.com/ranaudio/hair-follicle-detection-gjgak (Roboflow Universe)
- **Task:** object detection (axis-aligned boxes) · **Images:** 688 · **Classes:** 5 (named `1`–`5` — hair count per unit) · **License:** CC BY 4.0
- **Attribution:** `ranaudio, "Hair Follicle Detection Dataset", Roboflow Universe (2025)` — exact cite on project page
- **Status:** ✅ primary v0.1 training source. Class names are the hair counts, matching our fu1–fu5 taxonomy; the converter maps them from the export's `data.yaml`.
- **Download:** `python scripts/download_datasets.py --source ranaudio-fu5`
- **Notes:** closest thing to a graft-sizing dataset. Train/val/test splits exist in export (70/20/10). ⚠ class ids in the export are 0-based — the converter resolves names, never assumes ids.

### 2. Purandhar / hair-follicle-detection-huxvk

- **Source:** https://universe.roboflow.com/purandhar-wdd7k/hair-follicle-detection-huxvk
- **Images:** 688 · **Classes:** 5 (numeric) · **License:** CC BY 4.0
- **Status:** ⚠️ **Suspected re-upload of #1** (identical image count and class scheme). Do not merge without hashing comparison — see issue #1.
- **Action item (contributor-friendly):** hash a sample of images from both exports and file a PR to this file. The validator already flags duplicate image content.

### 3. Vera Robotics / hair-follicle-2

- **Source:** https://universe.roboflow.com/vera-robotics/hair-follicle-2-0x4hy (716 images; several versions — the downloader pins one)
- **Images:** 716 · **Classes:** 2 (`follicle`, `follicles`) · **License:** CC BY 4.0 · reported mAP@50 79.7% (yolov11s)
- **Status:** ⚠️ different taxonomy (presence only, no hair counts). Candidate for a v0.2 "presence" head or weak-label source. Not merged into v0.1 — mixing taxonomies mislabels graft size.
- **Note:** publisher builds transplant robots — potential outreach contact (see `outreach/` in launch assets).

---

## ⚠️ Usable with conditions

### 4. Ultralytics "scalps" dataset

- **Source:** https://docs.ultralytics.com/datasets/detect/scalps/
- **Images:** 4,005 · **Annotations:** 59,471 individual hair follicle + shaft detections · **License:** AGPL-3.0
- **Conditions:** AGPL — usable inside this project because our code is Apache 2.0 but the *dataset export* is a "derived collection" carrying AGPL. Complicated. **Decision open — see `governance/rfcs/0001-agpl-datasets.md`** (no merge until decided).
- **Why it matters:** it is 5x larger than anything else, and has per-hair shaft annotations (useful later for extraction simulation).

### 5. YOLO-OHFD dataset (paper's OBB set)

- **Source:** paper code: https://github.com/Melonpoint/YOLO-OHFD (MDPI Applied Sciences 2025, open access)
- **Status:** ❌ **not released.** The paper describes an OBB hair-follicle dataset + oriented detector; the repo is 3 stars, 2 commits, no release, no license. Prior art; we reimplement from the paper and cite it.
- **Action:** DM the corresponding author on X (draft in `launch-assets/dm-outreach/`) inviting collaboration — this is the single most relevant research group.

---

## ❌ Research-only (reference/benchmark, do not redistribute)

### 6. Fudan / Huashan Hospital follicle dataset

- **Source:** paper — X Gu et al., "A New Dataset for Hair Follicle Recognition and Detection", ICANN 2023 (https://doi.org/10.1007/978-3-031-44207-0_4)
- **Content:** 1,652 images, 20,697 annotated vectors, 4 classes, clinical dermoscopic images
- **Status:** ❌ "publicly available" in the research sense (request-based). Referenced in papers; not redistributed here.
- **Action:** request benchmark access. If we get it, results go in the benchmark under strict terms, artifacts stay private.

### 7. ARTAS / HAIRO internal data

Closed. Referenced for market context only.

---

## Planned contributions (what we make)

| Name | Size | License | Status |
|---|---|---|---|
| `follicle-v0.1` | cleaned merge of #1 (+#2 after dedup), axis-aligned boxes | CC BY 4.0 | building |
| `follicle-v0.2` | + Vera presence-mapped + cleaned | CC BY 4.0 | backlog |
| `follicle-obb-v0.3` | oriented boxes for crowded regions | CC BY 4.0 | roadmap |
| `haircount-val` | 200 hand-verified images for eval only | CC BY 4.0 | labeling round 1 |
| `synthetic-scalp-v1` | Blender-rendered scalps w/ ground-truth FU counts | CC0 | planned |

## For maintainers: adding a dataset

1. Check license on the project page — screenshot it in the PR.
2. Add an entry here (all fields) before any code references it.
3. Add loader support in `download_datasets.py` behind a `--source <name>` flag.
4. Convert with `convert_to_yolo.py`, validate, hash, publish.
