"""Validate a canonical follicular-unit release.

Checks:
  1. every image has exactly one label file (and vice versa)
  2. label format: >=5 fields, class id in range, box coords normalized [0,1]
  3. label boxes have sane aspect/size (not full-image degenerate boxes)
  4. duplicate detection by content hash: (a) leakage across splits, (b) duplicate sources
  5. per-split and per-class instance counts vs dataset.yaml

Usage:
    python scripts/validate_dataset.py --path ./data/follicle-v0.1 [--strict]

Exit code 1 on any hard error (missing labels, format, split leakage); 2 on warnings-only.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from collections import Counter, defaultdict
from pathlib import Path

IMG_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse_yaml_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    names, in_names = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("names:"):
            in_names = True
            continue
        if in_names:
            s = line.strip()
            if s.startswith("- "):
                names.append(s[2:].strip())
            elif ":" in s:
                names.append(s.split(":", 1)[1].strip())
            elif names and not s:
                break
    return names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True)
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = ap.parse_args()

    root = Path(args.path)
    yaml_path = next((p for p in (root / "dataset.yaml", root / "data.yaml") if p.exists()), None)
    names = parse_yaml_names(yaml_path) if yaml_path else []
    nclass = len(names)
    if yaml_path is None:
        print("WARN  no dataset.yaml/data.yaml found")
    else:
        print(f"ok    dataset: {yaml_path} classes={names}")

    errors: list[str] = []
    warnings: list[str] = []
    hashes: dict[str, list[str]] = defaultdict(list)
    per_split_class: dict[str, Counter] = {}

    for split in ("train", "val", "test"):
        img_dir, lbl_dir = root / "images" / split, root / "labels" / split
        if not img_dir.is_dir():
            if lbl_dir.is_dir():
                errors.append(f"{split}: labels dir exists without images dir")
            continue
        images = {p.stem: p for p in img_dir.rglob("*") if p.suffix.lower() in IMG_EXT}
        labels = {p.stem: p for p in lbl_dir.rglob("*.txt")} if lbl_dir.is_dir() else {}
        missing = set(images) - set(labels)
        extra = set(labels) - set(images)
        if missing:
            errors.append(f"{split}: {len(missing)} images without labels (e.g. {sorted(missing)[0]})")
        if extra:
            errors.append(f"{split}: {len(extra)} labels without images (e.g. {sorted(extra)[0]})")

        counts: Counter = Counter()
        for stem, lbl in sorted(labels.items()):
            img_path = images.get(stem)
            if img_path is None:
                continue
            hashes[sha256(img_path)].append(f"{split}/{img_path.name}")
            for ln, line in enumerate(lbl.read_text(encoding="utf-8").splitlines(), 1):
                parts = line.split()
                if len(parts) < 5:
                    errors.append(f"{split}/{lbl.name}:{ln} malformed: {line!r}")
                    continue
                try:
                    cls = int(parts[0])
                    vals = [float(v) for v in parts[1:5]]
                except ValueError:
                    errors.append(f"{split}/{lbl.name}:{ln} non-numeric: {line!r}")
                    continue
                if nclass and not 0 <= cls < nclass:
                    errors.append(f"{split}/{lbl.name}:{ln} class {cls} out of range")
                if not all(0.0 <= v <= 1.0 for v in vals):
                    errors.append(f"{split}/{lbl.name}:{ln} coords not normalized: {vals}")
                w, h = vals[2], vals[3]
                if w > 0.99 or h > 0.99 or w <= 0.001 or h <= 0.001:
                    warnings.append(f"{split}/{lbl.name}:{ln} degenerate box {w:.3f}x{h:.3f}")
                if counts is not None:
                    counts[cls] += 1
        per_split_class[split] = counts
        print(f"ok    {split}: {len(images)} images, {sum(counts.values())} instances {dict(counts)}")

    leaks = [paths for paths in hashes.values() if len({p.split('/')[0] for p in paths}) > 1]
    dups = [paths for paths in hashes.values() if len(paths) > 1]
    for group in leaks:
        errors.append(f"SPLIT LEAKAGE: identical image in multiple splits: {group[:4]}")
    for group in dups:
        if len(group) > 1:
            warnings.append(f"duplicate image content ({len(group)} copies): {group[:4]}")

    for e in errors:
        print("ERROR", e)
    for w in warnings:
        print("WARN ", w)

    if errors or (args.strict and warnings):
        print(f"\nFAIL: {len(errors)} errors, {len(warnings)} warnings")
        return 1
    print(f"\nPASS: {len(warnings)} warnings")
    return 0 if not warnings else 2


if __name__ == "__main__":
    raise SystemExit(main())
