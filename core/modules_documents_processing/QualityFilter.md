# QualityFilter Module

## 1. Overview
The `QualityFilter` module removes low-quality, noisy, and non-informative text from the dataset using heuristic and statistical rules.

This module corresponds to **Stage F: Quality Filtering**, where low-value content such as boilerplate, spam, and malformed text must be removed before further processing.

---

## 2. Role in Pipeline

### Execution Flow

Raw → Normalize → **Quality Filtering** → Language → Deduplication → Safety → Token

- Runs after normalization  
- Runs before language filtering  
- Acts as a **primary noise reduction stage**  

---

## 3. Responsibilities

### 3.1 Length Filtering
- Remove too short or too long documents  

### 3.2 Noise Detection
- Remove spam (URLs, markup-heavy text)  
- Remove boilerplate content  

### 3.3 Structural Quality Checks
- Detect repetitive or low-diversity text  
- Detect template-like documents  

### 3.4 Statistical Filtering
- Entropy-based filtering  
- n-gram repetition detection  

---

## 4. Core Methods

### 4.1 keep(text)

Main filtering function:

- returns `True` if document passes  
- returns `False` if rejected  

Checks:

- length bounds  
- URL spam  
- markup ratio  
- character diversity  
- template detection  
- repetition  
- boilerplate phrases  
- entropy  

---

### 4.2 Length Filtering

    if length < min_chars → reject  
    if length > max_chars → reject  

---

### 4.3 URL Spam Detection

    len(url_pattern.findall(text)) > 5

---

### 4.4 Markup Ratio

    tag_chars / len(text)

- reject if > 0.3  

---

### 4.5 Character Diversity

    len(set(tokens)) / len(tokens) < 0.2

- detects repetitive tokens  

---

### 4.6 Template Detection (SimHash)

    near = self.index.get_near_dups(h)

- if similar document exists → reject  
- else → store hash  

---

### 4.7 Repetition Detection

    repetition_ratio > 0.2

- based on n-gram frequency  

---

### 4.8 Boilerplate Detection

- checks presence of phrases:

    "accept cookies"  
    "privacy policy"  
    "terms of service"  

---

### 4.9 Entropy Filtering

    ent = - Σ p log2(p)

- reject if entropy < 3.5  

---

### 4.10 Boilerplate Removal (Optional)

Uses:

    trafilatura.extract(...)

- removes HTML boilerplate  
- fallback: return original text  

---

## 5. Algorithms

- Regex-based filtering  
- SimHash (template detection)  
- Shannon entropy  
- n-gram frequency analysis  

---

## 6. Input / Output

### Input
- text (string)

### Output
- `True`: keep document  
- `False`: reject document  

---

## 7. Logging & Evidence

### Current Implementation

- no structured logging  
- only boolean result  

---

### Required (Production)

Must record:

- rejection reason  
- filter stage name  
- threshold values  
- document length before/after  

---

### Example Log

    {
      "doc_id": "...",
      "stage": "quality_filter",
      "reason": "low_entropy",
      "entropy": 2.9
    }

---

## 8. Metrics

- rejection_rate_quality  
- rejection_reason_distribution  
- average_document_length  
- entropy_distribution  

---

## 9. Reproducibility

- deterministic given same parameters  
- depends on:
  - thresholds  
  - SimHash state  

SimHash introduces:
- state dependency (order-sensitive)

---

## 10. Failure Handling

| Scenario            | Behavior |
|--------------------|----------|
| None input         | reject   |
| extraction failure | fallback |
| short text         | reject   |

---

## 11. Risks

### 11.1 Over-Filtering

- aggressive thresholds may remove useful data  

---

### 11.2 Language Bias

- token-based logic may not work well for Korean  

---

### 11.3 SimHash State Dependency

- results depend on processing order  

---

### 11.4 No Logging

- no rejection trace  
- audit difficulty  

---

## 12. Improvements

### 12.1 Structured Logging

- record rejection reason  
- integrate MetadataTracker  

---

### 12.2 Language-Aware Processing

- separate logic for:
  - Korean  
  - code  

---

### 12.3 Threshold Tuning

- domain-specific thresholds  

---

### 12.4 Stateless Template Detection

- batch-based similarity instead of incremental  

---

## 13. Compliance with Requirements

| Requirement              | Status |
|--------------------------|--------|
| Noise filtering          | OK     |
| Boilerplate removal      | OK     |
| Template detection       | OK     |
| Statistical filtering    | OK     |
| Logging                  | Missing|
| Audit traceability       | Missing|

---

## 14. Conclusion

The `QualityFilter` module effectively removes noisy and low-quality data using multiple heuristic and statistical techniques.

However, to meet production-grade standards, it requires improvements in logging, audit traceability, and language-aware processing.