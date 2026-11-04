"""Module ky thuat - phong thi nghiem (schema `lab`).

Khach hang va san pham cong ty nam o `common`; bang o day tro toi do.
"""
import enum

from sqlalchemy import (
    CheckConstraint, Column, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

SCHEMA = "lab"


class _InSchema:
    __table_args__ = {"schema": SCHEMA}


class LabChemical(_InSchema, Base):
    """Bang 3: HC PTN - ton kho hoa chat phong thi nghiem"""
    __tablename__ = "lab_chemicals"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100))
    box_count = Column(Float, default=0)            # So luong (co the le, vd 0.4 = 200/500)
    volume_per_box = Column(Float)                  # dung tich
    total_volume = Column(Float)                    # Nguyen = so luong * dung tich
    remaining_volume = Column(Float, default=0)     # Le - phan dang mo dung, tu dong tru
    unit = Column(String(50))
    note = Column(Text)

    orders = relationship("ChemicalOrder", back_populates="lab_chemical")


class Indicator(_InSchema, Base):
    """Chat chi thi (thuoc thu)"""
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100))
    quantity = Column(Float, default=0)
    unit = Column(String(50))
    note = Column(Text)


class Equipment(_InSchema, Base):
    """Bang 4: Thiet bi"""
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    note = Column(Text)

    variants = relationship("EquipmentVariant", back_populates="equipment", cascade="all, delete-orphan", order_by="EquipmentVariant.id")


class EquipmentVariant(_InSchema, Base):
    """Phan loai / so luong con cua tung thiet bi (vd pH co 3 dong)"""
    __tablename__ = "equipment_variants"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("lab.equipment.id", ondelete="CASCADE"), nullable=False)
    classification = Column(String(100))
    quantity = Column(Float, default=0)
    unit = Column(String(50))
    note = Column(Text)

    equipment = relationship("Equipment", back_populates="variants")


class ChemicalOrder(_InSchema, Base):
    """Bang 5: Don hang HCTN - Ma HC -> lab_chemicals, KH -> customers"""
    __tablename__ = "chemical_orders"

    id = Column(Integer, primary_key=True, index=True)
    lab_chemical_id = Column(Integer, ForeignKey("lab.lab_chemicals.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("common.customers.id"), nullable=False)
    product_name = Column(String(255))  # ten chung khi 1 don gom nhieu hoa chat (vd "pH 10")
    concentration = Column(String(100))
    amount = Column(String(100))
    order_quantity = Column(String(100))
    used_amount = Column(Float, nullable=False)
    unit = Column(String(50))
    mix_date = Column(Date)
    issue_date = Column(Date)
    note = Column(Text)

    lab_chemical = relationship("LabChemical", back_populates="orders")
    customer = relationship("Customer")


class ChemicalSampling(_InSchema, Base):
    """Bang 6: Lay mau HC - Ma HC o day thuc ra -> company_products (Bang 2)"""
    __tablename__ = "chemical_sampling"

    id = Column(Integer, primary_key=True, index=True)
    company_product_id = Column(Integer, ForeignKey("common.company_products.id"), nullable=False)
    name = Column(String(255))
    quantity = Column(Float)
    unit = Column(String(50))
    sample_date = Column(Date)
    note = Column(Text)

    company_product = relationship("CompanyProduct")


class AnalysisReport(_InSchema, Base):
    """Bao cao phan tich - KH -> customers (Bang 1). 1 bao cao co n mau pha, n NV phan tich, 1 nguoi duyet."""
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("common.customers.id"), nullable=False)
    sample_receive_date = Column(Date)   # Ngay nhan mau
    issue_date = Column(Date)            # Ngay phan tich
    approved_by = Column(String(100))    # Nguoi duyet - chi 1 nguoi
    note = Column(Text)

    samples = relationship("AnalysisSample", back_populates="report", cascade="all, delete-orphan", order_by="AnalysisSample.id")
    completed_by_entries = relationship("AnalysisCompletedBy", back_populates="report", cascade="all, delete-orphan", order_by="AnalysisCompletedBy.id")

    @property
    def completed_by(self):
        return [e.name for e in self.completed_by_entries]


class AnalysisCompletedBy(_InSchema, Base):
    """NV phan tich - 1 bao cao co the co nhieu NV phan tich"""
    __tablename__ = "analysis_completed_by"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("lab.analysis_reports.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)

    report = relationship("AnalysisReport", back_populates="completed_by_entries")


class AnalysisSample(_InSchema, Base):
    """Mau pha - 1 mau pha co n thanh phan (TP)"""
    __tablename__ = "analysis_samples"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("lab.analysis_reports.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)   # vd: Be SnO2

    report = relationship("AnalysisReport", back_populates="samples")
    components = relationship("AnalysisComponent", back_populates="sample", cascade="all, delete-orphan", order_by="AnalysisComponent.id")


class WorkLog(_InSchema, Base):
    """Nhat ky cong tac"""
    __tablename__ = "work_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date)
    content = Column(Text, nullable=False)
    ot_hours = Column(Float)  # so gio tang ca, de trong neu khong OT


class AnalysisComponent(_InSchema, Base):
    """TP (thanh phan) + KQ (ket qua) - 1 TP co 1 KQ"""
    __tablename__ = "analysis_components"

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("lab.analysis_samples.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)   # TP, vd: SnO2, Ni, pH
    result = Column(String(100))                  # KQ, vd: 3, 4, 5
    note = Column(Text)                            # Ghi chu rieng cho TP nay

    sample = relationship("AnalysisSample", back_populates="components")


class TestProcessStatus(str, enum.Enum):
    draft = "draft"               # Nhap
    in_progress = "in_progress"   # Dang test
    completed = "completed"       # Hoan thanh
    cancelled = "cancelled"       # Da huy


class TemperatureMode(str, enum.Enum):
    none = "none"         # de trong
    ambient = "ambient"   # in ra "Thuong"
    range = "range"       # in ra khoang do C, vd "20-30"


class TestProcess(Base):
    """Luu trinh test mau - 1 to phieu A4, gom n buoc."""
    __tablename__ = "test_processes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)  # LT-YYYY-NNN
    customer_id = Column(Integer, ForeignKey("common.customers.id", ondelete="SET NULL"), nullable=True, index=True)
    # Ten in tren phieu: luu rieng khoi customers de doi ten KH khong lam doi phieu da phat hanh,
    # va de nhan duoc ca KH chua co trong danh muc.
    customer_name = Column(String(255), nullable=False)
    requirement = Column(Text)
    sample_quantity = Column(Integer, nullable=False, default=1)
    test_month = Column(Date, nullable=False)          # luon la ngay 01 cua thang
    prepared_by = Column(String(100))
    status = Column(String(20), nullable=False, default=TestProcessStatus.draft.value, index=True)
    internal_note = Column(Text)                        # khong in ra phieu
    source_process_id = Column(Integer, ForeignKey("lab.test_processes.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)   # xoa mem

    __table_args__ = (
        CheckConstraint("sample_quantity > 0", name="ck_test_processes_sample_quantity_positive"),
        {"schema": SCHEMA},
    )

    customer = relationship("Customer")
    source_process = relationship("TestProcess", remote_side=[id])
    steps = relationship(
        "TestProcessStep", back_populates="process",
        cascade="all, delete-orphan", order_by="TestProcessStep.position",
    )


class TestProcessStep(Base):
    """1 buoc trong luu trinh = 1 hang cua bang tren phieu."""
    __tablename__ = "test_process_steps"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("lab.test_processes.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False)          # 1..n, cung la STT in ra
    operation = Column(String(255), nullable=False)     # Hang muc

    time_min = Column(Numeric(8, 2))
    time_max = Column(Numeric(8, 2))
    time_unit = Column(String(10))                      # sec / min / hour

    temp_mode = Column(String(10), nullable=False, default=TemperatureMode.none.value)
    temp_min = Column(Numeric(6, 1))
    temp_max = Column(Numeric(6, 1))

    ph_min = Column(Numeric(4, 2))
    ph_max = Column(Numeric(4, 2))

    # Chu in thay the cho truong hop dac biet: co gia tri thi in nguyen van,
    # bo qua cac o so o tren.
    time_text = Column(String(100))
    temp_text = Column(String(100))
    ph_text = Column(String(100))

    note = Column(Text)                                 # khong in ra phieu

    __table_args__ = (
        UniqueConstraint("process_id", "position", name="uq_test_process_steps_position"),
        CheckConstraint("ph_min IS NULL OR (ph_min >= 0 AND ph_min <= 14)", name="ck_test_process_steps_ph_min_range"),
        CheckConstraint("ph_max IS NULL OR (ph_max >= 0 AND ph_max <= 14)", name="ck_test_process_steps_ph_max_range"),
        {"schema": SCHEMA},
    )

    process = relationship("TestProcess", back_populates="steps")
    concentrations = relationship(
        "TestProcessStepConcentration", back_populates="step",
        cascade="all, delete-orphan", order_by="TestProcessStepConcentration.position",
    )
    chemicals = relationship(
        "TestProcessStepChemical", back_populates="step",
        cascade="all, delete-orphan", order_by="TestProcessStepChemical.position",
    )


class TestProcessStepConcentration(_InSchema, Base):
    """1 dong nong do trong o NONG DO. 1 buoc co 0..n dong, doc lap voi danh sach hoa chat."""
    __tablename__ = "test_process_step_concentrations"

    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("lab.test_process_steps.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    component = Column(String(50))          # "Zn^2+", "NaOH" - de trong neu la nong do cua chinh hoa chat
    value_min = Column(Numeric(10, 3))
    value_max = Column(Numeric(10, 3))
    unit = Column(String(20))               # g/l, ml/l, %, mg/l...
    text_override = Column(String(100))     # chu in thay the

    step = relationship("TestProcessStep", back_populates="concentrations")


class TestProcessStepChemical(Base):
    """1 hoa chat trong o HOA CHAT. Tro toi SP cong ty hoac HC PTN, hoac chi la chu tu do."""
    __tablename__ = "test_process_step_chemicals"

    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("lab.test_process_steps.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey("common.company_products.id", ondelete="SET NULL"), nullable=True, index=True)
    lab_chemical_id = Column(Integer, ForeignKey("lab.lab_chemicals.id", ondelete="SET NULL"), nullable=True, index=True)
    # Chu in, chot lai tai thoi diem chon: doi ten SP ve sau khong lam doi phieu da phat hanh.
    display_name = Column(String(100), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "product_id IS NULL OR lab_chemical_id IS NULL",
            name="ck_test_process_step_chemicals_single_source",
        ),
        {"schema": SCHEMA},
    )

    step = relationship("TestProcessStep", back_populates="chemicals")
    product = relationship("CompanyProduct")
    lab_chemical = relationship("LabChemical")


class ProcessTemplate(_InSchema, Base):
    """Quy trinh chuan = bo buoc dung lai. steps luu jsonb, cung cau truc voi mang steps cua API."""
    __tablename__ = "process_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    steps = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
