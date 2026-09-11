from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import EvalRun
from app.db.schemas import EvalRunRequest, EvalRunResponse
from app.services.auth_service import get_current_user, require_admin
from app.services.eval_service import run_evaluation_suite

router = APIRouter(prefix="/evaluation", tags=["Evaluation System"])

@router.post("/run", response_model=EvalRunResponse)
def trigger_evaluation_run(
    data: EvalRunRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    eval_run = run_evaluation_suite(
        db=db,
        name=data.name or "Benchmark Run",
        collection_id=data.collection_id,
        top_k=data.top_k or 5
    )
    return eval_run

@router.get("/runs", response_model=List[EvalRunResponse])
def list_evaluation_runs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    runs = db.query(EvalRun).order_by(EvalRun.run_date.desc()).all()
    return runs

@router.get("/runs/{run_id}", response_model=EvalRunResponse)
def get_evaluation_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    run = db.query(EvalRun).filter(EvalRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return run
