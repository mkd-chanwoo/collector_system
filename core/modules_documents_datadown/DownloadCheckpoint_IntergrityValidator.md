# DownloadCheckpoint & IntegrityValidator Module

## 1. Overview
This module provides **download state management** and **raw data integrity validation** for the data ingestion stage. It ensures that raw dataset collection is resumable, verifiable, and auditable.

This module corresponds to:
- **Stage B: Raw Data Collection (checkpoint & resume)**
- **Stage C: Integrity Verification (data validation)**

---

## 2. Role in Pipeline

### Execution Flow

Downloader → **Checkpoint Save / Resume → Raw JSONL → Integrity Validation → Metadata**

- Works alongside raw downloader  
- Ensures:
  - fault tolerance (checkpoint)  
  - data correctness (validation)  

---

## 3. Components

### 3.1 DownloadCheckpoint

Manages dataset download progress.

### 3.2 IntegrityValidator

Validates raw JSONL dataset integrity.

---

## 4. DownloadCheckpoint

### 4.1 Responsibilities

- Track current dataset download state  
- Enable resume from last index  
- Prevent reprocessing  

---

### 4.2 Stored State

    {
      "dataset": "dataset_name",
      "last_index": int,
      "status": "running",
      "updated_at": "ISO8601"
    }

---

### 4.3 Core Methods

#### load()

- Loads checkpoint file  
- Returns None if not exists  

---

#### save(dataset_name, index, status)

- Saves current progress  
- Overwrites previous state  

---

#### is_resume(dataset_name)

- Checks if current dataset matches checkpoint  

---

#### get_index()

- Returns last processed index  

---

#### clear()

- Deletes checkpoint after completion  

---

## 5. IntegrityValidator

### 5.1 Responsibilities

- Validate JSONL format  
- Detect corrupted lines  
- Detect encoding errors  

---

### 5.2 Validation Process

1. Read file in binary mode:

    open(file_path, "rb")

2. Decode line:

    raw_line.decode("utf-8")

3. Check encoding issues:
   - UnicodeDecodeError  
   - replacement character (�)  

4. Parse JSON:

    json.loads(line)

5. Count:
   - total lines  
   - corrupted lines  
   - encoding errors  

---

### 5.3 Output

    {
      "dataset": "...",
      "file_path": "...",
      "total_lines": int,
      "corrupted_lines": int,
      "encoding_errors": int,
      "valid": bool,
      "timestamp": "..."
    }

---

### 5.4 Validation Rule

- valid if:
  - corrupted_lines == 0  
  - encoding_errors == 0  

- additional rule:

    if encoding_errors / total_lines > 0.05:
        valid = False  

---

### 5.5 Logging

- Saves validation result:

    logs/downloader_log/{dataset}.json  

---

## 6. Input / Output

### Input

- file_path (JSONL)  
- dataset_name  

### Output

- validation result (bool)  
- log file  

---

## 7. Logging & Evidence

### Evidence Produced

- checkpoint state file  
- validation logs  

Supports:

- resume traceability  
- data integrity proof  
- audit validation  

---

## 8. Metrics

- total_lines  
- corrupted_lines  
- encoding_error_rate  
- validation_pass_rate  

---

## 9. Reproducibility

- checkpoint ensures:
  - resumable execution  
  - consistent processing  

- integrity validation ensures:
  - data correctness  
  - reproducible dataset  

---

## 10. Failure Handling

| Scenario                  | Behavior |
|--------------------------|----------|
| missing checkpoint       | return None |
| missing file             | return False |
| decoding error           | count as encoding error |
| JSON parsing error       | count as corrupted |

---

## 11. Risks

### 11.1 Overwrite Checkpoint

- only one dataset tracked  
- multi-dataset resume limitation  

---

### 11.2 No Atomic Write

- checkpoint write not atomic  
- risk of corruption  

---

### 11.3 Performance Cost

- full file scan for validation  
- expensive for large datasets  

---

### 11.4 Hardcoded Paths

- reduces portability  

---

## 12. Improvements

### 12.1 Multi-Dataset Checkpoint

- track multiple datasets simultaneously  

---

### 12.2 Atomic Save

- write temp file → rename  

---

### 12.3 Incremental Validation

- validate during download  
- avoid full scan  

---

### 12.4 Configurable Paths

- move paths to config  

---

## 13. Compliance with Requirements

| Requirement              | Status |
|--------------------------|--------|
| Resume support           | OK     |
| Checkpoint tracking      | OK     |
| JSONL validation         | OK     |
| Encoding validation      | OK     |
| Multi-source tracking    | Missing|
| Atomic checkpoint        | Missing|

---

## 14. Conclusion

This module provides essential reliability mechanisms for raw data collection, ensuring both resumability and data integrity.

While functional, enhancements in checkpoint management, performance, and configurability are required to meet full production-grade standards.