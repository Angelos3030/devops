# Threat Model for conversational editing system

This document models the security boundaries and threat mitigation strategies for the AI-assisted editing engine. Since the model receives untrusted natural language input from users, it must be treated as an untrusted agent.

## 1. Threats & Mitigation Matrix

| Threat | Source / Entrypoint | Severity | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Prompt Injection** | User Chat Message | **High** | The LLM ONLY outputs structured JSON matching the `EditPlan` schema. No natural language instructions are executed as code. The backend parses the JSON and maps it to deterministic, pre-written database functions. |
| **RCE (Remote Code Execution)** | Malicious Chat Input | **Critical** | Zero use of `eval()`, `exec()`, or dynamic system execution of model output. Input strings are parsed strictly as values, not commands or code. |
| **IDOR (Tenant Data Leakage)** | FastAPI Endpoint | **Critical** | Every request verifies ownership. The `Authorization` header bearer token is authenticated via Supabase Auth. The `client_id` requested is verified to match the authenticated user's email via `require_client_access`. |
| **Script/HTML Injection (XSS)** | Text Fields / URLs | **High** | Text parameters are length-capped and html-escaped. URLs (e.g., social links, custom URLs) are validated to ensure they start with `https://` and do not use `javascript:` or `data:` prefixes. |
| **Secrets Exposure** | Model Context / Prompt Leak | **Medium** | No secrets, credentials, or backend API tokens are ever included in the `SiteContext` sent to the model. The model only receives the public site data (name, description, hours, services) and current user message. |
| **Concurrency / Stale Updates** | Double-Submit / Parallel Tabs | **Medium** | Database updates use optimistic locking with versioning / timestamp checks. If the client state has been updated since the LLM planned the edit, the transaction is aborted. |
| **Reversible Transaction Failures** | Execution Errors | **Low** | Edits are applied in a database transaction block. If one operation in a multi-op plan fails, the entire transaction is rolled back, preventing half-applied states. |

## 2. Input Sanitization & Safety Check Filters

1. **Greek & English Script Lock**: The reply must be in Greek or English. Any unexpected Unicode block (e.g. Cyrillic, Han, Hangul) results in immediate rejection to prevent linguistic drift or weird payload delivery.
2. **Leakage Prevention**: Deterministic inspection of the LLM's natural language reply prevents internal DB keys or API parameters (like `palette`, `font_pair`, `cta_title`) from being shown to users.
3. **Pydantic Validation**: All fields, numbers, and lists are schema-validated at runtime. Extra fields are rejected.
