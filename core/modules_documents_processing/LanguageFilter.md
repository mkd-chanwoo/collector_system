# LanguageFilter Module

## 1. Overview
The `LanguageFilter` module detects and validates the language of each document to ensure domain purity (e.g., English-only corpus, Korean-only corpus).

This module corresponds to **Stage E: Language Filtering**, where strict language separation is required to maintain dataset quality and domain balance.

---

## 2. Role in Pipeline

### Execution Flow

Raw → Normalize → Quality → **Language Filtering** → Deduplication → Safety → Token → Quota

- Runs after quality filtering  
- Runs before deduplication  
- Acts as a **hard gate for language purity**  

---

## 3. Responsibilities

### 3.1 Language Detection
- Detect language using FastText model  
- Output language code and confidence score  

### 3.2 Confidence Validation
- Provide confidence score for filtering decisions  
- Enable rejection of low-confidence samples  

### 3.3 Fallback Handling
- Use `langdetect` if FastText fails  
- Prevent pipeline crashes  

---

## 4. Core Methods

### 4.1 __init__(model_path)

- Loads FastText language model:

    fasttext.load_model(model_path)

- Raises RuntimeError on failure  

---

### 4.2 detect_language(text)

Steps:

1. Clean text:
    
    clean_text = "".join(c for c in text if c.isprintable())

2. Normalize whitespace:
    
    replace("\n", " "), replace("\t", " ")

3. Truncate input:
    
    clean_text[:1000]

4. Predict:

    prediction = self.model.predict(...)

5. Extract:

    lang = "__label__en" → "en"  
    confidence = float score  

---

### 4.3 fallback(text)

- Uses:

    detect(text)

- Returns:
  - detected language  
  - "unknown" if failure  

---

## 5. Input / Output

### Input
- text (string)

### Output

    (lang, confidence)

Example:

    ("en", 0.92)

---

## 6. Filtering Logic (Pipeline Level)

Typical usage:

    lang, conf = detect_language(text)

    if conf < threshold:
        reject

    if lang not in allowed_languages:
        reject

---

## 7. Logging & Evidence

### Current Implementation

- prints error on FastText failure:

    print("FASTTEXT ERROR:", e)

---

### Required (Production)

Must log:

- detected language  
- confidence score  
- rejection reason:
  - low confidence  
  - unsupported language  

---

### Recommended Log Format

    {
      "doc_id": "...",
      "lang": "en",
      "confidence": 0.91,
      "status": "accepted"
    }

---

## 8. Metrics

- language_distribution  
- average_confidence  
- rejection_rate_low_confidence  
- rejection_rate_language_mismatch  

---

## 9. Reproducibility

- Deterministic for FastText model  
- Depends on:
  - model version  
  - preprocessing logic  

Fallback (`langdetect`) is:
- non-deterministic (uses randomness)

---

## 10. Failure Handling

| Scenario                | Behavior |
|------------------------|----------|
| FastText failure       | fallback to langdetect |
| langdetect failure     | return "unknown" |
| low confidence         | handled upstream |
| unsupported language   | handled upstream |

---

## 11. Risks

### 11.1 Text Truncation

- Only first 1000 chars used  
- May misclassify long documents  

---

### 11.2 Fallback Inconsistency

- FastText + langdetect may disagree  
- introduces non-determinism  

---

### 11.3 Limited Language Coverage

- Pipeline currently allows only:
  - "en", "ko"  
- excludes:
  - code
  - multilingual content  

---

### 11.4 No Confidence Threshold in Module

- threshold handled outside  
- module not self-contained  

---

## 12. Improvements

### 12.1 Add Configurable Threshold

    if confidence < threshold:
        reject

---

### 12.2 Unified Detection Strategy

- combine:
  - FastText (primary)
  - CLD3 / langdetect (secondary validation)

---

### 12.3 Language-Aware Routing

- allow:
  - code detection
  - multilingual tagging  

---

### 12.4 Structured Logging

- replace print with logging system  
- integrate MetadataTracker  

---

## 13. Compliance with Requirements

| Requirement                  | Status |
|-----------------------------|--------|
| Language detection          | OK     |
| Confidence scoring          | OK     |
| Fallback handling           | OK     |
| Language purity enforcement | Partial|
| Logging                     | Missing|
| Multilingual handling       | Missing|

---

## 14. Conclusion

The `LanguageFilter` module provides reliable language detection using FastText with fallback support. It is essential for maintaining domain purity in the dataset.

However, improvements in logging, threshold handling, and multilingual support are required to meet full production-grade standards.