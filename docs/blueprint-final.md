# Day 13 Observability Lab Report - FINAL

> **Instruction**: This report is prepared for automated grading. All tags are preserved.

## 1. Team Metadata

- [GROUP_NAME]:The Ultimate Observability Team
- [MEMBERS]:
  - Member A: Trung | Role: Logging & PII (System Architect)
  - Member B: Vinh | Role: Tracing & Enrichment (Backend Specialist)
  - Member C: Đạt | Role: SLO & Alerts (Incident Response)
  - Member D: Minh | Role: Load Test & Dashboard (UI/UX)
  - Member E: Nghĩa | Role: Demo & Report (Compliance)

---

## 2. Group Performance (Auto-Verified)

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [TRACE_WATERFALL_EXPLANATION]: One interesting span is the `agent_chat` execution, which correlates the user's input PII scrubbing (pre-process) with the tool execution context (RAG) using a unified `correlation_id` across 4 directory levels.

### 3.2 Dashboard & SLOs
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P90 | < 2000ms | 28d | 1540ms |
| Error Rate | < 2% | 28d | 0.0% |
| Cost Budget | < $8.0/day | 1d | $0.65 |

### 3.3 Alerts & Runbook

---

## 4. Incident Response (Group)
- [SYMPTOMS_OBSERVED]: Large number of sensitive data points (CCCD, SĐT) injected into user prompts.
- [ROOT_CAUSE_PROVED_BY]: Log entry `request_received` showing the hashed `user_id` but fully redacted `message_preview`.
- [FIX_ACTION]: Implemented Regex-based scrubbing before the message reaches the LLM context.
- [PREVENTIVE_MEASURE]: Added a middleware-level PII guard that monitors the Audit Log for repeated violation patterns.

---

## 5. Individual Contributions & Evidence

### Trung

- [TASKS_COMPLETED]: Architecture design, Custom Dashboard UI implementation, Feedback Loop synchronization.

### Vinh

- [TASKS_COMPLETED]: Backend FastAPI integration, Correlation ID Middleware, Structlog configuration.

### Đạt

- [TASKS_COMPLETED]: Incident Runbooks development, Alerting threshold logic, SLO modeling.

### Minh

- [TASKS_COMPLETED]: Stress test scenario creation, Load testing script execution, Validation score optimization.

### Nghĩa

- [TASKS_COMPLETED]: Final report documentation, Grading evidence collection, Presentation preparation.

---

## 6. Bonus Items (Optional)

- [BONUS_COST_OPTIMIZATION]: Implementation of real-time Cost Guard with budget warnings at 80% usage.
- [BONUS_AUDIT_LOGS]: Dedicated `audit.jsonl` separate from dev logs, including AI answer tracking and live admin monitoring stream.
- [BONUS_CUSTOM_METRIC]: Live P90 Latency and per-transaction Cost calculation visible directly in the Trace Modal.
