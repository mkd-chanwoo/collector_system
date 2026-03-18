# Keural Foundation Model Dataset Pipeline

## 1. Overview

This repository implements a **production-grade LLM data engineering pipeline** for constructing a high-quality, reproducible training corpus for a foundation model.

This is **NOT a simple data collection project**.  
Every step must be:

- measurable  
- reproducible  
- auditable  
- documented  

---

## 2. Project Goal

The goal is to construct a **high-quality, balanced, and production-ready dataset** for large-scale model training.

### Requirements

- High quality  
- Deduplicated  
- Token-verified  
- Domain-balanced  
- Fully documented  
- Audit-ready  
- Real-time monitored  

---

## 3. Pipeline Architecture

A  Source Discovery  
B  Raw Data Collection  
C  Integrity Verification  
D  Format Normalization  
E  Language Filtering  
F  Quality Filtering  
G  Deduplication  
H  Safety Filtering  
I  Metadata Generation  
J  Token Counting  
K  Quota Enforcement  
L  Audit  
M  Sharding  
N  Monitoring & Reporting  
O  Final Packaging  

---

## 4. Execution Order
start
watch log
pid check
kill pid

    nohup python -u pipeline/run_downloader.py >> pipeline/log/log_downloader.txt 2>&1 &
    tail -f pipeline/log/log_downloader.txt
    pgrep -fl run_downloader.py
    kill PID
    
    nohup python -u pipeline/run_normalizer.py >> pipeline/log/log_normalizer.txt 2>&1 &
    tail -f pipeline/log/log_normalizer.txt
    pgrep -fl run_normalizer.py
    kill PID
    
    nohup python -u pipeline/run_pipeline.py >> pipeline/log/log_pipeline.txt 2>&1 &
    tail -f pipeline/log/log_pipeline.txt
    pgrep -fl run_pipeline.py
    kill PID
    
---

## 5. Directory Structure

    collector_system/
    ├── config/
    ├── core/
    │   ├── modules_document_datadown/
    │   ├── modules_document_processing/
    ├── data/
    │   ├── raw/
    │   ├── normalized/
    │   ├── shards/
    │   ├── meta/
    ├── evidence/
    │   ├── charts/
    ├── logs/
    │   ├── downloader_log/
    ├── reports/
    │   ├── Daily/
    ├── state/
    ├── tokenizer/
    ├── utils/
    ├── checkpoints/
    ├── collector_system/
    │   ├── download_checkpoint
    │   ├── normalizer_checkpoint

---

## 6. Pipeline Flow

    Approved Source
        ↓
    Raw Download (Streaming)
        ↓
    Integrity Validation
        ↓
    Normalization
        ↓
    Quality Filtering
        ↓
    Language Filtering
        ↓
    Deduplication
        ↓
    Toxicity Filtering
        ↓
    Token Counting
        ↓
    Quota Enforcement
        ↓
    Audit Validation
        ↓
    Sharding
        ↓
    Monitoring & Reporting
        ↓
    Chart Generation

---

## 7. Core Modules

### Source & Ingestion
- SourceManager 
-- This module is responsible for loading and managing configuration files used throughout the pipeline.--
  
- Downloader
--This module retrieves data using a streaming approach, processing it line-by-line in JSONL format and dumping the raw output into the data/raw directory without modification.--
  
- DownloadCheckpoint
- IntegrityValidator
--This module validates raw stored data by checking for missing lines and detecting encoding issues through comparison with the original dataset, ensuring data completeness and integrity.--

### Processing
- Normalizer
--The text is normalized by removing null characters, unifying line breaks, converting multi-line text into a single line, collapsing multiple whitespaces, and trimming leading/trailing spaces.--
  
- QualityFilter
  --This module performs quality filtering using heuristic rules, including length constraints, URL/HTML pattern detection via regex, and text structure analysis. It applies SimHash for template/near-duplicate detection, n-gram repetition analysis for redundancy, and Shannon entropy to filter low-information content, along with boilerplate phrase matching to remove non-informative text.--
  
- LanguageFilter
--This module performs language detection using a FastText pre-trained model for primary classification, leveraging its speed and high accuracy on short text segments. It preprocesses text to remove non-printable characters and limits input length for efficiency, while using langdetect as a fallback mechanism to ensure robustness in case of model failure, returning both predicted language and confidence score.--

- Deduplicator
--This module performs deduplication using a two-stage approach: exact duplicate detection via SHA256 hashing and near-duplicate detection using MinHash with LSH (Locality Sensitive Hashing). Exact duplicates are efficiently tracked with a hash set, while semantic similarity is captured by generating n-gram (shingle) based MinHash signatures and querying them through an LSH index, enabling scalable and approximate duplicate detection in large datasets.--

- ToxicFilter
--This module performs toxicity filtering using a hybrid approach: rule-based bad word detection via the better_profanity library and model-based scoring using the Detoxify deep learning model. To improve efficiency, it applies random sampling and input length truncation before inference, reducing computational cost while still capturing high-toxicity content through a threshold-based classification.--

### Measurement & Control
- TokenCounter
- QuotaController
--Tracks token usage per domain and source, enforcing predefined token budgets with real-time updates and warning thresholds (50–100%) to prevent quota overflow and maintain balanced dataset distribution.--

### Validation & Output
- Auditor
--Validates documents using rule-based checks, including required field presence, text type and non-emptiness, UTF-8 encoding validity, consistency between text length and char_count, positive token count, and printable character ratio to detect corrupted or broken text.--
  
- Sharder
--Writes processed documents into fixed-size JSONL shards, batching data and saving both shard files and corresponding metadata (document count, token count). It maintains shard indexing for continuity and recovery, enabling efficient storage, downstream training usage, and traceable dataset packaging.--

### Monitoring & Reporting
- Reporter
- Monitoring
- DailyReporter
- Charts Generator

---

## 8.1 Data Format After Format Normalization

    {
      "doc_id": "...",
      "source_name": "...",
      "domain": "...",
      "language": "...",
      "text": "...",
      "url": "...",
      "license": "...",
      "timestamp": "...",
      "raw_path": "...",
      "processing_version": "v1"
    }

## 8.2 Data Format After Pipeline

    {
      "doc_id": "...",
      "source": "...",
      "domain": "...",
      "text": "...",
      "char_count": "...",
      "tokens_count": "..."
    }


---

## 9. Key System Features

- Resume & checkpoint system  
- Exact + near deduplication  
- Token-based accounting  
- Domain quota enforcement  
- Audit validation  
- Real-time monitoring  
- Chart-based reporting  

---

## 10. Evidence Structure
### not yet but I record in checkpoint the total count of filtering. I have to implement this.

    evidence/
    ├── download_logs/
    ├── validation_logs/
    ├── cleaning_logs/
    ├── dedup_logs/
    ├── token_logs/
    ├── audit_logs/
    ├── charts/

---

## 11. Rules

### DO NOT
- skip validation  
- assume data quality  
- mix domains blindly  
- report without evidence  

### MUST
- log everything  
- track tokens strictly  
- preserve raw data  
- ensure reproducibility  

---

## 12. Deliverables

- dataset shards (JSONL)  
- source registry  
- cleaning & dedup reports  
- token statistics  
- monitoring logs  
- charts  
- audit reports  

---

## 13. Warning

Bad dataset → bad model

- duplicates → overfitting  
- toxic data → unsafe outputs  
- imbalance → performance degradation  

This is **infrastructure-level engineering**, not scripting.

---

## 14. Quick Start

    python run_downloader.py
    python run_normalizer.py
    python run_pipeline.py
    python run_generate_charts.py
    

## 15. Limitations & Future Improvements

The pipeline has addressed key requirements such as token consistency and metadata tracking.  
However, several aspects still require improvement to achieve full production-grade robustness and stability.

---

### 15.1 Atomic Write & Data Safety

**Current limitations**
- shard files are written directly without atomic guarantees  
- checkpoint overwrite is not crash-safe  
- metadata append operations are not protected  

**Impact**
- risk of partial writes and file corruption in case of interruption  
- potential inconsistency between data and metadata  

**Planned improvements**
- implement atomic write pattern (temporary file → rename)  
- ensure crash-safe checkpointing  
- synchronize data and metadata writes  

---

### 15.2 Deduplication Stability

**Current limitations**
- deduplication behavior depends on input order  
- streaming-based insertion into similarity index  

**Impact**
- non-deterministic deduplication results  
- reduced reliability in large-scale dataset construction  

**Planned improvements**
- introduce batch-based deduplication  
- persist hash/signature states across runs  
- decouple deduplication from processing order  

---

### 15.3 Error Handling & Logging

**Current limitations**
- reliance on print-based error handling  
- lack of structured logging system  

**Impact**
- limited observability  
- difficulty in debugging and failure analysis  

**Planned improvements**
- introduce centralized logging system  
- persist structured error logs  
- implement retry and failure tracking mechanisms  

---

### 15.4 Shard Metadata Completeness

**Current limitations**
- shard metadata contains only basic statistics  

**Impact**
- limited auditability and integrity verification  

**Planned improvements**
- extend metadata to include:
  - checksum  
  - creation timestamp  
  - domain information  

---

### 15.8 Configuration Management

**Current limitations**
- Some paths and parameters are hardcoded into code - but no problem if you copy the entire repo.

**Planned improvements**
- Building a centralized setup management system (if required)

---
