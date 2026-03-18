# Deduplicator Module

## 1. Overview
The `Deduplicator` module removes duplicate and near-duplicate documents from the dataset. It prevents redundant information from entering the training corpus, which is critical for avoiding overfitting and preserving data diversity.

This module corresponds to **Stage G: Deduplication**, where both exact and near-duplicate removal are mandatory requirements in production pipelines.

---

## 2. Role in Pipeline

### Execution Flow

Raw → Normalize → Quality → Language → **Deduplication** → Safety → Token → Quota → Audit

- Runs after language filtering  
- Runs before toxicity filtering and tokenization  
- Acts as a **data reduction and quality control stage**  

---

## 3. Responsibilities

### 3.1 Exact Duplicate Removal
- Detect identical documents using hashing  
- Remove repeated content completely  

### 3.2 Near-Duplicate Removal
- Detect semantically similar documents  
- Prevent redundancy across sources  

### 3.3 Statistics Tracking
- Track total processed documents  
- Track exact and near duplicate removal counts  

---

## 4. Core Methods

### 4.1 is_exact_duplicate(text)

- Uses SHA256 hash:

    hashlib.sha256(text.encode("utf-8")).hexdigest()

- Logic:
  - If hash already exists → duplicate  
  - Else → store hash  

---

### 4.2 _create_minhash(text)

- Splits text into words  
- Generates 3-word shingles  

    shingles = zip(*(words[i:] for i in range(3)))

- Updates MinHash signature  

- Returns `None` if text too short  

---

### 4.3 is_near_duplicate(text, doc_id)

- Generates MinHash  
- Queries LSH index:

    result = self.lsh.query(m)

- If similar document exists → duplicate  
- Else → insert into LSH  

---

## 5. Algorithms

### 5.1 Exact Deduplication
- SHA256 hashing  
- Time complexity: O(1) lookup  

---

### 5.2 Near Deduplication

- MinHash + LSH (Locality Sensitive Hashing)

Parameters:

- threshold = similarity threshold (default 0.85)  
- num_perm = number of hash permutations (default 128)  

Properties:

- Approximate Jaccard similarity  
- Sublinear search via LSH  

---

## 6. Input / Output

### Input
- text (string)  
- doc_id (string, for near-duplicate indexing)  

### Output

- Exact:
  - `True` → duplicate  
  - `False` → unique  

- Near:
  - `True` → near duplicate  
  - `False` → unique  

---

## 7. Logging & Evidence

### Current Implementation

- Internal counters:
    self.total_docs
    self.exact_removed
    self.near_removed

(※ currently not updated in code — logical gap)

---

### Required (Production)

Must track:

- total input documents  
- exact duplicates removed  
- near duplicates removed  
- removal rate per source  

---

### Example Metrics

- exact_duplicate_rate = exact_removed / total_docs  
- near_duplicate_rate = near_removed / total_docs  

---

## 8. Metrics

- documents_before_dedup  
- documents_after_dedup  
- exact_removal_rate  
- near_removal_rate  
- retention_rate  

---

## 9. Reproducibility

- Exact deduplication is deterministic  
- Near deduplication depends on:
  - MinHash randomness  
  - num_perm parameter  

To ensure reproducibility:
- fix random seed  
- persist LSH state if needed  

---

## 10. Failure Handling

| Scenario             | Behavior |
|---------------------|----------|
| Short text (<3 words)| skip near-dup |
| Encoding error       | upstream handling |
| LSH query empty      | treated as unique |

---

## 11. Risks

### 11.1 Short Text Handling
- texts < 3 words bypass near-dup  
- duplicates may remain  

---

### 11.2 Memory Growth
- seen_hashes grows indefinitely  
- LSH index grows with data  

---

### 11.3 Missing Stats Update
- total_docs / removed counters not incremented  
- audit metrics incomplete  

---

### 11.4 Language Sensitivity
- word-based shingling may not work well for:
  - Korean (no whitespace segmentation issues)
  - code (token structure differs)

---

## 12. Improvements

### 12.1 Statistics Tracking

Add:

    self.total_docs += 1

    if exact:
        self.exact_removed += 1

---

### 12.2 Language-Aware Tokenization

- use tokenizer-based shingles instead of whitespace  
- support Korean and code domains  

---

### 12.3 Memory Optimization

- use disk-backed storage  
- periodically prune LSH  

---

### 12.4 Threshold Tuning

- domain-specific thresholds:
  - code: higher threshold  
  - web text: lower threshold  

---

## 13. Compliance with Requirements

| Requirement                     | Status |
|--------------------------------|--------|
| Exact duplicate removal        | OK     |
| Near duplicate removal         | OK     |
| LSH-based similarity detection | OK     |
| Removal tracking               | Partial|
| Per-source stats               | Missing|
| Audit logging                  | Missing|

---

## 14. Conclusion

The `Deduplicator` module effectively removes redundant data using both exact and approximate methods. It is critical for maintaining dataset diversity and preventing overfitting.

However, improvements are required in statistics tracking, language-aware processing, and audit logging to fully meet production-grade standards.