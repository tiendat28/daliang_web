from sqlalchemy.orm import Session

from app import models


def deduct_lab_chemical(db: Session, lab_chemical: models.LabChemical, amount: float) -> None:
    """Tru thang vao phan 'Le' dang dung - khong canh bao, cho phep am neu vuot ton."""
    lab_chemical.remaining_volume = (lab_chemical.remaining_volume or 0) - amount


def restore_lab_chemical(db: Session, lab_chemical: models.LabChemical, amount: float) -> None:
    """Hoan lai luong da tru khi sua/xoa don hang."""
    lab_chemical.remaining_volume = (lab_chemical.remaining_volume or 0) + amount
