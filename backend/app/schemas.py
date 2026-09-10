from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

from app.models import ProcessStage, DocumentCategory


# ---------- Customer ----------
class CustomerFieldProductOut(BaseModel):
    id: int
    product_code_text: Optional[str] = None
    company_product_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class CustomerFieldOut(BaseModel):
    id: int
    field_name: str
    products: List[CustomerFieldProductOut] = []
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


# ---------- Company Product ----------
class CompanyProductBase(BaseModel):
    code: str
    name: str
    field: Optional[str] = None
    usage_purpose: Optional[str] = None
    concentration: Optional[str] = None
    unit: Optional[str] = None
    process_stage: Optional[ProcessStage] = None
    price: Optional[float] = None


class CompanyProductCreate(CompanyProductBase):
    pass


class CompanyProductUpdate(CompanyProductBase):
    pass


class CompanyProductOut(CompanyProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


# ---------- Equipment ----------
class EquipmentVariantIn(BaseModel):
    classification: Optional[str] = None
    quantity: float = 0
    unit: Optional[str] = None
    note: Optional[str] = None


class EquipmentVariantOut(EquipmentVariantIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


# ---------- Analysis Report (Bao cao phan tich) ----------
class AnalysisComponentIn(BaseModel):
    name: str
    result: Optional[str] = None
    note: Optional[str] = None


class AnalysisComponentOut(AnalysisComponentIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


class AnalysisSampleIn(BaseModel):
    name: str
    components: List[AnalysisComponentIn] = []


class AnalysisSampleOut(BaseModel):
    id: int
    name: str
    components: List[AnalysisComponentOut] = []
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


# ---------- Work Log (Nhat ky cong tac) ----------
class WorkLogBase(BaseModel):
    log_date: Optional[date] = None
    content: str


class WorkLogCreate(WorkLogBase):
    pass


class WorkLogUpdate(WorkLogBase):
    pass


class WorkLogOut(WorkLogBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)
