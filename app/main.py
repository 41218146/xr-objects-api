"""FastAPI 主程式：XR 場景物件管理 CRUD API。"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import database
from app.schemas import XRObjectCreate, XRObjectResponse, XRObjectUpdate

logger = logging.getLogger("xr_objects_api")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """應用程式啟動時初始化資料表。"""
    database.init_db()
    yield


app = FastAPI(
    title="XR 場景物件管理 API",
    description="使用 OpenCode Agent + Subagent 團隊開發的 XR 3D 物件後端管理服務",
    version="1.0.0",
    lifespan=lifespan,
)

# A01/A05: 限制 CORS 來源（本地開發與 WebXR 預覽用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """加入基礎安全標頭（OWASP A05）。"""
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("未預期的伺服器錯誤")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """健康檢查端點。"""
    return {"status": "ok"}


@app.get("/objects", response_model=list[XRObjectResponse], tags=["XR Objects"])
def get_all_objects() -> list[dict]:
    """取得場景中所有 3D 物件。"""
    return database.list_objects()


@app.get("/objects/{object_id}", response_model=XRObjectResponse, tags=["XR Objects"])
def get_single_object(object_id: int) -> dict:
    """依 ID 取得單一 3D 物件。"""
    obj = database.get_object_by_id(object_id)
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到 ID 為 {object_id} 的 3D 物件",
        )
    return obj


@app.post(
    "/objects",
    response_model=XRObjectResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["XR Objects"],
)
def create_xr_object(payload: XRObjectCreate) -> dict:
    """新增 3D 物件至場景。"""
    created = database.create_object(payload.model_dump())
    logger.info("新增 3D 物件成功: id=%s name=%s", created["id"], created["name"])
    return created


@app.put("/objects/{object_id}", response_model=XRObjectResponse, tags=["XR Objects"])
def update_xr_object(object_id: int, payload: XRObjectUpdate) -> dict:
    """更新指定 ID 的 3D 物件。"""
    updated = database.update_object(object_id, payload.model_dump())
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到 ID 為 {object_id} 的 3D 物件",
        )
    logger.info("更新 3D 物件成功: id=%s", object_id)
    return updated


@app.delete("/objects/{object_id}", tags=["XR Objects"])
def delete_xr_object(object_id: int) -> dict[str, str]:
    """刪除指定 ID 的 3D 物件。"""
    deleted = database.delete_object(object_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"找不到 ID 為 {object_id} 的 3D 物件",
        )
    logger.info("刪除 3D 物件成功: id=%s", object_id)
    return {"message": f"已刪除 ID 為 {object_id} 的 3D 物件"}
