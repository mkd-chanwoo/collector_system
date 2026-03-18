# TokenCounter Module

## 1. Overview
The `TokenCounter` module computes the number of tokens for each document using a SentencePiece tokenizer. It provides the **single source of truth for token accounting**, which is critical for dataset construction, quota enforcement, and reporting.

This module corresponds to **Stage J: Token Counting**, where all token measurements must be performed using the designated tokenizer.

---

## 2. Role in Pipeline

### Execution Flow

... → Deduplication → Safety → **Token Counting → Quota → Audit → Sharder**

- Runs after all filtering stages  
- Runs before quota enforcement  
- Provides token counts for:
  - dataset balancing  
  - shard metadata  
  - reporting  

---

## 3. Responsibilities

### 3.1 Token Counting
- Convert text into tokens  
- Return token count  

---

### 3.2 Tokenizer Management
- Load SentencePiece tokenizer  
- Ensure tokenizer availability  

---

### 3.3 Error Handling
- Handle encoding failures gracefully  
- Prevent pipeline crash  

---

## 4. Core Methods

### 4.1 __init__(tokenizer_path)

- Loads tokenizer:

    self.sp = spm.SentencePieceProcessor()
    self.sp.load(tokenizer_path)

- Raises RuntimeError if loading fails  

---

### 4.2 count(text)

Steps:

1. Check input:

    if text is None → return 0

2. Encode text:

    tokens = self.sp.encode(text)

3. Return:

    len(tokens)

4. On error:

    return 0  

---

## 5. Input / Output

### Input
- text (string)

### Output
- token count (int)

Example:

    "Hello world" → 3 tokens

---

## 6. Logging & Evidence

### Current Implementation

- no logging  
- silent failure on exception  

---

### Required (Production)

Must record:

- token count per document  
- tokenizer version  
- failed encoding cases  

---

### Example Log

    {
      "doc_id": "...",
      "tokens": 128,
      "status": "success"
    }

---

## 7. Metrics

- total_tokens  
- average_tokens_per_document  
- token_distribution  
- tokenization_failure_rate  

---

## 8. Reproducibility

- deterministic given same tokenizer  
- depends on:
  - tokenizer model file  
  - tokenizer version  

Critical requirement:

- must use a **single consistent tokenizer** across entire pipeline  

---

## 9. Failure Handling

| Scenario            | Behavior |
|--------------------|----------|
| text is None       | return 0 |
| encoding error     | return 0 |
| tokenizer load fail| RuntimeError |

---

## 10. Risks

### 10.1 Silent Failure

- exceptions return 0  
- invalid documents may pass downstream  

---

### 10.2 Tokenizer Inconsistency

- incorrect tokenizer → wrong token counts  
- breaks quota enforcement  

---

### 10.3 No Validation

- does not verify:
  - token distribution  
  - abnormal token counts  

---

### 10.4 No Version Tracking

- tokenizer version not recorded  
- reproducibility risk  

---

## 11. Improvements

### 11.1 Error Logging

Replace silent failure:

    except Exception:
        log_error()

---

### 11.2 Token Validation

- detect abnormal values:
  - extremely low or high token counts  

---

### 11.3 Tokenizer Version Tracking

- store tokenizer metadata  
- include in audit logs  

---

### 11.4 Batch Tokenization

- process multiple documents  
- improve performance  

---

## 12. Compliance with Requirements

| Requirement                  | Status |
|-----------------------------|--------|
| Token counting              | OK     |
| Deterministic output        | OK     |
| Single tokenizer usage      | Partial|
| Logging                     | Missing|
| Version tracking            | Missing|

---

## 13. Conclusion

The `TokenCounter` module provides essential token measurement functionality required for dataset construction and quota control.

However, improvements in logging, validation, and tokenizer version tracking are required to fully meet production-grade standards and ensure reliable token accounting.