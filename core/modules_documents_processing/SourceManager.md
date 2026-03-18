# SourceManager Module

## 1. Overview
The `SourceManager` module manages the dataset source registry and provides validated dataset configurations to the pipeline. It ensures that all datasets are properly defined, structured, and compliant before ingestion.

This module corresponds to **Stage A: Source Discovery and Approval**, where every dataset must be registered, validated, and documented prior to use.

---

## 2. Role in Pipeline

### Execution Flow

Config Load → **SourceManager → Validated Sources → Downloader**

- Entry point of dataset definition  
- Provides configuration to downstream modules  
- Ensures only valid sources enter pipeline  

---

## 3. Responsibilities

### 3.1 Source Registry Management
- Load dataset configurations from YAML  
- Maintain centralized dataset registry  

---

### 3.2 Configuration Validation
- Validate required fields for each dataset  
- Prevent invalid configurations  

---

### 3.3 Source Access Interface
- Provide access to:
  - all sources  
  - individual source config  

---

### 3.4 Summary Reporting
- Print overview of registered datasets  

---

## 4. Configuration Schema

Each dataset must include:

    hf_name
    config
    split
    field
    domain
    streaming
    target_tokens

---

### Example

    datasets:
      refinedweb:
        hf_name: tiiuae/falcon-refinedweb
        config: default
        split: train
        field: text
        domain: english
        streaming: true
        target_tokens: 1000000

---

## 5. Core Methods

### 5.1 __init__(config_path)

- Loads YAML file  
- Validates existence of "datasets" key  
- Calls validation  

---

### 5.2 _validate_sources()

- Ensures required fields exist  
- Raises ValueError on missing fields  

---

### 5.3 list_sources()

- Returns all dataset configs  

---

### 5.4 get_source(name)

- Returns single dataset config  
- Raises KeyError if not found  

---

### 5.5 print_summary()

- Prints:

    dataset_name | domain | target_tokens  

---

## 6. Input / Output

### Input

- YAML config file  

### Output

- dictionary of dataset configurations  

---

## 7. Logging & Evidence

### Evidence Produced

- dataset registry (YAML)  
- validated configuration  

Supports:

- source traceability  
- audit requirements  
- reproducibility  

---

## 8. Metrics

- number of datasets  
- token allocation per dataset  
- domain distribution  

---

## 9. Reproducibility

- fully deterministic  
- depends on:
  - YAML configuration  
  - version control of config file  

Ensures:
- consistent dataset selection  
- reproducible pipeline execution  

---

## 10. Failure Handling

| Scenario                    | Behavior |
|----------------------------|----------|
| Missing config file        | FileNotFoundError |
| Missing "datasets" key     | ValueError |
| Missing required field     | ValueError |
| Unknown dataset name       | KeyError |

---

## 11. Risks

### 11.1 Limited Validation

- does not validate:
  - URL correctness  
  - domain validity  
  - token targets consistency  

---

### 11.2 No License Tracking

- license field not included  
- audit requirement gap  

---

### 11.3 Static Configuration

- requires manual updates  
- no dynamic source discovery  

---

## 12. Improvements

### 12.1 Extended Schema

Add:

    license
    url
    description
    version

---

### 12.2 Validation Enhancement

- validate domain values  
- validate token targets  

---

### 12.3 Source Approval Status

- add approval flag  

---

### 12.4 Integration with Audit System

- track:
  - source usage  
  - token contribution  

---

## 13. Compliance with Requirements

| Requirement              | Status |
|--------------------------|--------|
| Source registry          | OK     |
| Config validation        | OK     |
| Source traceability      | Partial|
| License tracking         | Missing|
| Approval system          | Missing|

---

## 14. Conclusion

The `SourceManager` module provides a structured and validated entry point for dataset configuration, ensuring that only properly defined sources are used in the pipeline.

However, it requires enhancements in validation depth, license tracking, and audit integration to fully meet production-grade standards.