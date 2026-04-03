import os
import sys
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db, Base, engine
from ..models.schema import (
    DataSource, Product, Supplier, ProductSupplier, Inventory,
    SalesHistory, PurchaseOrder, PurchaseOrderItem, DemandForecast,
    RiskEvent, WeatherData,
)

router = APIRouter(prefix="/data-sources", tags=["Data Manager"])

_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DB_DIR = _ROOT / "database"
sys.path.insert(0, str(_DB_DIR))
sys.path.insert(0, str(_ROOT))


def _counts(db: Session) -> dict:
    return {
        "products": db.query(Product).count(),
        "sales": db.query(SalesHistory).count(),
        "suppliers": db.query(Supplier).count(),
        "risk_events": db.query(RiskEvent).count(),
        "forecasts": db.query(DemandForecast).count(),
        "purchase_orders": db.query(PurchaseOrder).count(),
    }


def _wipe_all(db: Session) -> None:
    db.query(PurchaseOrderItem).delete()
    db.query(PurchaseOrder).delete()
    db.query(DemandForecast).delete()
    db.query(SalesHistory).delete()
    db.query(Inventory).delete()
    db.query(ProductSupplier).delete()
    db.query(Product).delete()
    db.query(Supplier).delete()
    db.query(RiskEvent).delete()
    db.query(WeatherData).delete()
    db.flush()


def _deactivate_all(db: Session) -> None:
    db.query(DataSource).update({"is_active": False})
    db.flush()


@router.get("")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(DataSource).order_by(DataSource.loaded_at.desc()).all()
    result = []
    for s in sources:
        result.append({
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "source_file": s.source_file,
            "product_count": s.product_count,
            "sales_count": s.sales_count,
            "is_active": s.is_active,
            "loaded_at": s.loaded_at.isoformat() if s.loaded_at else None,
        })
    return result


@router.get("/active")
def active_source(db: Session = Depends(get_db)):
    s = db.query(DataSource).filter(DataSource.is_active == True).first()
    if not s:
        return {"active": None, "counts": _counts(db)}
    return {
        "active": {
            "id": s.id, "name": s.name, "source_type": s.source_type,
            "source_file": s.source_file,
            "product_count": s.product_count, "sales_count": s.sales_count,
            "loaded_at": s.loaded_at.isoformat() if s.loaded_at else None,
        },
        "counts": _counts(db),
    }


@router.post("/load-seed")
def load_seed(db: Session = Depends(get_db)):
    Base.metadata.create_all(bind=engine)
    _wipe_all(db)
    _deactivate_all(db)
    db.commit()

    import seed_data
    seed_data.seed()

    db2 = db
    counts = _counts(db2)
    ds = DataSource(
        name="Built-in Synthetic Seed",
        source_type="synthetic",
        source_file=None,
        product_count=counts["products"],
        sales_count=counts["sales"],
        is_active=True,
    )
    db2.add(ds)
    db2.commit()
    db2.refresh(ds)
    return {"message": "Synthetic seed loaded", "id": ds.id, "counts": counts}


@router.post("/load-farming")
def load_farming(db: Session = Depends(get_db)):
    """Load the farming/crops dataset with mixed stock levels + agri risks."""
    Base.metadata.create_all(bind=engine)

    import seed_farming
    seed_farming.seed_farming()

    counts = _counts(db)
    _deactivate_all(db)
    ds = DataSource(
        name="Farming Crops Dataset",
        source_type="synthetic_farming",
        source_file=None,
        product_count=counts["products"],
        sales_count=counts["sales"],
        is_active=True,
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return {"message": "Farming crops dataset loaded", "id": ds.id, "counts": counts}


@router.post("/load-csv")
async def load_csv(
    file: UploadFile = File(...),
    max_products: int = Query(default=0, description="0 = all products"),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Please upload a .csv file")

    content = await file.read()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=tempfile.gettempdir())
    try:
        tmp.write(content)
        tmp.close()

        import import_kaggle_retail as _retail
        mp = max_products if max_products > 0 else None
        try:
            _retail.import_csv(Path(tmp.name), max_products=mp)
        except HTTPException:
            raise
        except ValueError as e:
            # User-facing validation errors (format mismatch, missing columns, parse problems)
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"CSV import failed: {e}",
            ) from e

        counts = _counts(db)
        _deactivate_all(db)
        ds = DataSource(
            name=f"Kaggle CSV: {file.filename}",
            source_type="kaggle_csv",
            source_file=file.filename,
            product_count=counts["products"],
            sales_count=counts["sales"],
            is_active=True,
        )
        db.add(ds)
        db.commit()
        db.refresh(ds)
        return {"message": f"CSV '{file.filename}' imported", "id": ds.id, "counts": counts}
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)


@router.post("/load-kaggle")
def load_kaggle(
    preset: str = Query(
        default="superstore",
        description="Known preset: superstore or online-retail",
    ),
    dataset: str | None = Query(
        default=None,
        description="Optional Kaggle slug owner/name to override preset",
    ),
    max_products: int = Query(default=0, description="0 = all products"),
    db: Session = Depends(get_db),
):
    # Importing Kaggle data can take a while, so keep the API response simple.
    import kagglehub

    import import_kaggle_retail as _retail
    import fetch_superstore_kagglehub as _kaggle_hub

    Base.metadata.create_all(bind=engine)

    if preset not in _kaggle_hub.PRESETS:
        raise HTTPException(status_code=400, detail=f"Unknown preset '{preset}'")

    slug = dataset.strip() if dataset else _kaggle_hub.PRESETS[preset]
    preset_key = preset if not dataset else "custom"
    mp = max_products if max_products > 0 else None

    # Deactivate old sources; import_csv() will clear and recreate product/sales/inventory tables.
    _deactivate_all(db)

    try:
        path = kagglehub.dataset_download(slug)
        root = Path(path)
        csv_path = _kaggle_hub._pick_csv(root, preset_key)
        _retail.import_csv(csv_path, max_products=mp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kaggle import failed: {e}") from e

    counts = _counts(db)
    ds = DataSource(
        name=f"Kaggle preset: {preset if not dataset else dataset}",
        source_type="kaggle",
        source_file=slug,
        product_count=counts["products"],
        sales_count=counts["sales"],
        is_active=True,
    )
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return {"message": "Kaggle data imported", "id": ds.id, "counts": counts}


@router.post("/{source_id}/activate")
def activate_source(source_id: int, db: Session = Depends(get_db)):
    ds = db.query(DataSource).get(source_id)
    if not ds:
        raise HTTPException(404, "Data source not found")
    _deactivate_all(db)
    ds.is_active = True
    db.commit()
    return {"message": f"'{ds.name}' marked active", "id": ds.id}


@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    ds = db.query(DataSource).get(source_id)
    if not ds:
        raise HTTPException(404, "Data source not found")

    was_active = ds.is_active
    db.delete(ds)
    db.flush()

    if was_active:
        _wipe_all(db)
    db.commit()

    remaining = db.query(DataSource).count()
    return {
        "message": f"'{ds.name}' deleted" + (" — all data wiped" if was_active else ""),
        "remaining_sources": remaining,
        "counts": _counts(db),
    }


@router.delete("")
def delete_all_sources(db: Session = Depends(get_db)):
    _wipe_all(db)
    db.query(DataSource).delete()
    db.commit()
    return {"message": "All data sources and data deleted", "counts": _counts(db)}
