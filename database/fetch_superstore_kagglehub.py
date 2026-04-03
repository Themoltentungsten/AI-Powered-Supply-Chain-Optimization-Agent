# ═══════════════════════════════════════════════════════════════════════
#  Download a retail Kaggle dataset via Kaggle Hub, then import into the DB.
#
#  Setup (one-time):
#    pip install kagglehub
#    Configure Kaggle API credentials (same as Kaggle CLI), e.g.:
#      • ~/.kaggle/kaggle.json with "username" and "key"
#      • env: KAGGLE_USERNAME + KAGGLE_KEY
#
#  Run from project root:
#    python database/fetch_superstore_kagglehub.py
#    python database/fetch_superstore_kagglehub.py --preset online-retail
#    python database/fetch_superstore_kagglehub.py --dataset owner/slug --max-products 80
#
#  See: https://github.com/Kaggle/kaggle-api/blob/main/docs/README.md
# ═══════════════════════════════════════════════════════════════════════

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_DATABASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_DATABASE_DIR))

import kagglehub

import import_kaggle_retail as _import_retail

PRESETS: dict[str, str] = {
    "superstore": "aditisaxena20/superstore-sales-dataset",
    "online-retail": "mathchi/online-retail-data-set-from-ml-repository",
}


def _pick_csv(root: Path, preset: str) -> Path:
    csvs = list(root.rglob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No .csv files under {root}")

    def biggest(paths: list[Path]) -> Path:
        return max(paths, key=lambda p: p.stat().st_size)

    if preset == "superstore":
        hit = [p for p in csvs if "superstore" in p.name.lower()]
        return biggest(hit) if hit else biggest(csvs)

    if preset == "online-retail":
        for key in ("online", "retail", "data"):
            hit = [p for p in csvs if key in p.name.lower()]
            if len(hit) == 1:
                return hit[0]
            if len(hit) > 1:
                return biggest(hit)
        return biggest(csvs)

    # --dataset override or unknown preset: pick best guess
    if preset == "custom":
        for hint in ("superstore", "online", "retail"):
            hit = [p for p in csvs if hint in p.name.lower()]
            if hit:
                return biggest(hit)
        return biggest(csvs)

    return biggest(csvs)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Download a Kaggle retail CSV via kagglehub and import into supply_chain DB.",
    )
    ap.add_argument(
        "--preset",
        choices=list(PRESETS),
        default="superstore",
        help="Which known dataset to download (default: superstore).",
    )
    ap.add_argument(
        "--dataset",
        default=None,
        help="Full Kaggle slug owner/name — overrides --preset if set.",
    )
    ap.add_argument(
        "--max-products",
        type=int,
        default=None,
        help="Top N products by volume (smaller DB for demos).",
    )
    args = ap.parse_args()

    slug = args.dataset.strip() if args.dataset else PRESETS[args.preset]
    preset_key = args.preset if not args.dataset else "custom"

    print(f"Downloading via kagglehub: {slug} …")
    path = kagglehub.dataset_download(slug)
    root = Path(path)
    print("Path to dataset files:", root)

    csv_path = _pick_csv(root, preset_key)
    print("Using CSV:", csv_path)

    _import_retail.import_csv(csv_path, max_products=args.max_products)


if __name__ == "__main__":
    main()
