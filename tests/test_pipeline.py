"""Smoke-test the data pipeline scripts end to end with synthetic data.

Usage:
    python tests/test_pipeline.py            # uses a scratch dir in the system temp
    OHS_TEST_DIR=./scratch python tests/test_pipeline.py

Creates a fake Roboflow export, runs convert_to_yolo_obb.py, validates the
release (expect PASS), corrupts a label and validates again (expect FAIL),
then smoke-tests scalp-analyzer's plan_simulation + _bar_chart (stdlib+PIL only).

No third-party deps beyond Pillow; no GPU, no model weights, no network.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PY = sys.executable
REPOS = Path(__file__).resolve().parents[2]  # repos/
BASE = Path(os.environ.get("OHS_TEST_DIR", Path(tempfile.gettempdir()) / "ohs-pipeline-test"))

# ---------- fake roboflow export ----------
export = BASE / "raw" / "ranaudio-fu5"
for split in ("train", "valid", "test"):
    (export / split / "images").mkdir(parents=True, exist_ok=True)
    (export / split / "labels").mkdir(parents=True, exist_ok=True)
for i, split in enumerate(["train"] * 3 + ["valid"] + ["test"]):
    import random

    from PIL import Image

    random.seed(i)
    img = Image.new("RGB", (64, 64))
    img.putdata([(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                 for _ in range(64 * 64)])
    img.save(export / split / "images" / f"img_{i}.jpg")
    labels = []
    for cls in ["1", "2", "3", "4", "5"][: (i % 5) + 1]:
        labels.append(f"{cls} 0.5 0.5 0.1 0.1")
    (export / split / "labels" / f"img_{i}.txt").write_text("\n".join(labels) + "\n")

print("=== 1. convert ===")
r = subprocess.run([PY, str(REPOS / "data-pipeline/scripts/convert_to_yolo_obb.py"),
                    "--input", str(BASE / "raw"), "--output", str(BASE / "follicle-obb-v0.1")],
                   capture_output=True, text=True)
print(r.stdout, r.stderr)
assert (BASE / "follicle-obb-v0.1" / "dataset.yaml").exists(), "conversion produced no dataset.yaml"

print("=== 2. validate clean release (expect PASS) ===")
r = subprocess.run([PY, str(REPOS / "data-pipeline/scripts/validate_dataset.py"),
                    "--path", str(BASE / "follicle-obb-v0.1")], capture_output=True, text=True)
print(r.stdout, r.stderr)
assert r.returncode in (0, 2), f"validator crashed: rc={r.returncode}"

print("=== 3. break a label (expect FAIL, rc=1) ===")
lbl = next((BASE / "follicle-obb-v0.1" / "labels" / "train").glob("*.txt"))
lbl.write_text("9 0.5 0.5 5.0 0.1\nnot-a-label\n")  # out-of-range class + malformed line
r = subprocess.run([PY, str(REPOS / "data-pipeline/scripts/validate_dataset.py"),
                    "--path", str(BASE / "follicle-obb-v0.1")], capture_output=True, text=True)
print(r.stdout[-800:], r.stderr)
assert r.returncode == 1, "validator should fail on bad labels"

print("=== 4. core.py plan simulation + chart (no TF needed) ===")
sys.path.insert(0, str(REPOS / "scalp-analyzer"))
import core  # noqa: E402

bands = [
    {"name": "anterior", "count": 12, "fu1_share": 0.5, "area_cm2": 45.0, "density": 8.0},
    {"name": "middle", "count": 60, "fu1_share": 0.3, "area_cm2": 45.0, "density": 40.0},
    {"name": "posterior", "count": 90, "fu1_share": 0.2, "area_cm2": 40.0, "density": 75.0},
]
rows, capacity, note, demand = core.plan_simulation(bands, density_per_cm2=45.0, scale_known=True, total_fu=162)
print("capacity:", capacity, "| demand:", demand, "| note:", note)
for row in rows:
    print(" ", row)
assert sum(r["grafts_allocated"] for r in rows) <= capacity, "allocation exceeded donor capacity"
chart = core._bar_chart(rows)
assert chart.size[0] == 640
chart.save(BASE / "plan_chart.png")
print("chart saved:", chart.size)

print("\nALL PIPELINE SMOKE TESTS PASSED")
