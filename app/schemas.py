"""Pydantic 資料模型與輸入驗證規則。"""

import math
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


def _check_finite(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("數值不可為 NaN 或無限大")
    return value


class Vector3(BaseModel):
    """三維向量模型（用於位置、旋轉、縮放）。"""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    @field_validator("x", "y", "z")
    @classmethod
    def validate_finite(cls, v: float) -> float:
        return _check_finite(v)


class ScaleVector3(Vector3):
    """縮放向量模型，各軸倍率必須嚴格大於 0。"""

    x: float = 1.0
    y: float = 1.0
    z: float = 1.0

    @field_validator("x", "y", "z")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        _check_finite(v)
        if v <= 0:
            raise ValueError("縮放倍率必須大於 0")
        return v


class XRObjectBase(BaseModel):
    """3D 物件共用欄位與驗證。"""

    name: str = Field(..., min_length=1, max_length=100, description="3D 物件名稱")
    model_url: str = Field(..., max_length=500, description="3D 模型檔案網址")
    position: Vector3 = Field(default_factory=Vector3)
    rotation: Vector3 = Field(default_factory=Vector3)
    scale: ScaleVector3 = Field(default_factory=ScaleVector3)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("物件名稱不可為空白")
        return cleaned

    @field_validator("model_url")
    @classmethod
    def validate_model_url(cls, v: str) -> str:
        cleaned = v.strip()
        parsed = urlparse(cleaned)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("model_url 必須為合法的 http 或 https 網址")
        return cleaned


class XRObjectCreate(XRObjectBase):
    """建立 3D 物件請求模型。"""


class XRObjectUpdate(XRObjectBase):
    """更新 3D 物件請求模型。"""


class XRObjectResponse(XRObjectBase):
    """3D 物件回應模型。"""

    id: int
    created_at: str
    updated_at: str
