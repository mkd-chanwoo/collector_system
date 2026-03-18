# ToxicFilter Module

## 1. Overview
The `ToxicFilter` module detects and removes harmful, abusive, or low-quality toxic content from the dataset. It combines lexical filtering with a machine learning–based toxicity model to ensure baseline safety.

This module corresponds to **Stage H: Safety and Toxicity Filtering**, where filtering of harmful and unusable content is mandatory.

---

## 2. Role in Pipeline

### Execution Flow

... → Deduplication → **Toxicity Filtering** → Token Counting → Quota → Audit

- Runs after deduplication  
- Runs before token counting  
- Acts as a **safety gate**  

---

## 3. Responsibilities

### 3.1 Lexical Filtering
- Detect explicit bad words using predefined dictionary  

---

### 3.2 Model-Based Toxicity Detection
- Use Detoxify model to score toxicity  
- Filter high-toxicity content  

---

### 3.3 Performance Optimization
- Apply sampling to reduce computation  
- Limit input length for model inference  

---

## 4. Core Methods

### 4.1 __init__(sample_rate, max_length)

- Loads profanity dictionary:

    profanity.load_censor_words()

- Loads model:

    Detoxify("original")

- Parameters:
  - sample_rate (default 0.05)  
  - max_length (default 512)  

---

### 4.2 badword_filter(text)

- Checks:

    profanity.contains_profanity(text)

- Returns:
  - True → contains bad words  
  - False → clean  

---

### 4.3 toxicity_filter(text, threshold=0.9)

Steps:

1. Sampling:

    if random.random() > sample_rate → skip

2. Length truncation:

    text[:max_length]

3. Model prediction:

    score = self.model.predict(text)

4. Decision:

    toxicity_score > threshold

Returns:

    (is_toxic, toxicity_score)

---

## 5. Input / Output

### Input
- text (string)

### Output

- badword_filter:
  - True / False  

- toxicity_filter:
  - (True, score) → toxic  
  - (False, score) → safe  

---

## 6. Algorithms

### 6.1 Lexical Filtering
- dictionary-based matching  
- fast, deterministic  

---

### 6.2 ML-Based Filtering

- Detoxify model  
- outputs toxicity score ∈ [0,1]  

---

### 6.3 Sampling Strategy

- Only process ~5% of documents  
- reduces computational cost  

---

## 7. Logging & Evidence

### Current Implementation

- no logging  
- no record of filtered samples  

---

### Required (Production)

Must record:

- number of toxic documents removed  
- toxicity score distribution  
- sampling rate  
- threshold used  

---

### Example Log

    {
      "doc_id": "...",
      "toxicity_score": 0.93,
      "status": "rejected"
    }

---

## 8. Metrics

- toxic_rejection_rate  
- average_toxicity_score  
- sampled_documents_ratio  
- badword_detection_rate  

---

## 9. Reproducibility

- badword filter: deterministic  
- toxicity model:
  - deterministic inference  
- sampling:
  - non-deterministic (random)  

Reproducibility requires:
- fixed random seed  
- fixed model version  

---

## 10. Failure Handling

| Scenario              | Behavior |
|----------------------|----------|
| sampling skip        | treated as safe |
| model error          | not handled |
| empty text           | upstream handling |

---

## 11. Risks

### 11.1 Sampling Risk

- only 5% checked  
- toxic content may pass  

---

### 11.2 Threshold Sensitivity

- threshold=0.9 is strict  
- may miss moderate toxicity  

---

### 11.3 Language Bias

- Detoxify primarily trained on English  
- may not detect Korean toxicity  

---

### 11.4 No Logging

- no audit trace  
- no visibility into filtering  

---

## 12. Improvements

### 12.1 Deterministic Sampling

- set random seed  
- enable reproducibility  

---

### 12.2 Adaptive Sampling

- increase sampling for suspicious texts  

---

### 12.3 Multi-Language Support

- use multilingual toxicity models  

---

### 12.4 Structured Logging

- record filtering decisions  
- integrate MetadataTracker  

---

## 13. Compliance with Requirements

| Requirement              | Status |
|--------------------------|--------|
| Bad-word filtering       | OK     |
| Toxicity scoring         | OK     |
| Sampling optimization    | OK     |
| Logging                  | Missing|
| Full coverage            | Partial|
| Multilingual support     | Missing|

---

## 14. Conclusion

The `ToxicFilter` module provides a two-stage safety filtering mechanism combining lexical and model-based approaches.

While efficient due to sampling, it introduces risks in coverage and lacks audit logging. Enhancements in reproducibility, logging, and multilingual capability are required for production-grade deployment.