"""SQLite 資料庫連線與 CRUD 資料存取層（使用參數化查詢防止 SQL Injection）。"""

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "xr_objects.db"


def get_db_path() -> str:
    """取得資料庫檔案路徑，測試時可透過 XR_DB_PATH 環境變數覆寫。"""
    return os.environ.get("XR_DB_PATH", str(DEFAULT_DB_PATH))


def get_connection() -> sqlite3.Connection:
    """建立 SQLite 連線並啟用 dict-like Row 存取。"""
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """初始化 xr_objects 資料表。"""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS xr_objects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                model_url TEXT NOT NULL,
                pos_x REAL NOT NULL,
                pos_y REAL NOT NULL,
                pos_z REAL NOT NULL,
                rot_x REAL NOT NULL,
                rot_y REAL NOT NULL,
                rot_z REAL NOT NULL,
                scale_x REAL NOT NULL,
                scale_y REAL NOT NULL,
                scale_z REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "model_url": row["model_url"],
        "position": {"x": row["pos_x"], "y": row["pos_y"], "z": row["pos_z"]},
        "rotation": {"x": row["rot_x"], "y": row["rot_y"], "z": row["rot_z"]},
        "scale": {"x": row["scale_x"], "y": row["scale_y"], "z": row["scale_z"]},
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_objects() -> list[dict[str, Any]]:
    """取得所有 3D 物件。"""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM xr_objects ORDER BY id ASC").fetchall()
        return [_row_to_dict(row) for row in rows]


def get_object_by_id(object_id: int) -> dict[str, Any] | None:
    """依 ID 取得單一 3D 物件。"""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM xr_objects WHERE id = ?", (object_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None


def create_object(data: dict[str, Any]) -> dict[str, Any]:
    """新增 3D 物件並回傳完整資料。"""
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO xr_objects (
                name, model_url,
                pos_x, pos_y, pos_z,
                rot_x, rot_y, rot_z,
                scale_x, scale_y, scale_z,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data["model_url"],
                data["position"]["x"],
                data["position"]["y"],
                data["position"]["z"],
                data["rotation"]["x"],
                data["rotation"]["y"],
                data["rotation"]["z"],
                data["scale"]["x"],
                data["scale"]["y"],
                data["scale"]["z"],
                now,
                now,
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
    created = get_object_by_id(int(new_id))
    assert created is not None
    return created


def update_object(object_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
    """更新指定 ID 的 3D 物件；若不存在回傳 None。"""
    existing = get_object_by_id(object_id)
    if existing is None:
        return None
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE xr_objects
            SET name = ?, model_url = ?,
                pos_x = ?, pos_y = ?, pos_z = ?,
                rot_x = ?, rot_y = ?, rot_z = ?,
                scale_x = ?, scale_y = ?, scale_z = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                data["name"],
                data["model_url"],
                data["position"]["x"],
                data["position"]["y"],
                data["position"]["z"],
                data["rotation"]["x"],
                data["rotation"]["y"],
                data["rotation"]["z"],
                data["scale"]["x"],
                data["scale"]["y"],
                data["scale"]["z"],
                now,
                object_id,
            ),
        )
        conn.commit()
    return get_object_by_id(object_id)


def delete_object(object_id: int) -> bool:
    """刪除指定 ID 的 3D 物件，回傳是否成功刪除。"""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM xr_objects WHERE id = ?", (object_id,))
        conn.commit()
        return cursor.rowcount > 0
