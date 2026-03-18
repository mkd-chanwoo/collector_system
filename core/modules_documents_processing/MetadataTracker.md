# MetadataTracker Module

## 1. Overview
The `MetadataTracker` module records per-document processing history across all pipeline stages. It captures pass/fail decisions, intermediate metrics, and final acceptance status for each document.

This module is critical for **auditability, traceability, and reproducibility**, and directly supports requirements from:
- Metadata Generation (Stage I)  
- Dataset Audit System (Section 6)  

Without this module, full audit compliance is not achievable.

---

## 2. Role in Pipeline

### Execution Flow

Each document:

Initialize → record(stage results) → finalize → save

Integrated across all stages:

Normalize → Quality → Language → Dedup → Safety → Audit  
→ **MetadataTracker (record at each step)**

- Runs alongside every filtering stage  
- Does not alter data  
- Produces **audit logs per document**  

---

## 3. Responsibilities

### 3.1 Per-Stage Tracking
- Record pass/fail for each filter stage  
- Store additional metadata (confidence, length changes, etc.)  

---

### 3.2 Final Decision Recording
- Aggregate all stage results  
- Produce final accept/reject decision  

---

### 3.3 Persistent Logging
- Save metadata as JSONL  
- Append one record per document  

---

## 4. Data Structure

### Metadata Schema

    {
      "doc_id": int,
      "filters": {
        "Quality-Filtering": {
          "passed": true,
          "info": ...
        },
        "Language-Filtering": {
          "passed": false,
          "lang": "en",
          "confidence": 0.65
        }
      },
      "final_decision": "accepted"
    }

---

## 5. Core Methods

### 5.1 record(filter_name, passed, **info)

- Records result of a pipeline stage:

    self.data["filters"][filter_name] = {
        "passed": passed,
        **info
    }

- Supports arbitrary metadata via `**info`

---

### 5.2 finalize()

- Computes final decision:

    passed = all(f["passed"] for f in filters)

- Sets:

    "accepted" or "rejected"

- Returns full metadata object  

---

### 5.3 save()

- Writes metadata to JSONL:

    process.jsonl

- Appends one line per document  
- Uses UTF-8 encoding  

---

### 5.4 _convert(obj)

- Converts numpy types:

    np.float32 → float  
    np.int64 → int  

- Ensures JSON compatibility  

---

## 6. Storage Design

### Directory Structure

    path/
      dataset_name/
        process.jsonl

### File Format

- JSONL (append-only)  
- One document per line  

---

## 7. Logging & Evidence

### Evidence Produced

- full per-document processing trace  
- filter-level pass/fail history  
- rejection reasons  
- final decision  

This enables:

- audit replay  
- error diagnosis  
- filtering analysis  

---

## 8. Metrics

Derived from metadata:

- rejection rate per filter  
- filter contribution to rejection  
- pipeline bottleneck analysis  
- acceptance rate  

---

## 9. Reproducibility

- Full trace per document  
- Enables exact replay of decisions  

Reproducibility requires:

- consistent pipeline logic  
- stable filter thresholds  

---

## 10. Failure Handling

| Scenario              | Behavior |
|----------------------|----------|
| Missing filters      | handled in finalize |
| JSON serialization   | handled via _convert |
| File write failure   | not handled |

---

## 11. Risks

### 11.1 Severe Performance Overhead

- file write per document  
- high I/O cost  
- major bottleneck in large-scale pipelines  

---

### 11.2 No Batching

- immediate write instead of buffered write  
- inefficient disk usage  

---

### 11.3 No Error Handling

- save() has no try/except  
- potential silent failure  

---

### 11.4 File Growth

- JSONL grows indefinitely  
- potential storage explosion  

---

## 12. Improvements

### 12.1 Batch Logging

- buffer N records before write  

---

### 12.2 Async Logging

- use queue + worker thread  
- decouple from main pipeline  

---

### 12.3 Sampling Strategy

- log subset of documents (e.g., 1~5%)  
- full logging only for rejected samples  

---

### 12.4 Log Rotation

- split by size or date  
- compress old logs  

---

### 12.5 Error Handling

- wrap file write in try/except  
- log failures  

---

## 13. Compliance with Requirements

| Requirement                  | Status |
|-----------------------------|--------|
| Per-document metadata       | OK     |
| Filter-level traceability   | OK     |
| Final decision tracking     | OK     |
| Audit support               | OK     |
| Performance efficiency      | Poor   |
| Log management              | Missing|

---

## 14. Conclusion

The `MetadataTracker` module is essential for auditability and traceability, providing full visibility into document-level processing decisions.

However, its current implementation introduces significant performance overhead and lacks log management. Optimization strategies such as batching, async logging, and sampling are required for production-scale deployment.