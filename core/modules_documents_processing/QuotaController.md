# Reporting & Visualization (Charts Generator) Module

## 1. Overview
This module generates visual reports from pipeline execution logs and state files. It transforms historical and snapshot data into charts that provide evidence of dataset construction progress and quality.

This module corresponds to **Stage N: Monitoring and Reporting** and **Section 9: Required Graphs and Charts**, where visual evidence is mandatory for validation and audit.

---

## 2. Role in Pipeline

### Execution Flow

Pipeline Execution → Logs (history.jsonl, checkpoint.json) → **Chart Generator → PNG Outputs**

- Runs post-processing (offline or periodically)  
- Consumes:
  - history logs  
  - snapshot state  
- Produces visual artifacts  

---

## 3. Responsibilities

### 3.1 Visualization
- Generate charts for:
  - token distribution  
  - domain balance  
  - deduplication impact  
  - audit results  

---

### 3.2 Evidence Generation
- Produce PNG charts  
- Support audit and reporting requirements  

---

### 3.3 Historical Analysis
- Analyze time-series data  
- Track pipeline progression  

---

## 4. Input Data Sources

### 4.1 History File

    state/history.jsonl

Contains:
- timestamp  
- dataset  
- total_tokens  
- stats_tmp  

---

### 4.2 Snapshot File

    checkpoints/pipeline_checkpoint.json

Contains:
- quota_state  
- stats_tmp  

---

## 5. Output

### Directory

    evidence/charts/

### Format

- PNG images  
- one chart per metric  

---

## 6. Generated Charts

### 6.1 Token Count by Source
- Bar chart  
- max tokens per dataset  

---

### 6.2 Token Count by Domain
- Bar chart  
- domain distribution  

---

### 6.3 Cumulative Tokens
- Line chart  
- token growth over time  

---

### 6.4 Cleaned vs Raw
- Bar chart  
- filtering effectiveness  

---

### 6.5 Deduplication Impact
- Bar chart  
- exact vs near duplicates  

---

### 6.6 Document Length Distribution
- Histogram  
- distribution of processed docs  

---

### 6.7 Token Length Distribution
- Histogram  
- token distribution  

---

### 6.8 Language Purity
- Pie chart  
- valid vs invalid language  

---

### 6.9 Daily Throughput
- Line chart  
- tokens per day  

---

### 6.10 Audit Summary
- Bar chart  
- pass vs fail  

---

### 6.11 Storage Growth
- Line chart  
- estimated storage usage  

---

## 7. Core Functions

### load_history()

- Reads JSONL file  
- returns list of records  

---

### load_snapshot()

- Loads latest checkpoint  
- returns dict  

---

### save(name)

- Saves chart:

    evidence/charts/{name}.png

---

### main()

- orchestrates chart generation  
- executes all visualization functions  

---

## 8. Metrics

Derived metrics include:

- token growth rate  
- domain distribution  
- filtering effectiveness  
- deduplication impact  
- audit pass rate  
- storage growth trend  

---

## 9. Logging & Evidence

### Evidence Produced

- visual proof of pipeline progress  
- dataset quality indicators  
- audit validation artifacts  

Required for:
- final report  
- audit review  
- monitoring dashboard  

---

## 10. Reproducibility

- deterministic given same input logs  
- depends on:
  - history completeness  
  - snapshot accuracy  

---

## 11. Failure Handling

| Scenario              | Behavior |
|----------------------|----------|
| Missing history file | crash    |
| Missing snapshot     | returns None |
| plotting error       | not handled |

---

## 12. Risks

### 12.1 No Error Handling
- file read/write not protected  
- potential crash  

---

### 12.2 Data Inconsistency
- relies on stats_tmp correctness  
- incorrect stats → misleading charts  

---

### 12.3 Approximate Metrics
- storage = tokens * 4 (rough estimate)  

---

### 12.4 Static Output
- no interactive dashboard  
- limited usability  

---

## 13. Improvements

### 13.1 Error Handling
- wrap file IO and plotting  

---

### 13.2 Interactive Visualization
- integrate with dashboard tools  
- e.g., Grafana, W&B  

---

### 13.3 More Accurate Metrics
- real storage measurement  
- document-level stats  

---

### 13.4 Automated Scheduling
- generate charts periodically  

---

## 14. Compliance with Requirements

| Requirement                | Status |
|---------------------------|--------|
| Required charts           | OK     |
| Visual evidence           | OK     |
| Historical tracking       | OK     |
| Error handling            | Missing|
| Real-time dashboard       | Missing|

---

## 15. Conclusion

The reporting module generates essential visual evidence required for monitoring and audit. It provides clear insight into dataset construction progress and quality.

However, it requires improvements in robustness, accuracy, and integration with real-time monitoring systems to fully meet production-grade standards.