from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models import ProcessStage, DocumentCategory, TemperatureMode, TestProcessStatus

# Cac schema *Out doc thang tu doi tuong SQLAlchemy
ORM_CONFIG = ConfigDict(from_attributes=True)


# ---------- Customer ----------
class CustomerFieldProductOut(BaseModel):
    id: int
    product_code_text: Optional[str] = None
    company_product_id: Optional[int] = None
    model_config = ORM_CONFIG


class CustomerFieldOut(BaseModel):
    id: int
    field_name: str
    products: List[CustomerFieldProductOut] = []
    model_config = ORM_CONFIG


class CustomerFieldIn(BaseModel):
    field_name: str
    product_codes: List[str] = []  # se tu map sang company_products neu trung ma


class CustomerBase(BaseModel):
    name: str
    address: Optional[str] = None
    note: Optional[str] = None


class CustomerCreate(CustomerBase):
    fields: List[CustomerFieldIn] = []


class CustomerUpdate(CustomerBase):
    fields: List[CustomerFieldIn] = []


class CustomerOut(CustomerBase):
    id: int
    fields: List[CustomerFieldOut] = []
    model_config = ORM_CONFIG


# ---------- Company Product ----------
class CompanyProductComponentBase(BaseModel):
    component: Optional[str] = None     # "CHB-89A", "pH", "Nhiet do"
    standard: Optional[str] = None      # "100 ml/L"
    spec_range: Optional[str] = None    # "80-120 ml/L"


class CompanyProductComponentOut(CompanyProductComponentBase):
    id: int
    model_config = ORM_CONFIG


class CompanyProductBase(BaseModel):
    code: str
    name: str
    field: Optional[str] = None
    usage_purpose: Optional[str] = None
    process_stage: Optional[ProcessStage] = None
    price: Optional[float] = None

    # O chon de trong gui len "" chu khong phai null; coi nhu chua chon thay vi
    # bat nguoi dung phai chon mot cong doan.
    @field_validator("process_stage", mode="before")
    @classmethod
    def _blank_stage_is_none(cls, value):
        return None if value == "" else value


class CompanyProductWrite(CompanyProductBase):
    components: List[CompanyProductComponentBase] = []


class CompanyProductCreate(CompanyProductWrite):
    pass


class CompanyProductUpdate(CompanyProductWrite):
    pass


class CompanyProductOut(CompanyProductBase):
    id: int
    components: List[CompanyProductComponentOut] = []
    model_config = ORM_CONFIG


# ---------- Lab Chemical ----------
class LabChemicalBase(BaseModel):
    code: str
    name: str
    type: Optional[str] = None
    box_count: float = 0
    volume_per_box: Optional[float] = None
    unit: Optional[str] = None
    note: Optional[str] = None


class LabChemicalCreate(LabChemicalBase):
    remaining_volume: Optional[float] = None


class LabChemicalUpdate(LabChemicalBase):
    remaining_volume: Optional[float] = None


class LabChemicalOut(LabChemicalBase):
    id: int
    total_volume: Optional[float] = None
    remaining_volume: Optional[float] = None
    model_config = ORM_CONFIG


# ---------- Indicator (Chat chi thi) ----------
class IndicatorBase(BaseModel):
    name: str
    type: Optional[str] = None
    quantity: float = 0
    unit: Optional[str] = None
    note: Optional[str] = None


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorUpdate(IndicatorBase):
    pass


class IndicatorOut(IndicatorBase):
    id: int
    model_config = ORM_CONFIG


# ---------- Equipment ----------
class EquipmentVariantIn(BaseModel):
    classification: Optional[str] = None
    quantity: float = 0
    unit: Optional[str] = None
    note: Optional[str] = None


class EquipmentVariantOut(EquipmentVariantIn):
    id: int
    model_config = ORM_CONFIG


class EquipmentBase(BaseModel):
    name: str
    note: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    variants: List[EquipmentVariantIn] = []


class EquipmentUpdate(EquipmentBase):
    variants: List[EquipmentVariantIn] = []


class EquipmentOut(EquipmentBase):
    id: int
    variants: List[EquipmentVariantOut] = []
    model_config = ORM_CONFIG


# ---------- Chemical Order ----------
class ChemicalOrderBase(BaseModel):
    lab_chemical_id: int
    customer_id: int
    product_name: Optional[str] = None
    concentration: Optional[str] = None
    amount: Optional[str] = None
    order_quantity: Optional[str] = None
    used_amount: float
    unit: Optional[str] = None
    mix_date: Optional[date] = None
    issue_date: Optional[date] = None
    note: Optional[str] = None


class ChemicalOrderCreate(ChemicalOrderBase):
    pass


class ChemicalOrderUpdate(ChemicalOrderBase):
    pass


class ChemicalOrderOut(ChemicalOrderBase):
    id: int
    model_config = ORM_CONFIG


# ---------- Chemical Sampling ----------
class ChemicalSamplingBase(BaseModel):
    company_product_id: int
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    sample_date: Optional[date] = None
    note: Optional[str] = None


class ChemicalSamplingCreate(ChemicalSamplingBase):
    pass


class ChemicalSamplingUpdate(ChemicalSamplingBase):
    pass


class ChemicalSamplingOut(ChemicalSamplingBase):
    id: int
    model_config = ORM_CONFIG


# ---------- Analysis Report (Bao cao phan tich) ----------
class AnalysisComponentIn(BaseModel):
    name: str
    result: Optional[str] = None
    note: Optional[str] = None


class AnalysisComponentOut(AnalysisComponentIn):
    id: int
    model_config = ORM_CONFIG


class AnalysisSampleIn(BaseModel):
    name: str
    components: List[AnalysisComponentIn] = []


class AnalysisSampleOut(BaseModel):
    id: int
    name: str
    components: List[AnalysisComponentOut] = []
    model_config = ORM_CONFIG


class AnalysisReportBase(BaseModel):
    customer_id: int
    sample_receive_date: Optional[date] = None
    issue_date: Optional[date] = None
    approved_by: Optional[str] = None   # nguoi duyet - chi 1 nguoi
    note: Optional[str] = None


class AnalysisReportCreate(AnalysisReportBase):
    completed_by: List[str] = []   # nhieu NV phan tich
    samples: List[AnalysisSampleIn] = []


class AnalysisReportUpdate(AnalysisReportBase):
    completed_by: List[str] = []
    samples: List[AnalysisSampleIn] = []


class AnalysisReportOut(AnalysisReportBase):
    id: int
    completed_by: List[str] = []
    samples: List[AnalysisSampleOut] = []
    model_config = ORM_CONFIG


# ---------- Work Log (Nhat ky cong tac) ----------
class WorkLogBase(BaseModel):
    log_date: Optional[date] = None
    content: str
    ot_hours: Optional[float] = None


class WorkLogCreate(WorkLogBase):
    pass


class WorkLogUpdate(WorkLogBase):
    pass


class WorkLogOut(WorkLogBase):
    id: int
    model_config = ORM_CONFIG


# ---------- Document (Tai lieu) ----------
class DocumentOut(BaseModel):
    id: int
    category: DocumentCategory
    name: str
    original_filename: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_by: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    model_config = ORM_CONFIG


# ---------- Luu trinh test mau ----------
# Thong bao loi viet tieng Viet vi FE hien thang len canh o nhap.

class TestProcessStepConcentrationIn(BaseModel):
    component: Optional[str] = None
    value_min: Optional[float] = None
    value_max: Optional[float] = None
    unit: Optional[str] = None
    text_override: Optional[str] = None

    @model_validator(mode="after")
    def check_range(self):
        if self.value_min is not None and self.value_max is not None and self.value_min > self.value_max:
            raise ValueError("Nồng độ: giá trị đầu phải nhỏ hơn hoặc bằng giá trị cuối")
        return self


class TestProcessStepChemicalIn(BaseModel):
    product_id: Optional[int] = None
    lab_chemical_id: Optional[int] = None
    display_name: str

    @field_validator("display_name")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise ValueError("Tên hóa chất không được để trống")
        return value

    @model_validator(mode="after")
    def only_one_source(self):
        if self.product_id is not None and self.lab_chemical_id is not None:
            raise ValueError("Một hóa chất chỉ trỏ tới sản phẩm công ty hoặc hóa chất PTN, không được cả hai")
        return self


class TestProcessStepIn(BaseModel):
    operation: str
    time_min: Optional[float] = None
    time_max: Optional[float] = None
    time_unit: Optional[str] = None
    temp_mode: TemperatureMode = TemperatureMode.none
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    ph_min: Optional[float] = Field(default=None, ge=0, le=14)
    ph_max: Optional[float] = Field(default=None, ge=0, le=14)
    time_text: Optional[str] = None
    temp_text: Optional[str] = None
    ph_text: Optional[str] = None
    note: Optional[str] = None
    concentrations: List[TestProcessStepConcentrationIn] = []
    chemicals: List[TestProcessStepChemicalIn] = []

    @field_validator("operation")
    @classmethod
    def operation_required(cls, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise ValueError("Hạng mục không được để trống")
        return value

    @field_validator("time_unit")
    @classmethod
    def known_time_unit(cls, value):
        if value and value not in ("sec", "min", "hour"):
            raise ValueError("Đơn vị thời gian phải là sec, min hoặc hour")
        return value

    @model_validator(mode="after")
    def check_ranges(self):
        for low, high, label in (
            (self.time_min, self.time_max, "Thời gian"),
            (self.temp_min, self.temp_max, "Nhiệt độ"),
            (self.ph_min, self.ph_max, "pH"),
        ):
            if low is not None and high is not None and low > high:
                raise ValueError(f"{label}: giá trị đầu phải nhỏ hơn hoặc bằng giá trị cuối")
        return self


class TestProcessBase(BaseModel):
    customer_id: Optional[int] = None
    customer_name: str
    requirement: Optional[str] = None
    sample_quantity: int = Field(default=1, gt=0)
    test_month: date
    prepared_by: Optional[str] = None
    status: TestProcessStatus = TestProcessStatus.draft
    internal_note: Optional[str] = None

    @field_validator("customer_name")
    @classmethod
    def customer_required(cls, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise ValueError("Tên khách hàng không được để trống")
        return value

    @field_validator("test_month")
    @classmethod
    def first_of_month(cls, value: date) -> date:
        return value.replace(day=1)   # luon luu ngay 01 cua thang


class TestProcessWrite(TestProcessBase):
    steps: List[TestProcessStepIn]

    @field_validator("steps")
    @classmethod
    def at_least_one_step(cls, value):
        if not value:
            raise ValueError("Lưu trình phải có ít nhất 1 bước")
        return value


class TestProcessCreate(TestProcessWrite):
    pass


class TestProcessUpdate(TestProcessWrite):
    pass


class TestProcessStatusIn(BaseModel):
    status: TestProcessStatus


class TestProcessStepConcentrationOut(BaseModel):
    id: int
    position: int
    component: Optional[str] = None
    value_min: Optional[float] = None
    value_max: Optional[float] = None
    unit: Optional[str] = None
    text_override: Optional[str] = None
    model_config = ORM_CONFIG


class TestProcessStepChemicalOut(BaseModel):
    id: int
    position: int
    product_id: Optional[int] = None
    lab_chemical_id: Optional[int] = None
    display_name: str
    model_config = ORM_CONFIG


class TestProcessStepOut(BaseModel):
    id: int
    position: int
    operation: str
    time_min: Optional[float] = None
    time_max: Optional[float] = None
    time_unit: Optional[str] = None
    temp_mode: str
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    ph_min: Optional[float] = None
    ph_max: Optional[float] = None
    time_text: Optional[str] = None
    temp_text: Optional[str] = None
    ph_text: Optional[str] = None
    note: Optional[str] = None
    concentrations: List[TestProcessStepConcentrationOut] = []
    chemicals: List[TestProcessStepChemicalOut] = []
    # Chu in san cua buoc nay (da qua formatter, co the chua <sub>/<sup>)
    display: Optional[dict[str, Any]] = None
    model_config = ORM_CONFIG


class TestProcessDetailOut(BaseModel):
    id: int
    code: str
    customer_id: Optional[int] = None
    customer_name: str
    requirement: Optional[str] = None
    sample_quantity: int
    test_month: date
    prepared_by: Optional[str] = None
    status: str
    internal_note: Optional[str] = None
    source_process_id: Optional[int] = None
    source_process_code: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    steps: List[TestProcessStepOut] = []
    model_config = ORM_CONFIG


class TestProcessListItem(BaseModel):
    id: int
    code: str
    customer_name: str
    requirement: Optional[str] = None
    sample_quantity: int
    test_month: date
    prepared_by: Optional[str] = None
    status: str
    step_count: int = 0
    chemical_names: List[str] = []   # toi da 5 ten, giu nguyen chu hoa/thuong, da bo ky hieu _ ^
    chemical_count: int = 0
    updated_at: Optional[datetime] = None
    model_config = ORM_CONFIG


class TestProcessPage(BaseModel):
    items: List[TestProcessListItem]
    total: int
    page: int
    page_size: int


class LastStepOut(BaseModel):
    """Thong so cua lan gan nhat dung mot hang muc (nut "Dien theo lan gan nhat")."""
    found: bool
    step: Optional[TestProcessStepIn] = None


class SaveAsTemplateIn(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_required(cls, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise ValueError("Tên quy trình chuẩn không được để trống")
        return value


# ---------- Quy trinh chuan ----------
class ProcessTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[TestProcessStepIn] = []

    @field_validator("name")
    @classmethod
    def name_required(cls, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise ValueError("Tên quy trình chuẩn không được để trống")
        return value


class ProcessTemplateCreate(ProcessTemplateBase):
    pass


class ProcessTemplateUpdate(ProcessTemplateBase):
    pass


class ProcessTemplateOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    steps: List[dict[str, Any]] = []
    step_count: int = 0
    operations: List[str] = []   # ten cac buoc, de hien chip tren trang danh sach
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ORM_CONFIG


# ---------- Letterhead ----------
class CompanyProfileBase(BaseModel):
    name_zh: Optional[str] = None
    name_en: Optional[str] = None
    address_zh: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None


class CompanyProfileUpdate(CompanyProfileBase):
    pass


class CompanyProfileOut(CompanyProfileBase):
    id: int
    logo_path: Optional[str] = None
    logo_url: Optional[str] = None
    model_config = ORM_CONFIG
