# 加分題：OWASP Top 10 安全審查報告（`team/security`）

本報告依據 **OWASP Top 10 (2021)** 對 `app/` 底下之 XR 場景物件管理 API 進行靜態與架構審查。

## 審查結果摘要

| OWASP 類別 | 檢查項目 | 風險狀態 | 實作防護機制 |
| :--- | :--- | :---: | :--- |
| **A01: Broken Access Control** | CORS 與資源存取控制 | 已防護 | 明確設定 `CORSMiddleware` 允許來源白名單，不無差別開放未知來源攜帶憑證。 |
| **A03: Injection** | SQL Injection | 已防護 | `app/database.py` 全面使用 SQLite 參數化查詢（`?` 佔位符），無字串拼接 SQL。 |
| **A04: Insecure Design** | 輸入驗證與 URL Scheme | 已防護 | Pydantic 限制 `name` 長度、`scale > 0`、排除 `NaN`/`Inf`，且僅允許 `http`/`https` 網址，阻擋 `javascript:` / `file:` 等危險協定。 |
| **A05: Security Misconfiguration** | 安全 HTTP 標頭與錯誤訊息 | 已防護 | Middleware 自動加入 `X-Content-Type-Options: nosniff`、`X-Frame-Options: DENY`；統一捕捉例外，不回傳內部堆疊追蹤（Stack Trace）。 |
| **A09: Security Logging** | 操作與異常紀錄 | 已防護 | 使用標準 `logging` 模組紀錄關鍵新增、更新、刪除與異常事件。 |

## 結論
API 目前已通過上述 OWASP Top 10 基礎檢查，無高風險漏洞；若未來部署至正式環境，建議再加入 JWT 身分驗證與 Rate Limiting（如 `slowapi`）。
