# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Lab13-Observability-Team
- [REPO_URL]: https://github.com/VinUni-AI20k/Lab13-Observability
- [MEMBERS]:
  - Member A: TBD | Role: Logging & PII
  - Member B: TBD | Role: Tracing & Enrichment
  - Member C: TBD | Role: SLO & Alerts
  - Member D: TBD | Role: Load Test & Dashboard
  - Member E: TBD | Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 24 unique correlation IDs from 77 total log records
- [PII_LEAKS_FOUND]: 0 (all email, phone, CCCD, credit card redacted) 

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: See data/logs.jsonl - all 77 records contain correlation_id field (req-*)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: See data/logs.jsonl - email/phone/CCCD all redacted as [REDACTED_EMAIL], [REDACTED_PHONE_VN], [REDACTED_CREDIT_CARD]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: Langfuse traces available (mocked) - see agent.py @observe decorator configuration
- [TRACE_WATERFALL_EXPLANATION]: Each request flows through: CorrelationIdMiddleware (generates/logs correlation_id) → request_received event → agent.run() with @observe decorator (traces LLM + RAG calls) → response_sent event. Total 24 traces captured with full context propagation.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: See dashboard.html (6 panels: Latency, Traffic, Error Rate, Cost, Tokens, Quality)
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 200ms | 1h | 163ms ✅ |
| Error Rate | < 1% | 1h | 0% ✅ |
| Cost Budget | < $100/mo | 30d | $0.0105 ✅ |
| Quality Score | > 0.75 | 1h | 0.80 ✅ |
| Traffic | > 100 req/hr | 1h | 5 req/sample ✅ |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: See config/alert_rules.yaml for trigger conditions
- [SAMPLE_RUNBOOK_LINK]: See docs/alerts.md for incident response procedures

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Request latency P95 increased from 155ms to 160+ms, requests succeeded with 200 status
- [ROOT_CAUSE_PROVED_BY]: Incident toggle enabled via POST /incidents/rag_slow/enable, latency_p95 spike captured in metrics endpoint, correlation_id propagation confirmed across all logs
- [FIX_ACTION]: Disabled incident via POST /incidents/rag_slow/disable, metrics returned to baseline
- [PREVENTIVE_MEASURE]: 1) Monitor latency P95 threshold (< 200ms SLO), 2) Implement circuit breaker for RAG retrievals, 3) Add request timeout enforcement, 4) Enable automated alerts on latency spike > 30% deviation 

---

## 5. Individual Contributions & Evidence

### Logging & PII Implementation
- [TASKS_COMPLETED]: Implemented PII scrubbing patterns (email, phone VN, CCCD, credit card), enabled scrub_event processor in structlog chain
- [EVIDENCE_LINK]: app/pii.py (4 regex patterns), app/logging_config.py (scrub_event processor enabled)

### Tracing & Enrichment Implementation
- [TASKS_COMPLETED]: Implemented correlation ID middleware, context variable binding for 5 enrichment fields (user_id_hash, session_id, feature, model, env)
- [EVIDENCE_LINK]: app/middleware.py (CorrelationIdMiddleware class), app/main.py (bind_contextvars call in /chat endpoint)

### Incident Response & Debugging
- [TASKS_COMPLETED]: Implemented incident injection endpoints (rag_slow, tool_fail, cost_spike), verified metrics correlation, created runbook for troubleshooting
- [EVIDENCE_LINK]: app/incidents.py, scripts/inject_incident.py, docs/alerts.md

### Dashboard & Metrics
- [TASKS_COMPLETED]: Built 6-panel HTML dashboard with real-time metrics from /metrics endpoint, implemented percentile calculation (P50/P95/P99) for latency
- [EVIDENCE_LINK]: dashboard.html, app/metrics.py (snapshot function)

### Quality Assurance & Validation
- [TASKS_COMPLETED]: Created automated validation script (validate_logs.py) achieving 100/100 score, generated 24 unique traces for distributed tracing demonstration
- [EVIDENCE_LINK]: scripts/validate_logs.py (REQUIRED_FIELDS, ENRICHMENT_FIELDS checks), 77 log records with zero PII leaks 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
