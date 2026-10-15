# Annotation guide: follicular units

Labeling follicles is a skill that takes ~15 minutes to learn and one coffee break to get consistent. Read this fully before your first batch.

## What a follicular unit is

A follicular unit (FU) is the naturally-occurring bundle of 1–5+ hair shafts emerging from a single pore. Transplant grafts are cut from these bundles — **graft size = hair count per unit**, which is exactly what the model must learn. Your annotation directly trains the classifier that estimates graft size, the number transplant planning is based on.

## Our taxonomy (v0.1)

Draw one box per follicular unit. Tag it by how many hair shafts you can *confidently* see emerging from the pore — the classes are exact counts:

| Tag | Hairs per unit |
|---|---|
| `fu1` | 1 |
| `fu2` | 2 |
| `fu3` | 3 |
| `fu4` | 4 |
| `fu5` | 5+ (rare; count everything above four as `fu5`) |

Can't count a unit confidently — blur, occlusion, motion, blown-out highlight? **Skip it; don't
guess.** Forcing a guess poisons training data. If you're skipping many units, the image is
probably unusable — flag it for the batch owner.

## Drawing rules

1. **One box per pore, not per hair.** A box enclosing three hairs that share one pore = one `fu2`, not three boxes.
2. **Tight to the bundle.** Corners just outside the outermost shafts, not around the scalp region.
3. **Axis-aligned boxes for v0.1.** Draw the rectangle tight to the bundle. Oriented boxes (OBB) are a later milestone — don't use tool rotation in this round.
4. **Partial FUs at image edge:** label them normally if ≥1 shaft emergence is visible; skip if cut off before the pore.
5. **Never guess follicle geometry under heavy scaling artifacts.** Digital trichoscopes (and phone macro shots) distort at frame edges.

## Difficult calls (ask in Discord `#data` or a GitHub issue when unsure)

- **Hairs merging into a mat / afro texture:** label one `fu3` per merge point if you can see it, else `fu5`.
- **Dense bald-region borders:** label FUs you can see; do not infer hidden ones.
- **Sparse regrowth / early recovery:** label only defined FUs with at least one terminal shaft.

## Quality bar

Project maintainers sample-audit 10% of every labeling batch against two reviewers. A batch whose per-unit class agreement drops below ~0.8 kappa gets relabeled — this is normal, not blame. The validator `scripts/validate_dataset.py` checks: box/shaft count sanity per image, label image parity, and train/val split leakage by hash.

## Tools

- **CVAT** (self-hosted or cloud free tier) — supports OBB, has web UI, exports to COCO/YOLO. Default.
- **Label Studio** — good if labels come from multiple taxonomies.
- **roboflow Annotate** — OK for the legacy datasets; avoid exporting back through their format converters when possible.

## Consent and privacy (hard rules)

Only label images you have the right to label. Never upload identifiable patient photos to this project. Public clinical datasets stay request-based research-only — that boundary is a Charter issue, not a workflow preference.
