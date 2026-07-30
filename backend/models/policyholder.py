from pydantic import BaseModel
from typing import Optional
from datetime import date


class PolicyholderCreateRequest(BaseModel):
    nama_lengkap: str
    no_ktp: str
    tanggal_lahir: Optional[date] = None
    jenis_kelamin: Optional[str] = None  # L / P
    alamat: Optional[str] = None
    no_telepon: Optional[str] = None
    email: Optional[str] = None
    tanggal_daftar: Optional[date] = None
