# Part C：XR 場景物件管理 API 系統規格書

## 1. 系統概述
本 API 提供 XR 應用程式管理 3D 場景物件的後端服務，支援新增、查詢、更新與刪除 3D 物件，並透過 Pydantic 進行嚴格輸入驗證與 SQLite 持久化儲存。

## 2. 資料模型（3D Object）

| 欄位名稱 | 型別 | 必填 | 說明與驗證規則 |
| :--- | :--- | :---: | :--- |
| `id` | `integer` | 自動產生 | 物件唯一識別碼（主鍵） |
| `name` | `string` | ✔ | 物件名稱，去除前後空白後長度 `1 ~ 100` 字元 |
| `model_url` | `string` | ✔ | 3D 模型網址（如 `.glb` / `.gltf`），必須為合法 `http://` 或 `https://` URL |
| `position` | `Vector3` | 選填 | 世界座標 `{x, y, z}`，預設 `{0.0, 0.0, 0.0}`，不可為 `NaN` / `Infinity` |
| `rotation` | `Vector3` | 選填 | 歐拉角旋轉 `{x, y, z}`（度數），預設 `{0.0, 0.0, 0.0}` |
| `scale` | `Vector3` | 選填 | 縮放倍率 `{x, y, z}`，預設 `{1.0, 1.0, 1.0}`，各軸必須 `> 0` |
| `created_at` | `string` | 自動產生 | ISO 8601 建立時間 |
| `updated_at` | `string` | 自動產生 | ISO 8601 最後更新時間 |

## 3. API 端點規格

| 方法 | 路徑 | 功能說明 | 成功狀態碼 | 錯誤狀態碼 |
| :--- | :--- | :--- | :---: | :---: |
| `GET` | `/health` | 健康檢查 | `200 OK` | - |
| `GET` | `/objects` | 取得所有 3D 物件列表 | `200 OK` | - |
| `GET` | `/objects/{object_id}` | 依 ID 取得單一 3D 物件 | `200 OK` | `404 Not Found` |
| `POST` | `/objects` | 新增 3D 物件 | `201 Created` | `422 Unprocessable Entity` |
| `PUT` | `/objects/{object_id}` | 更新指定 ID 的 3D 物件 | `200 OK` | `404 Not Found`, `422 Unprocessable Entity` |
| `DELETE` | `/objects/{object_id}` | 刪除指定 ID 的 3D 物件 | `200 OK` | `404 Not Found` |
