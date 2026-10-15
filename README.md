# data-pipeline

> **The foundation:** every openly-licensed hair-follicle dataset consolidated, validated,
> and documented — plus the tools to grow the largest freely-usable scalp dataset we can get to.

### In plain English

Hair grows in little bundles called *follicular units*, usually 1–6 hairs per bundle. How many
hairs are in each bundle is the single most useful number in transplant work — the whole bundle
moves as one unit, so the count decides graft size.

This repo exists because: the images that teach computers to see those bundles are scattered
across the internet under inconsistent licenses, with nobody checking whether they're labeled
correctly. We collect them, keep receipts (provenance + license), and ship a tool that catches
broken data before it poisons a model.

**You can help without writing code:** labeling is a 15-minute skill. Start with
[ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md).

---

## What's inside

| File | What it is |
|---|---|
| `DATASETS.md` | the manifest: every known public dataset, its license, its status |
| `scripts/download_datasets.py` | fetches every license-clean source in one command |
| `scripts/convert_to_yolo.py` | builds a canonical release from any export (class mapping from the export's data.yaml) |
| `scripts/validate_dataset.py` | integrity + format + split-leakage checker |
| `ANNOTATION_GUIDE.md` | how to label follicular units (the 15-minute skill) |
| `schema/dataset_card.md` | provenance card every release must ship |
| `tests/test_pipeline.py` | smoke test the whole flow on synthetic data |

## Quick start

```bash
pip install -r requirements.txt

# 1. download all license-clean sources (~5 GB)
python scripts/download_datasets.py --out ./data/raw --set clean

# 2. convert + validate into a canonical release
python scripts/convert_to_yolo.py --input ./data/raw --output ./data/follicle-v0.1
python scripts/validate_dataset.py --path ./data/follicle-v0.1
```

Run the tests without downloading anything:
```bash
python tests/test_pipeline.py   # synthetic data, checks convert + validate + planner logic
```

## The taxonomy (v0.1)

One task: **detect follicular units and classify their hair count.** The classes are exact
counts — the number graft-size planning is based on. The converter reads each export's own
`data.yaml` and maps its class names onto this taxonomy automatically.

| Class | Hairs per unit |
|---|---|
| `fu1` | 1 |
| `fu2` | 2 |
| `fu3` | 3 |
| `fu4` | 4 |
| `fu5` | 5+ |

Uncountable units are skipped during labeling rather than guessed (see the annotation guide) —
v0.1 has no "unsure" class; a missed unit shows up as a lower count, never a wrong label.

## How to add a dataset

1. Check the license on the project page — screenshot it in the PR.
2. Add the entry to `DATASETS.md` (all fields) **before** any code references it.
3. Add loader support in `download_datasets.py` behind a `--source <name>` flag.
4. Convert → validate → hash → publish with a dataset card.

## Status

- [x] Manifest v0.1: license-clean public datasets identified (688 + 716 images)
- [ ] Canonical release `follicle-v0.1` (dedup check between two suspected-duplicate sources — first good issue)
- [ ] Community labeling round 1 (target: 1,000 newly labeled images)
- [ ] Benchmark harness (the `follicle-detect/benchmark/` directory is itself an open contribution)

**Month-3 goal:** the largest permissively-licensed follicular-unit dataset we can get to,
with a published validator others run against their own hospital datasets.
