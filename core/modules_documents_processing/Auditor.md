# Auditor Module

## 1. Overview
The `Auditor` module validates each document before it enters the final dataset. It ensures structural correctness, encoding validity, and consistency between text, character count, and token count.

This module corresponds to **Stage L: Dataset Audit and Validation**, where no data may enter the final corpus without passing validation checks.

---

## 2. Role in Pipeline

### Execution Flow

Raw → Normalize → Quality → Language → Deduplication → Safety  
→ Token Counting → Quota Enforcement → **Auditor → Sharder**

- Runs after token counting and quota enforcement  
- Runs before sharding and final storage  
- Acts as a strict validation gate  

---

## 3. Input / Output Specification

### Input

    {
      "doc_id": "string",
      "source": "string",
      "domain": "string",
      "text": "string",
      "char_count": int,
      "tokens_count": int
    }

### Output

- `True`: document is valid  
- `False`: document is rejected  

---

## 4. Validation Logic

### 4.1 Structural Validation

- Input must be a dictionary  
- Required fields:
  - doc_id
  - source
  - domain
  - text
  - char_count
  - tokens_count

---

### 4.2 Text Integrity Validation

- text must be string  
- not empty  
- UTF-8 encodable  

    text.encode("utf-8")

---

### 4.3 Consistency Validation

Character count:

    doc["char_count"] == len(text)

Token count:

    doc["tokens_count"] > 0

---

### 4.4 Broken Text Detection

    printable_ratio = sum(c in string.printable for c in text) / len(text)

- reject if < 0.7

---

## 5. Logging & Evidence

Current:

    stats_tmp["audit"] += 1

Required:

- total evaluated docs  
- rejected docs  
- rejection reasons  
- per-source rejection rate  

---

## 6. Metrics

- audit_pass_rate = accepted / total  
- audit_rejection_rate = rejected / total  

---

## 7. Failure Handling

| Failure Type          | Action  |
|----------------------|--------|
| Missing field        | Reject |
| Encoding error       | Reject |
| Empty text           | Reject |
| Token count invalid  | Reject |
| Broken text          | Reject |

---

## 8. Configuration

    auditor:
      printable_threshold: 0.7
      required_fields:
        - doc_id
        - source
        - domain
        - text
        - char_count
        - tokens_count

---

## 9. Reproducibility

- Deterministic  
- Stateless  

---

## 10. Risks

- English bias in printable check  
- no semantic validation  
- missing detailed logs  

---

## 11. Improvements

- Unicode-aware validation  
- return rejection reason  
- integrate MetadataTracker  

---

## 12. Conclusion

This module ensures structural validity before final dataset inclusion.  
However, additional logging and audit traceability are required for full production compliance.