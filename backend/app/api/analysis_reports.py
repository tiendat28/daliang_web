from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/analysis-reports", tags=["analysis-reports"])

_LOAD_OPTIONS = (
    joinedload(models.AnalysisReport.samples).joinedload(models.AnalysisSample.components),
    joinedload(models.AnalysisReport.completed_by_entries),
)


def _sync_samples(db: Session, report: models.AnalysisReport, samples_in):
    for s in list(report.samples):
        db.delete(s)
    db.flush()

    for s_in in samples_in:
        sample = models.AnalysisSample(report_id=report.id, name=s_in.name)
        db.add(sample)
        db.flush()
        for c_in in s_in.components:
            db.add(models.AnalysisComponent(
                sample_id=sample.id, name=c_in.name, result=c_in.result, note=c_in.note,
            ))


def _sync_completed_by(db: Session, report: models.AnalysisReport, names):
    for e in list(report.completed_by_entries):
        db.delete(e)
    db.flush()

    for name in names:
        name = name.strip()
        if not name:
            continue
        db.add(models.AnalysisCompletedBy(report_id=report.id, name=name))


@router.get("", response_model=list[schemas.AnalysisReportOut])
def list_analysis_reports(db: Session = Depends(get_db)):
    return db.query(models.AnalysisReport).options(*_LOAD_OPTIONS).all()


@router.get("/{report_id}", response_model=schemas.AnalysisReportOut)
def get_analysis_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(models.AnalysisReport).options(*_LOAD_OPTIONS).filter(
        models.AnalysisReport.id == report_id
    ).first()
    if not report:
        raise HTTPException(404, "Khong tim thay bao cao")
    return report


@router.post("", response_model=schemas.AnalysisReportOut)
def create_analysis_report(payload: schemas.AnalysisReportCreate, db: Session = Depends(get_db)):
    report = models.AnalysisReport(
        customer_id=payload.customer_id,
        sample_receive_date=payload.sample_receive_date,
        issue_date=payload.issue_date,
        approved_by=payload.approved_by,
        note=payload.note,
    )
    db.add(report)
    db.flush()
    _sync_completed_by(db, report, payload.completed_by)
    _sync_samples(db, report, payload.samples)
    db.commit()
    db.refresh(report)
    return report


@router.put("/{report_id}", response_model=schemas.AnalysisReportOut)
def update_analysis_report(report_id: int, payload: schemas.AnalysisReportUpdate, db: Session = Depends(get_db)):
    report = db.query(models.AnalysisReport).get(report_id)
    if not report:
        raise HTTPException(404, "Khong tim thay bao cao")
    report.customer_id = payload.customer_id
    report.sample_receive_date = payload.sample_receive_date
    report.issue_date = payload.issue_date
    report.approved_by = payload.approved_by
    report.note = payload.note
    _sync_completed_by(db, report, payload.completed_by)
    _sync_samples(db, report, payload.samples)
    db.commit()
    db.refresh(report)
    return report


@router.delete("/{report_id}")
def delete_analysis_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(models.AnalysisReport).get(report_id)
    if not report:
        raise HTTPException(404, "Khong tim thay bao cao")
    db.delete(report)
    db.commit()
    return {"ok": True}
