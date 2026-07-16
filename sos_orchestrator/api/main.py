from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.models import Turbine, BladePatch, FleetTask
from digital_twin.paris_rul import ParisLawParameters, rul_days
from digital_twin.evoc import EVOCInputs, evoc_score

app = FastAPI(title="WindFarm SoS Operations API", version="1.0.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/turbines")
def list_turbines(db: Session = Depends(get_db)):
    rows = db.query(Turbine).all()
    return [
        {
            "id": str(r.id),
            "turbine_code": r.turbine_code,
            "name": r.name,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "blade_length_m": r.blade_length_m,
            "hub_height_m": r.hub_height_m,
        }
        for r in rows
    ]


@app.get("/patches")
def list_patches(db: Session = Depends(get_db)):
    rows = db.query(BladePatch).limit(500).all()
    return [
        {
            "id": str(r.id),
            "turbine_id": str(r.turbine_id),
            "blade_index": r.blade_index,
            "chord_pos": r.chord_pos,
            "span_pos": r.span_pos,
            "defect_class": r.defect_class,
            "severity": r.severity,
            "rul_days": r.rul_days,
            "recommendation": r.recommendation,
        }
        for r in rows
    ]


@app.post("/rul/estimate")
def estimate_rul(payload: dict):
    params = ParisLawParameters(
        C=payload["C"],
        m=payload["m"],
        Y=payload["Y"],
        delta_sigma=payload["delta_sigma"],
        k_ic=payload["k_ic"],
        sigma_max=payload["sigma_max"],
    )
    result = rul_days(
        a0=payload["a0"],
        params=params,
        cycles_per_day=payload.get("cycles_per_day", 1e5),
    )
    return result.__dict__


@app.post("/decision/evoc")
def estimate_evoc(payload: dict):
    result = evoc_score(EVOCInputs(**payload))
    return {"evoc": result, "dispatch_contact_scan": result > 0.0}


@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    rows = db.query(FleetTask).limit(500).all()
    return [
        {
            "id": str(r.id),
            "task_type": r.task_type,
            "robot_id": r.robot_id,
            "reward": r.reward,
            "execution_cost": r.execution_cost,
            "utility": r.utility,
            "state": r.state,
        }
        for r in rows
    ]
