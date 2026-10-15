# Dataset card — required template

Every dataset published under this project must ship a card based on this file, named `dataset_card.md` in the release directory. Copy this template; replace the sections; delete nothing.

---

name: `follicle-obb-vX.Y`
license: `cc-by-4.0`
language: `n/a` (images)
task: object-detection / instance-segmentation (bbox, fu1–fu5)

## Provenance

- Source(s): (list each with URL, download date, source license, required attribution)
- Redistribution rights: (who confirmed what, when)

## Composition

| Split | Images | Instances | Notes |
|---|---|---|---|
| train | | | |
| val | | | |
| test | | | |

Classes: `fu1` `fu2` `fu3` `fu4` `fu5` = number of hair shafts per follicular unit (2–3, 4–5, 6+ buckets). `fu5` = unreadable/ambiguous.

## Collection process

Who collected/annotated, with what tool, under what review protocol, and — where applicable — consent basis. Synthetic data must be labeled synthetic.

## Known limitations

Capture device, resolution ranges, ethnicities/textures represented, conditions NOT represented. Be specific. A dataset that is only Fitzpatrick I–II scalps is a model limitation, not a surprise.

## Validation

Result of `scripts/validate_dataset.py --path <this dir> --strict`, pasted verbatim.

## Citation

How to cite the source datasets (each source has its own required attribution) and this release:

```bibtex
@misc{openhairstack_follicle_obb_vX_Y,
  title  = {Open Hair Stack Follicle Unit Dataset vX.Y},
  author = {Open Hair Stack contributors},
  year   = {2026},
  url    = {https://github.com/openhairstack/data-pipeline}
}
```
