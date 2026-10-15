# data-pipeline

Consolidated, license-clean follicular-unit datasets + the tooling to validate, convert, and extend them.

**Why this repo exists:** every public follicle dataset today is scattered (Roboflow, university sites, paper appendices), inconsistently licensed, and unreproduced. The "model" is not the bottleneck — **a known-good, attributable, machine-readable dataset supply is**. This repo is the supply chain.

## Layout

```
DATASETS.md              the manifest: every known dataset, its license, its status
ANNOTATION_GUIDE.md      how to label follicular units (count-based taxonomy)
schema/dataset_card.md   template every dataset must ship with
scripts/download_datasets.py   fetch all "clean" sources in one shot
scripts/validate_dataset.py    integrity + taxonomy + split-leak checks
scripts/convert_to_yolo_obb.py COCO/COCO-JSON -> YOLO-OBB conversion
scripts/import_labels.py       merge community annotations into a release
```

## Quick start

```bash
pip install -r requirements.txt

# 1. download all license-clean sources (~5 GB)
python scripts/download_datasets.py --out ./data/raw --set clean

# 2. convert + validate -> a canonical release
python scripts/convert_to_yolo_obb.py --input ./data/raw --output ./data/follicle-obb-v0.1
python scripts/validate_dataset.py --path ./data/follicle-obb-v0.1
```

Output release directory structure (YOLO-OBB, matches Ultralytics conventions):

```
follicle-obb-v0.1/
  dataset.yaml          # names: [fu1, fu2, fu3, fu4, fu5], path, train/val/test
  images/{train,val,test}/...
  labels/{train,val,test}/...   # class cx cy w h angle (OBB format)
  manifest.json         # provenance: source, license, attribution, hashes
```

## Taxonomy (v0.1)

One task: **detect follicular units and classify by hair count per unit.**

| Class | Meaning | Why it matters |
|---|---|---|
| `fu1` | unit with exactly 1 hair | small graft, high count, frontal work |
| `fu2` | unit with 2–3 hairs* | medium graft |
| `fu3` | unit with 4–5 hairs* | large graft, dense packing |
| `fu4` | unit with 6+ hairs* | maximum graft |
| `fu5` | ambiguous / unreadable | deliberate class for honesty — ambiguous crops exist |

\* Exact bucket boundaries are set per dataset from the source annotations; see `DATASETS.md` for the active mapping. `fu5` exists so the model can express uncertainty instead of guessing.

## Status

- [x] Manifest v0.1: 2 license-clean public datasets identified (688 + 716 images)
- [ ] Canonical release `follicle-obb-v0.1` (blocked on: dedup check between the two sources — see DATASETS.md issue #1)
- [ ] Community labeling round 1 (target: 1,000 new images)
- [ ] Benchmark harness lives in `follicle-detect/benchmark/` (cross-repo)

## The goal for this repo

By month 3: the **largest permissively-licensed follicular-unit dataset in existence**, with a published validator others run against their own private hospitals datasets. The model follows the data, not the other way around.
