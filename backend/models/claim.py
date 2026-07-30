from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class LineItemRequest(BaseModel):
    item_no: int
    deskripsi: str
    kode: Optional[str] = None
    biaya: float
    catatan: Optional[str] = None


class ClaimSubmitRequest(BaseModel):
    policy_id: str
    patient_id: str
    patient_name: str
    tanggal_kejadian: date
    tanggal_pengajuan: date
    jenis_layanan: str  # RAWAT_INAP / RAWAT_JALAN / EMERGENCY
    nama_provider: str
    diagnosis_awal: Optional[str] = None
    line_items: list[LineItemRequest]


class ClaimResponse(BaseModel):
    claim_id: str
    policy_id: str
    patient_id: str
    patient_name: str
    tanggal_kejadian: date
    tanggal_pengajuan: date
    jenis_layanan: str
    nama_provider: str
    diagnosis_awal: Optional[str] = None
    status: str
    total_amount: float
    approved_amount: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LineItemResponse(BaseModel):
    line_item_id: int
    claim_id: str
    item_no: int
    deskripsi_tindakan: str
    kode_tindakan: Optional[str] = None
    jumlah_biaya: float
    catatan_tambahan: Optional[str] = None


class ClaimDetailResponse(BaseModel):
    claim: ClaimResponse
    line_items: list[LineItemResponse]
    documents: list[dict] = []


class ApiResponse(BaseModel):
    status: str
    data: Optional[dict | list] = None
    message: Optional[str] = None
