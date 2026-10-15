# Dataset card — required template

Every dataset published under this project must ship a card based on this file, named `dataset_card.md` in the release directory. Copy this template; replace the sections; delete nothing.

---

name: `follicle-vX.Y`
license: `cc-by-4.0`
language: `n/a` (images)
task: object-detection (axis-aligned boxes, classes fu1–fu5)

## Provenance

- Source(s): (list each with URL, download date, source license, required attribution)
- Redistribution rights: (who confirmed what, when)

## Composition

| Split | Images | Instances | Notes |
|---|---|---|---|
| train | | | |
| val | | | |
| test | | | |

Classes: `fu1` `fu2` `fu3` `fu4` `fu5` = hair shafts per follicular unit (exact counts 1–4; `fu5` = 5 or more).

## Collection process

Who collected/annotated, with what tool, under what review protocol, and — where applicable — consent basis. Synthetic data must be labeled synthetic.

## Known limitations

Capture device, resolution ranges, ethnicities/textures represented, conditions NOT represented. Be specific. A dataset that is only Fitzpatrick I–II scalps is a model limitation, not a surprise.

## Validation

Result of `scripts/validate_dataset.py --path <this dir> --strict`, pasted verbatim.

## Citation

How to cite the source datasets (each source has its own required attribution) and this release:

```bibtex
@misc{openhairstack_follicle_vX_Y,
  title  = {Open Hair Stack Follicle Unit Dataset vX.Y},
  author = {Open Hair Stack contributors},
  year   = {2026},
  url    = {https://github.com/openhairstack/data-pipeline}
}
```
