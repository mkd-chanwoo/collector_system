# Monitoring Module

## 1. Overview
The `Monitoring` module exports real-time pipeline metrics into structured files for dashboard integration and system observability. It provides comprehensive visibility into dataset construction, including token progress, domain balance, cleaning efficiency, and error statistics.

This module corresponds to **Stage N: Monitoring and Reporting** and **Section 8: Monitoring Dashboard Architecture**, where continuous tracking and visualization are mandatory.

---

## 2. Role in Pipeline

### Execution Flow

Processing Loop → Stats Aggregation → **Monitoring → JSON / CSV Outputs → Dashboard**

- Called periodically during pipeline execution  
- Produces machine-readable monitoring data  
- Feeds external dashboards (e.g., Grafana, W&B)  

---

## 3. Responsibilities

### 3.1 Global Progress Tracking
- Track total tokens vs target  
- Compute completion percentage  

---

### 3.2 Domain-Level Monitoring
- Track tokens per domain  
- Measure progress toward domain quotas  

---

### 3.3 Source Contribution Tracking
- Track token contribution per source  

---

### 3.4 Cleaning & Dedup Metrics
- Measure filtering effectiveness  
- Track deduplication impact  

---

### 3.5 Error & Audit Tracking
- Track rejection counts  
- Monitor audit failures  

---

### 3.6 Throughput Tracking
- Track processing speed over time  
- Record documents, tokens, shards  

---

## 4. Output Files

### 4.1 global_progress.json

    {
      "timestamp": "...",
      "total_tokens": int,
      "target_tokens": int,
      "remaining": int,
      "progress": float
    }

---

### 4.2 domain_progress.json

    {
      "english": {
        "tokens": int,
        "target": int,
        "progress": float
      }
    }

---

### 4.3 source_contribution.json

    {
      "english": {
        "source_name": tokens
      }
    }

---

### 4.4 cleaning_efficiency.json

    {
      "raw": int,
      "cleaned": int,
      "removal_rate": float
    }

---

### 4.5 deduplication.json

    {
      "exact": int,
      "near": int
    }

---

### 4.6 errors.json

    {
      "quality_reject": int,
      "lang_low_conf": int,
      "lang_invalid": int,
      "toxic": int
    }

---

### 4.7 audit.json

    {
      "audit_reject": int,
      "processed": int
    }

---

### 4.8 throughput.csv

    timestamp,documents,tokens,shards
    2026-03-17T12:00:00,1000,500000,5

---

## 5. Core Methods

### export(quota, stats, stats_tmp, sharder)

- Main entry point  
- Calls all monitoring functions  

---

### global_progress()

- Computes:

    progress = total_tokens / target_tokens

---

### domain_progress()

- Computes per-domain ratios  

---

### source_contribution()

- Dumps quota.source_tokens  

---

### cleaning_efficiency()

- Computes:

    removal_rate = (raw - cleaned) / raw

---

### deduplication()

- Tracks exact / near duplicates  

---

### error_stats()

- Aggregates rejection counts  

---

### audit_status()

- Tracks audit failures  

---

### throughput()

- Appends time-series data to CSV  

---

## 6. Metrics

### Core Metrics

- total_tokens  
- progress_ratio  
- tokens_per_domain  
- tokens_per_source  

---

### Quality Metrics

- cleaning removal rate  
- deduplication counts  
- error distribution  

---

### Performance Metrics

- documents processed  
- tokens processed  
- shard count  
- throughput over time  

---

## 7. Logging & Evidence

### Evidence Produced

- real-time pipeline metrics  
- domain balance validation  
- filtering effectiveness  
- audit statistics  

Supports:

- dashboard visualization  
- audit validation  
- progress reporting  

---

## 8. Reproducibility

- deterministic given same inputs  
- depends on:
  - quota state  
  - stats consistency  

Throughput logs provide:
- historical trace  
- execution timeline  

---

## 9. Failure Handling

| Scenario              | Behavior |
|----------------------|----------|
| Missing directory    | auto-create |
| File overwrite       | JSON overwritten |
| CSV append           | append mode |
| File write failure   | not handled |

---

## 10. Risks

### 10.1 No Error Handling
- file operations not protected  
- potential silent failure  

---

### 10.2 Overwrite Behavior
- JSON files overwritten each call  
- no historical snapshots  

---

### 10.3 Timestamp Consistency
- uses `datetime.utcnow()`  
- no timezone standardization  

---

### 10.4 Metric Accuracy Dependency
- depends entirely on stats_tmp correctness  
- upstream errors propagate  

---

## 11. Improvements

### 11.1 Add Error Handling
- wrap file writes with try/except  

---

### 11.2 Historical Snapshots
- store versioned JSON files  
- not just latest state  

---

### 11.3 Timezone Standardization

    datetime.now(UTC)

---

### 11.4 Dashboard Integration
- push metrics to external systems  
- real-time visualization  

---

## 12. Compliance with Requirements

| Requirement                  | Status |
|-----------------------------|--------|
| Global progress tracking    | OK     |
| Domain monitoring           | OK     |
| Source contribution         | OK     |
| Cleaning efficiency         | OK     |
| Deduplication metrics       | OK     |
| Error monitoring            | OK     |
| Throughput tracking         | OK     |
| Historical logging          | Partial|

---

## 13. Conclusion

The `Monitoring` module provides comprehensive real-time visibility into pipeline execution, covering progress, quality, and performance metrics.

It satisfies most monitoring requirements but requires enhancements in error handling, historical logging, and dashboard integration to achieve full production-grade observability.