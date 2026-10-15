"""Download license-clean follicular-unit datasets into ./data/raw.

Usage:
    python scripts/download_datasets.py --out ./data/raw --set clean
    python scripts/download_datasets.py --source ranaudio-fu5 --out ./data/raw
    python scripts/download_datasets.py --set clean --allow-agpl   # includes Ultralytics scalps (AGPL)

Roboflow sources need a free API key (https://docs.roboflow.com/developer/api/authentication):
    export ROBOFLOW_API_KEY=rf_xxxx      or pass --key rf_xxxx

Each download records sha256 + provenance into <out>/<source>/manifest.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCES = {
    # name: (roboflow api ref, license, attribution)
    "ranaudio-fu5": {
        "roboflow": ("ranaudio", "hair-follicle-detection-gjgak", 1),
        "license": "CC-BY-4.0",
        "attribution": 'ranaudio, "Hair Follicle Detection Dataset", Roboflow Universe (2025)',
        "classes": ["1", "2", "3", "4", "5"],
        "export": "yolov8",
    },
    "purandhar-fu5": {
        "roboflow": ("purandhar-wdd7k", "hair-follicle-detection-huxvk", 1),
        "license": "CC-BY-4.0",
        "attribution": 'Purandhar, "Hair Follicle Detection Dataset", Roboflow Universe (2025)',
        "classes": ["1", "2", "3", "4", "5"],
        "export": "yolov8",
        "warning": "Suspected duplicate of ranaudio-fu5. Run validate after download; do not merge blindly.",
    },
    "vera-robotics-fu2": {
        "roboflow": ("vera-robotics", "hair-follicle-2-0x4hy", 5),
        "license": "CC-BY-4.0",
        "attribution": 'Vera Robotics, "Hair Follicle 2 Dataset", Roboflow Universe (2025)',
        "classes": ["follicle", "follicles"],
        "export": "yolov8",
        "warning": "Presence-only taxonomy (no hair counts). Not compatible with fu1-fu5 training.",
    },
    "ultralytics-scalps": {
        "url": "https://ultralytics.com/assets/scalps.zip",
        "license": "AGPL-3.0",
        "attribution": "Ultralytics, 'scalps' dataset, https://github.com/ultralytics/assets (AGPL-3.0)",
        "warning": "AGPL: check governance/rfcs/0001-agpl-datasets.md before merging into any release.",
    },
}

CLEAN = ["ranaudio-fu5", "purandhar-fu5", "vera-robotics-fu2"]
AGPL = ["ultralytics-scalps"]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def zip_of_dir(path: Path) -> Path:
    out = path.with_suffix(".zip")
    if out.exists():
        out.unlink()
    shutil.make_archive(str(path), "zip", root_dir=path)
    return out


def fetch_roboflow(name: str, info: dict, dest: Path, api_key: str | None) -> Path:
    key = api_key or os.environ.get("ROBOFLOW_API_KEY")
    if not key:
        raise SystemExit(
            f"[{name}] needs a Roboflow API key: export ROBOFLOW_API_KEY=rf_... "
            "(free at https://docs.roboflow.com/developer/api/authentication)"
        )
    from roboflow import Roboflow  # noqa: PLC0415

    ws, proj, ver = info["roboflow"]
    rf = Roboflow(api_key=key)
    project = rf.workspace(ws).project(proj)
    version = project.version(ver)
    location = version.download(info["export"]).location  # downloads ./<proj>-<ver>
    src = Path(location).resolve()
    target = dest / name
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(src), str(target))
    return target


def fetch_url(name: str, url: str, dest: Path) -> Path:
    import urllib.request  # noqa: PLC0415

    target_dir = dest / name
    target_dir.mkdir(parents=True, exist_ok=True)
    archive = target_dir / url.split("/")[-1]
    print(f"[{name}] downloading {url}")
    urllib.request.urlretrieve(url, archive)
    with (target_dir / "raw.zip").open("wb") as dst, archive.open("rb") as src:
        dst.write(src.read())
    archive.unlink()
    return target_dir


def write_manifest(name: str, info: dict, folder: Path) -> None:
    files = sorted(p for p in folder.rglob("*") if p.is_file())
    payload = {
        "source": name,
        "license": info["license"],
        "attribution": info.get("attribution"),
        "classes": info.get("classes"),
        "warning": info.get("warning"),
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "files": {str(p.relative_to(folder)): sha256_of(p) for p in files},
    }
    (folder / "manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="./data/raw")
    ap.add_argument("--source", action="append", default=[])
    ap.add_argument("--set", choices=["clean", "agpl", "all"], default="clean")
    ap.add_argument("--allow-agpl", action="store_true")
    ap.add_argument("--key", help="Roboflow API key (or set ROBOFLOW_API_KEY)")
    args = ap.parse_args()

    wanted = args.source or (CLEAN if args.set == "clean" else AGPL if args.set == "agpl" else CLEAN + AGPL)
    wanted = [s for s in wanted if s not in AGPL or args.allow_agpl or s in args.source]
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)

    failures = []
    for name in wanted:
        info = SOURCES[name]
        try:
            if info.get("warning"):
                print(f"[{name}] WARNING: {info['warning']}")
            if "roboflow" in info:
                folder = fetch_roboflow(name, info, dest, args.key)
            else:
                folder = fetch_url(name, info["url"], dest)
            write_manifest(name, info, folder)
            print(f"[{name}] ok -> {folder}")
        except Exception as exc:  # noqa: BLE001
            print(f"[{name}] FAILED: {exc}", file=sys.stderr)
            failures.append(name)

    if failures:
        print(f"\n{len(failures)} source(s) failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    print("\nNext: python scripts/convert_to_yolo.py --input", str(dest), "--output ./data/follicle-v0.1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
