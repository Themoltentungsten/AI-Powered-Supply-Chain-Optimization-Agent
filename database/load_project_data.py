# ═══════════════════════════════════════════════════════════════════════
#  One entry point: load data into whatever DB is in DATABASE_URL (.env)
#  — PostgreSQL (recommended) or SQLite — choose synthetic seed vs Kaggle.
#
#  Synthetic demo (10 products, generated sales, risk events):
#    python database/load_project_data.py seed
#    python database/load_project_data.py seed --replace
#
#  Kaggle (download via kagglehub + import; needs Kaggle API credentials):
#    python database/load_project_data.py kaggle
#    python database/load_project_data.py kaggle --preset online-retail
#    python database/load_project_data.py kaggle --max-products 80
#
#  CSV you already downloaded:
#    python database/load_project_data.py csv --path "C:\data\file.csv"
#
#  Ensure .env has a single DATABASE_URL=postgresql://... or sqlite:///...
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

import import_kaggle_retail as _retail
import fetch_superstore_kagglehub as _kaggle_hub


def _print_db_hint() -> None:
    try:
        from backend.app.config import get_settings

        url = get_settings().database_url
        if "postgresql" in url:
            print(f"Target database (PostgreSQL): {url.split('@')[-1] if '@' in url else url}")
        elif "sqlite" in url:
            print(f"Target database (SQLite): {url}")
        else:
            print(f"Target database: {url[:80]}…")
    except Exception as e:
        print(f"(Could not read DATABASE_URL: {e})")


def cmd_seed(replace: bool) -> None:
    _print_db_hint()
    if replace:
        from backend.app.database import SessionLocal

        session = SessionLocal()
        try:
            print("Wiping demo tables (--replace) …")
            _retail.clear_demo_data(session)
        finally:
            session.close()
    print("Loading built-in synthetic seed …")
    import seed_data as _seed

    _seed.seed()


def cmd_kaggle(preset: str, dataset: str | None, max_products: int | None) -> None:
    _print_db_hint()
    slug = dataset.strip() if dataset else _kaggle_hub.PRESETS[preset]
    preset_key = preset if not dataset else "custom"
    print(f"Downloading: {slug}")
    path = kagglehub.dataset_download(slug)
    root = Path(path)
    print("Download folder:", root)
    csv_path = _kaggle_hub._pick_csv(root, preset_key)
    print("Importing:", csv_path)
    _retail.import_csv(csv_path, max_products=max_products)


def cmd_csv(csv_path: Path, max_products: int | None) -> None:
    _print_db_hint()
    if not csv_path.is_file():
        raise SystemExit(f"Not a file: {csv_path}")
    _retail.import_csv(csv_path, max_products=max_products)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Load data into the project DB (DATABASE_URL): synthetic seed or Kaggle retail CSV.",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    p_seed = sub.add_parser("seed", help="Built-in synthetic dataset (good for Prophet demos).")
    p_seed.add_argument(
        "--replace",
        action="store_true",
        help="Delete existing demo rows first (needed if DB was already seeded or had Kaggle data).",
    )

    p_kaggle = sub.add_parser("kaggle", help="Download dataset with kagglehub, then import.")
    p_kaggle.add_argument(
        "--preset",
        choices=list(_kaggle_hub.PRESETS),
        default="superstore",
    )
    p_kaggle.add_argument("--dataset", default=None, help="Override slug: owner/dataset-name")
    p_kaggle.add_argument("--max-products", type=int, default=None)

    p_csv = sub.add_parser("csv", help="Import a local CSV (Superstore or Online Retail shape).")
    p_csv.add_argument("--path", type=Path, required=True)
    p_csv.add_argument("--max-products", type=int, default=None)

    args = ap.parse_args()

    if args.command == "seed":
        cmd_seed(replace=args.replace)
    elif args.command == "kaggle":
        cmd_kaggle(args.preset, args.dataset, args.max_products)
    elif args.command == "csv":
        cmd_csv(args.path, args.max_products)
    else:
        raise SystemExit(args.command)


if __name__ == "__main__":
    main()
