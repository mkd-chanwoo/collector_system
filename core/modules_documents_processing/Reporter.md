# Reporter Module

## 1. Overview
The `Reporter` module records the real-time progress of the pipeline and outputs aggregated statistics in JSON format. It provides a lightweight summary of processing status, including document counts, token counts, and rejection statistics across pipeline stages.

This module supports **Stage N: Monitoring and Reporting**, enabling quick inspection of pipeline health and progress.

---

## 2. Role in Pipeline

### Execution Flow

Processing Loop → Stats Aggregation → **Reporter → JSON + Console Output**

- Called periodically (e.g., every N documents)  
- Produces summary snapshot  
- Provides human-readable console output  

---

## 3. Responsibilities

### 3.1 Progress Tracking
- Track total documents processed  
- Track total tokens processed  

---

### 3.2 Stage-wise Statistics
- Record rejection counts per stage:
  - non-text  
  - quality filtering  
  - language filtering  
  - deduplication  
  - toxicity filtering  
  - audit  

---

### 3.3 Reporting Output
- Save JSON report  
- Print formatted summary to console  

---

## 4. Core Method

### write(stats, stats2)

Generates report:

    {
      "timestamp": float,
      "elapsed_seconds": float,
      "documents_processed": int,
      "tokens_processed": int,
      "nontext_document": int,
      "quality_filtering": int,
      "low_language_confidence": int,
      "no_eng_kor": int,
      "exactly_duplicate": int,
      "near_duplicate": int,
      "toxic_filtering": int,
      "audit": int,
      "processed_documents_dataset": int
    }

- `stats`: global counters  
- `stats2`: stage-level counters  

---

## 5. Output

### 5.1 JSON File

- Overwritten each call  

    output_file

- Contains latest snapshot  

---

### 5.2 Console Output

Formatted summary:

    Documents : 1,000
    Tokens    : 5,000,000
    Elapsed   : 120.5 sec
    ...

---

## 6. Metrics

### Core Metrics

- documents_processed  
- tokens_processed  
- elapsed_seconds  

---

### Stage Metrics

- nontext_document  
- quality_filtering  
- language filtering failures  
- deduplication (exact / near)  
- toxic filtering  
- audit failures  

---

## 7. Logging & Evidence

### Evidence Produced

- real-time pipeline status  
- stage-level rejection counts  

Supports:

- monitoring  
- debugging  
- quick validation  

---

## 8. Reproducibility

- provides snapshot of pipeline state  
- does not preserve history  

Reproducibility depends on:
- external logs (history.jsonl, metadata)  

---

## 9. Failure Handling

| Scenario              | Behavior |
|----------------------|----------|
| Missing directory    | auto-create |
| File write failure   | not handled |
| Missing stats key    | defaults to 0 |

---

## 10. Risks

### 10.1 Overwrite Behavior

- JSON file overwritten each time  
- no history preserved  

---

### 10.2 No Error Handling

- file operations not protected  

---

### 10.3 Inconsistent Naming

- field names inconsistent:
  - `lang_confi`, `lang_in`  
- reduces readability  

---

### 10.4 Limited Granularity

- no per-source stats  
- no domain-level stats  

---

## 11. Improvements

### 11.1 Append Mode / Versioning

- keep history of reports  
- timestamped files  

---

### 11.2 Structured Logging

- standardize field names  
- align with audit schema  

---

### 11.3 Error Handling

- add try/except for file IO  

---

### 11.4 Integration with Dashboard

- connect to monitoring system  
- push metrics  

---

## 12. Compliance with Requirements

| Requirement              | Status |
|--------------------------|--------|
| Progress tracking        | OK     |
| Stage-level statistics   | OK     |
| JSON reporting           | OK     |
| Historical tracking      | Missing|
| Error handling           | Missing|

---

## 13. Conclusion

The `Reporter` module provides a simple and effective mechanism for tracking pipeline progress and stage-level statistics.

However, it lacks historical tracking, structured logging, and robustness, which are required for full production-grade monitoring and audit support.