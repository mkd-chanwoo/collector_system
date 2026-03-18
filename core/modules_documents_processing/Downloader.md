# Downloader Module

## 1. Overview
The `Downloader` module is responsible for loading datasets from HuggingFace and recording raw dataset metadata. It ensures that all datasets are properly configured, traceable, and reproducible before entering the pipeline.

This module corresponds to **Stage B: Raw Data Collection** and partially **Stage A: Source Discovery and Approval**, where all data sources must be validated, recorded, and preserved with metadata.

---

## 2. Role in Pipeline

### Execution Flow

Source Registry → **Downloader → Raw Data → Integrity Verification → Normalization → ...**

- Entry point of actual data ingestion  
- Loads datasets (streaming or full)  
- Generates raw metadata for audit  

---

## 3. Responsibilities

### 3.1 Dataset Loading
- Load datasets using HuggingFace `load_dataset`
- Support:
  - streaming datasets
  - local/full datasets  

---

### 3.2 Configuration Validation
- Validate required fields:

    hf_name  
    config  
    split  
    field  
    domain  
    streaming  
    url  

- Raise error if any field is missing  

---

### 3.3 Raw Metadata Generation
- Record dataset information before processing  
- Store metadata as JSON  

---

### 3.4 Dataset Card Preservation
- Download README.md from HuggingFace  
- Store locally for traceability  

---

## 4. Core Methods

### 4.1 load_dataset(source_config)

Loads dataset:

    dataset = load_dataset(
        dataset_name,
        config_name,
        split=split,
        streaming=streaming
    )

- Supports streaming mode  
- Raises RuntimeError on failure  

---

### 4.2 raw_info(source_config, save_dir)

Generates raw metadata:

    {
      "filename": "...",
      "config": "...",
      "split": "...",
      "url": "...",
      "checksums": "...",
      "start_time": float,
      "dataset_card": "...",
      "end_time": None
    }

- Records download start time  
- Includes dataset card path  

---

### 4.3 download_dataset_card(source_config, save_dir)

- Downloads README.md via:

    hf_hub_download(...)

- Saves locally  
- Returns path  

---

### 4.4 flush(source_config, save_dir)

- Writes metadata to disk:

    *_raw_metadata.json

- Ensures metadata persistence  

---

## 5. Input / Output

### Input

- source_config (dict)

### Output

- dataset iterator (from HuggingFace)  
- raw metadata JSON file  

---

## 6. Logging & Evidence

### Evidence Produced

- dataset metadata file  
- dataset card (README.md)  
- dataset source information  

These satisfy:

- source traceability  
- documentation requirement  
- audit readiness  

---

## 7. Metrics

- dataset load success/failure  
- dataset size (implicit)  
- processing start time  

---

## 8. Reproducibility

This module ensures reproducibility by:

- preserving dataset source info  
- storing config (hf_name, split, config)  
- saving dataset documentation  

Reproducibility depends on:
- dataset version stability  
- HuggingFace dataset consistency  

---

## 9. Failure Handling

| Scenario                    | Behavior |
|----------------------------|----------|
| Missing config field       | ValueError |
| Dataset load failure       | RuntimeError |
| README download failure    | return None |
| File write failure         | not handled |

---

## 10. Risks

### 10.1 Duplicate raw_info Call

- `flush()` calls raw_info twice  
- unnecessary overhead  

---

### 10.2 Missing End Time

- `end_time` always None  
- incomplete metadata  

---

### 10.3 No Checksum Verification

- checksums marked as "skipped"  
- integrity verification missing  

---

### 10.4 Streaming Limitation

- streaming datasets cannot verify:
  - full size  
  - completeness  

---

## 11. Improvements

### 11.1 Add End Time

    end_time = time.time()

---

### 11.2 Remove Redundant Call

- eliminate duplicate raw_info in flush  

---

### 11.3 Checksum Support

- verify dataset integrity when possible  

---

### 11.4 Version Tracking

- store dataset revision/version  

---

### 11.5 Error Handling

- wrap file operations in try/except  
- log failures  

---

## 12. Compliance with Requirements

| Requirement                | Status |
|---------------------------|--------|
| Dataset loading           | OK     |
| Config validation         | OK     |
| Source traceability       | OK     |
| Dataset card preservation | OK     |
| Integrity verification    | Missing|
| Full metadata completeness| Partial|

---

## 13. Conclusion

The `Downloader` module provides a structured entry point for dataset ingestion and ensures traceability through metadata and dataset documentation.

However, improvements are required in integrity verification, metadata completeness, and error handling to fully meet production-grade standards.