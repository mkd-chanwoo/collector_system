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

    python run_downloader.py
    python run_normalizer.py
    python run_pipeline.py
    python run_generate_charts.py

---

## 5. Directory Structure

    collector_system/
    ├── config/
    ├── core/
    ├── data/
    │   ├── raw/
    │   ├── normalized/
    │   ├── shards/
    ├── evidence/
    │   ├── charts/
    ├── logs/
    ├── reports/
    ├── state/
    ├── checkpoints/

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
- Downloader
- DownloadCheckpoint
- IntegrityValidator

### Processing
- Normalizer
- QualityFilter
- LanguageFilter
- Deduplicator
- ToxicFilter

### Measurement & Control
- TokenCounter
- QuotaController

### Validation & Output
- Auditor
- Sharder

### Monitoring & Reporting
- Reporter
- Monitoring
- DailyReporter
- Charts Generator

---

## 8. Data Format

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

### 15.3 Normalization Structure

**Current limitations**
- normalization is implemented as a utility function rather than a pipeline module  
- limited integration with logging and metadata tracking  

**Impact**
- incomplete traceability of preprocessing steps  
- reduced audit visibility  

**Planned improvements**
- refactor normalization into a dedicated pipeline module  
- integrate normalization stage with metadata tracking  
- log transformation statistics  

---

### 15.4 I/O Performance Optimization

**Current limitations**
- frequent flush operations  
- high frequency of file writes  
- reporting executed too often  

**Impact**
- unnecessary I/O overhead  
- reduced throughput in large-scale processing  

**Planned improvements**
- adopt batch-based writing (e.g., 1k–10k documents)  
- reduce flush frequency  
- decouple reporting from processing loop  

---

### 15.5 Error Handling & Logging

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

### 15.6 System Monitoring

**Current limitations**
- no tracking of system-level metrics (CPU, RAM, GPU)  

**Impact**
- limited visibility into performance bottlenecks  
- difficulty in resource optimization  

**Planned improvements**
- integrate system monitoring tools (e.g., psutil)  
- track resource usage during pipeline execution  
- extend monitoring outputs for dashboard integration  

---

### 15.7 Shard Metadata Completeness

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
- 일부 경로 및 파라미터가 코드에 하드코딩됨 - 하지만 repo 전체를 복사한다면 문제 없음.

**Planned improvements**
- 중앙 설정 관리 시스템 구축(필요하면)

---
