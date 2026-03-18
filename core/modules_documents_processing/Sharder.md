# Sharder Module

## 1. Overview
The `Sharder` module groups processed documents into fixed-size JSONL files (shards) and writes them to disk along with shard-level metadata.

This module corresponds to **Stage M: Packaging for Training**, where the final dataset must be stored in structured, shard-based formats with metadata for efficient loading and audit.

---

## 2. Role in Pipeline

### Execution Flow

Processing → Audit → **Sharder → Final Dataset (JSONL shards)**

- Runs after document validation (Auditor)  
- Final step before dataset completion  
- Produces training-ready files  

---

## 3. Responsibilities

### 3.1 Document Buffering
- Accumulate documents in memory  
- Maintain token count per shard  

---

### 3.2 Shard Creation
- Write documents into JSONL files  
- Use fixed shard size (default: 10,000 docs)  

---

### 3.3 Metadata Generation
- Record shard-level statistics:
  - document count  
  - token count  

---

### 3.4 Recovery Support
- Detect existing shards  
- Resume shard indexing  

---

## 4. Core Methods

### 4.1 __init__(output_dir, shard_size)

- Initializes buffer and directories  
- Recovers shard index  

---

### 4.2 _recover_shard_index()

- Scans existing files:

    shard_000001.jsonl

- Extracts indices  
- Returns next shard index  

---

### 4.3 add_document(doc, tokens)

- Adds document to buffer:

    self.current_docs.append(doc)

- Updates token count  
- Triggers flush when buffer full  

---

### 4.4 flush()

Steps:

1. Write shard file:

    shard_{index}.jsonl

2. Write metadata:

    shard_meta.jsonl

3. Reset buffer  

---

## 5. Output Structure

### Directory Layout

    output_dir/
      shard_000000.jsonl
      shard_000001.jsonl
      ...
      meta/
        shard_meta.jsonl

---

### Shard File Format

Each line:

    {
      "doc_id": "...",
      "text": "...",
      ...
    }

---

### Metadata File

    {
      "shard_id": "shard_000001.jsonl",
      "doc_count": int,
      "token_count": int
    }

---

## 6. Metrics

- documents_per_shard  
- tokens_per_shard  
- total_shards  
- shard_size consistency  

---

## 7. Logging & Evidence

### Evidence Produced

- final dataset shards  
- shard-level metadata  

Supports:

- audit validation  
- dataset integrity checks  
- training pipeline compatibility  

---

## 8. Reproducibility

- deterministic shard creation  
- depends on:
  - input order  
  - shard_size  

Recovery logic ensures:
- consistent shard numbering  

---

## 9. Failure Handling

| Scenario               | Behavior |
|-----------------------|----------|
| Empty buffer          | skip flush |
| Existing shards       | resume index |
| Invalid filenames     | ignored |
| File write failure    | not handled |

---

## 10. Risks

### 10.1 No Atomic Write

- shard files written directly  
- risk of partial write on failure  

---

### 10.2 No Checksum

- no integrity verification  
- corrupted shard undetected  

---

### 10.3 Memory Usage

- buffer stores full documents  
- large shard_size → high memory  

---

### 10.4 Metadata Simplicity

- missing:
  - checksum  
  - timestamp  
  - domain info  

---

## 11. Improvements

### 11.1 Atomic Write

- write to temp file → rename  

---

### 11.2 Checksum Support

- add hash per shard  

---

### 11.3 Extended Metadata

    {
      "shard_id": "...",
      "doc_count": ...,
      "token_count": ...,
      "timestamp": ...,
      "checksum": ...
    }

---

### 11.4 Compression

- store shards as:
  - .jsonl.gz  

---

### 11.5 Error Handling

- wrap file operations  
- log failures  

---

## 12. Compliance with Requirements

| Requirement              | Status |
|--------------------------|--------|
| Shard generation         | OK     |
| JSONL format             | OK     |
| Metadata tracking        | Partial|
| Recovery support         | OK     |
| Checksum verification    | Missing|
| Atomic write             | Missing|

---

## 13. Conclusion

The `Sharder` module converts processed documents into structured JSONL shards suitable for training. It provides basic metadata and recovery capabilities.

However, enhancements such as atomic writes, checksum validation, and richer metadata are required to meet full production-grade dataset packaging standards.