"""XR 場景物件管理 API 自動化測試（共 12 項測試）。"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """每個測試使用獨立的暫存 SQLite 資料庫，確保測試彼此隔離。"""
    db_file = tmp_path / "test_xr.db"
    monkeypatch.setenv("XR_DB_PATH", str(db_file))
    with TestClient(app) as test_client:
        yield test_client


def _sample_payload(**overrides):
    base = {
        "name": "Cyberpunk Chair",
        "model_url": "https://cdn.example.com/models/chair.glb",
        "position": {"x": 1.0, "y": 0.0, "z": -2.5},
        "rotation": {"x": 0.0, "y": 45.0, "z": 0.0},
        "scale": {"x": 1.0, "y": 1.0, "z": 1.0},
    }
    base.update(overrides)
    return base


def test_01_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_02_list_objects_initially_empty(client):
    res = client.get("/objects")
    assert res.status_code == 200
    assert res.json() == []


def test_03_create_object_success(client):
    res = client.post("/objects", json=_sample_payload())
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == 1
    assert data["name"] == "Cyberpunk Chair"
    assert data["position"]["z"] == -2.5


def test_04_create_object_with_defaults(client):
    res = client.post(
        "/objects",
        json={"name": "Simple Cube", "model_url": "https://example.com/cube.glb"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["position"] == {"x": 0.0, "y": 0.0, "z": 0.0}
    assert data["rotation"] == {"x": 0.0, "y": 0.0, "z": 0.0}
    assert data["scale"] == {"x": 1.0, "y": 1.0, "z": 1.0}


def test_05_get_single_object_success(client):
    created = client.post("/objects", json=_sample_payload()).json()
    res = client.get(f"/objects/{created['id']}")
    assert res.status_code == 200
    assert res.json()["name"] == "Cyberpunk Chair"


def test_06_get_nonexistent_object_returns_404(client):
    res = client.get("/objects/9999")
    assert res.status_code == 404


def test_07_update_object_success(client):
    created = client.post("/objects", json=_sample_payload()).json()
    updated_payload = _sample_payload(
        name="Updated Table",
        position={"x": 3.0, "y": 1.5, "z": 0.0},
        scale={"x": 2.0, "y": 2.0, "z": 2.0},
    )
    res = client.put(f"/objects/{created['id']}", json=updated_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Updated Table"
    assert data["position"]["x"] == 3.0
    assert data["scale"]["y"] == 2.0


def test_08_update_nonexistent_object_returns_404(client):
    res = client.put("/objects/9999", json=_sample_payload())
    assert res.status_code == 404


def test_09_delete_object_and_verify_gone(client):
    created = client.post("/objects", json=_sample_payload()).json()
    del_res = client.delete(f"/objects/{created['id']}")
    assert del_res.status_code == 200

    get_res = client.get(f"/objects/{created['id']}")
    assert get_res.status_code == 404


def test_10_delete_nonexistent_object_returns_404(client):
    res = client.delete("/objects/9999")
    assert res.status_code == 404


def test_11_validation_rejects_blank_name_and_bad_url(client):
    res_blank = client.post("/objects", json=_sample_payload(name="   "))
    assert res_blank.status_code == 422

    res_js_url = client.post("/objects", json=_sample_payload(model_url="javascript:alert(1)"))
    assert res_js_url.status_code == 422


def test_12_validation_rejects_non_positive_scale(client):
    res_zero = client.post(
        "/objects", json=_sample_payload(scale={"x": 0.0, "y": 1.0, "z": 1.0})
    )
    assert res_zero.status_code == 422

    res_neg = client.post(
        "/objects", json=_sample_payload(scale={"x": 1.0, "y": -0.5, "z": 1.0})
    )
    assert res_neg.status_code == 422


def test_13_security_headers_present(client):
    res = client.get("/health")
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
