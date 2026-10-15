"""Build a canonical YOLO release from raw downloads.

Usage:
    python scripts/convert_to_yolo_obb.py --input ./data/raw --output ./data/follicle-obb-v0.1
    python scripts/convert_to_yolo_obb.py --source ranaudio-fu5 --class-map 1:fu1,2:fu2,3:fu3,4:fu4,5:fu5

Roboflow exports look like:
    <export>/data.yaml, train/{images,labels}, valid/{images,labels}, test/{images,labels}

This script copies every source export into a unified release dir:
    <output>/dataset.yaml, images/{train,val,test}, labels/{train,val,test}, manifest.json
with class ids remapped to the canonical fu1..fu5 taxonomy and filenames prefixed
by source to guarantee uniqueness.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

CANON = ["fu1", "fu2", "fu3", "fu4", "fu5"]
# our split name -> Roboflow export split name
SPLIT_DIR = {"train": "train", "val": "valid", "test": "test"}

DEFAULT_CLASS_MAP: dict[str, dict[str, str]] = {
    "ranaudio-fu5": {"1": "fu1", "2": "fu2", "3": "fu3", "4": "fu4", "5": "fu5"},
    "purandhar-fu5": {"1": "fu1", "2": "fu2", "3": "fu3", "4": "fu4", "5": "fu5"},
}


def parse_class_map(spec: str) -> tuple[str, dict[str, str]]:
    src, _, rest = spec.partition(":")
    return src, {p.split(":")[0].strip(): p.split(":")[1].strip() for p in rest.split(",")}


def find_export(source_dir: Path) -> Path:
    """Roboflow SDK extracts to a dir containing data.yaml + split dirs."""
    if (source_dir / "data.yaml").exists() or (source_dir / "train").is_dir():
        return source_dir
    hits = [p for p in source_dir.rglob("data.yaml")]
    if hits:
        return hits[0].parent
    hits = [p for p in source_dir.rglob("train/images")]
    return hits[0].parent if hits else source_dir


def rewrite_labels(lbl: Path, cmap: dict[str, str]) -> tuple[list[str], Counter]:
    lines, counts = [], Counter()
    for line in lbl.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        new_cls = cmap.get(parts[0])
        if new_cls not in CANON:
            continue
        lines.append(" ".join([str(CANON.index(new_cls))] + parts[1:]))
        counts[new_cls] += 1
    return lines, counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="dir containing per-source export dirs")
    ap.add_argument("--output", required=True)
    ap.add_argument("--source", action="append", default=[], help="restrict to these source dirs")
    ap.add_argument("--class-map", action="append", default=[], help="e.g. ranaudio-fu5:1:fu1,2:fu2")
    args = ap.parse_args()

    root = Path(args.input)
    out = Path(args.output)
    for split in ("train", "val", "test"):
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)

    class_maps = dict(DEFAULT_CLASS_MAP)
    for spec in args.class_map:
        src, cmap = parse_class_map(spec)
        class_maps[src] = cmap

    sources = args.source or [
        p.name for p in root.iterdir() if p.is_dir() and p.name not in ("manifest.json",)
    ]

    manifest: dict = {"classes": CANON, "sources": [], "notes": []}
    total: Counter = Counter()

    for src in sources:
        cmap = class_maps.get(src)
        if not cmap:
            print(f"[{src}] no class map; taxonomy unrecognized -> skipped "
                  f"(pass --class-map {src}:1:fu1,...)", file=sys.stderr)
            manifest["notes"].append(f"{src}: skipped, no class map")
            continue
        export = find_export(root / src)
        counts: Counter = Counter()
        for our_split, src_split in SPLIT_DIR.items():
            img_root = export / src_split / "images"
            lbl_root = export / src_split / "labels"
            if not img_root.is_dir():
                continue
            for img in sorted(img_root.rglob("*")):
                if img.suffix.lower() not in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
                    continue
                lbl = lbl_root / f"{img.stem}.txt"
                if not lbl.exists():
                    print(f"[{src}] no label for {img.name} - skipped", file=sys.stderr)
                    continue
                lines, c = rewrite_labels(lbl, cmap)
                if not lines:
                    continue
                stem = f"{src.replace('-', '_')}_{img.stem}"
                shutil.copy2(img, out / "images" / our_split / f"{stem}{img.suffix.lower()}")
                (out / "labels" / our_split / f"{stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
                counts.update(c)
        if counts:
            manifest["sources"].append(
                {"name": src, "license": "CC-BY-4.0",
                 "see": "DATASETS.md", "instances": dict(counts)}
            )
            print(f"[{src}] {sum(counts.values())} instances {dict(counts)}")
            total.update(counts)

    (out / "dataset.yaml").write_text(
        "# canonical follicular-unit release\n"
        f"path: {out.resolve()}\ntrain: images/train\nval: images/val\ntest: images/test\n\n"
        "names:\n" + "".join(f"  {i}: {c}\n" for i, c in enumerate(CANON)),
        encoding="utf-8",
    )
    manifest["class_totals"] = dict(total)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    n = sum(total.values())
    print(f"\nrelease -> {out} ({n} instances, totals {dict(total)})")
    if n == 0:
        print("NOTHING IMPORTED. Check class maps (--class-map) and export layout.", file=sys.stderr)
        return 1
    print("next: python scripts/validate_dataset.py --path", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
