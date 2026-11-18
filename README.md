# XR 場景物件管理 API（OpenCode Agent + Subagent 作業）

本專案為「使用 Vibe Coding 方法來建立 XR 智慧後端（二）」作業實作，透過 OpenCode 的主代理（Orchestrator）與多個專業子代理（Subagent）協作完成。

---

## 一、Part A：團隊架構與權限設計表

遵循**最小權限原則（Least Privilege）**與**審查與實作分離**：

| 角色 (Agent ID) | Read | Edit | Shell | Subagent | 設計理由 |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **主 Agent (`orchestrator`)** | ✔ | ✔ | ✔ | 只限 `team/*`、`db-eval` | 擔任 Tech Lead 指揮官，負責派工與彙整結果 |
| **`team/architect`** | ✔ | 只限 `docs/**` | ✘ (`deny`) | ✘ | 僅負責系統架構與規格撰寫，防止直接修改程式碼 |
| **`team/coder`** | ✔ | 只限 `app/**`、`requirements.txt` | `ask` | ✘ | 專注後端實作，執行指令前須經確認，且不可改測試 |
| **`team/tester`** | ✔ | 只限 `tests/**` | ✔ (`allow`) | ✘ | 可撰寫並執行 `pytest`，但不可修改主程式掩蓋錯誤 |
| **`team/reviewer`** | ✔ | ✘ (`deny`) | ✘ (`deny`) | ✘ | 唯讀審查，確保 Code Review 客觀中立 |
| **`team/doc-writer`** | ✔ | 只限 `docs/**`、`README.md` | ✘ (`deny`) | ✘ | 專責文件同步與更新 |
| **`team/security`** *(加分題)* | ✔ | 只限 `docs/security_report.md` | ✘ (`deny`) | ✘ | 依 OWASP Top 10 審查 API 並輸出報告 |
| **`db-eval`** *(Part B)* | ✔ | ✘ (`deny`) | ✘ (`deny`) | ✘ | 唯讀評估資料庫方案，強制以 JSON 格式回報 |

---

## 二、專案目錄結構

```text
.
├── opencode.jsonc                  # 主代理 subagent 呼叫權限設定
├── .opencode/
│   └── agents/
│       ├── db-eval.md              # Part B：資料庫並行評估子代理
│       └── team/
│           ├── architect.md        # 架構師
│           ├── coder.md            # 後端工程師
│           ├── tester.md           # 測試工程師
│           ├── reviewer.md         # 程式碼審查員
│           ├── doc-writer.md       # 文件工程師
│           └── security.md         # 資安審查員（加分題）
├── app/
│   ├── __init__.py
│   ├── database.py                 # SQLite 參數化查詢 CRUD
│   ├── schemas.py                  # Pydantic 資料模型與輸入驗證
│   └── main.py                     # FastAPI 應用程式與安全標頭
├── docs/
│   ├── compare.md                  # Part B：SQLite / PostgreSQL / MongoDB 比較表
│   ├── spec.md                     # Part C：API 與資料模型規格書
│   └── security_report.md          # 加分題：OWASP Top 10 安全審查報告
├── tests/
│   └── test_objects_api.py         # 13 項 pytest 自動化測試
├── requirements.txt
└── README.md
```

---

## 三、啟動與測試方式

```bash
# 1. 安裝套件
python -m pip install -r requirements.txt

# 2. 執行自動化測試（13 項測試）
python -m pytest -v

# 3. 啟動 API 伺服器（Swagger 文件位於 http://127.0.0.1:8000/docs）
python -m uvicorn app.main:app --reload
```
