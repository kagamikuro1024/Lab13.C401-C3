# Evidence Collection Sheet

## Required screenshots
- Langfuse trace list with >= 10 traces
- One full trace waterfall
- JSON logs showing correlation_id
- Log line with PII redaction
- Dashboard with 6 panels
- Alert rules with runbook link

## Optional screenshots
- Incident before/after fix
- Cost comparison before/after optimization
- Auto-instrumentation proof

--- Lab Verification Results ---
Total log records analyzed: 1
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 1
Potential PII leaks detected: 0

--- Grading Scorecard (Estimates) ---
+ [PASSED] Basic JSON schema
- [FAILED] Correlation ID propagation (less than 2 unique IDs)
+ [PASSED] Log enrichment
+ [PASSED] PII scrubbing

Estimated Score: 80/100


## Kết quả kiểm tra metric ở 

```bash
curl http://localhost:8000/obs-metrics
```

{"traffic":7,"latency_p50":7972.0,"latency_p95":328431.0,"latency_p99":328431.0,"avg_cost_usd":0.002593,"total_cost_usd":0.01815,"tokens_in_total":57,"tokens_out_total":1191,"error_breakdown":{},"quality_avg":0.8}