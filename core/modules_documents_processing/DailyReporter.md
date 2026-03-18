# DailyReporter Module

## 1. Overview
The `DailyReporter` module generates structured daily and real-time reports of pipeline progress. It exports token statistics, domain-level progress, and source-level contributions in machine-readable formats.

This module corresponds to **Stage N: Monitoring and Reporting** and **Section 5.7 Daily Summary Export**, where continuous visibility into dataset construction is mandatory.

---

## 2. Role in Pipeline

### Execution Role

- Triggered periodically (e.g., during shard flush)
- Produces reporting artifacts for monitoring systems

### Functional Position

Processing → Token Counting → Quota → Sharding → **DailyReporter**

- Does not modify data  
- Produces **observability outputs only**

---

## 3. Responsibilities

### 3.1 Real-Time Budget Tracking
- Export current total tokens
- Track shard generation progress
- Record domain-level token accumulation

### 3.2 Domain Progress Monitoring
- Compare actual tokens vs target quota
- Compute completion ratios

### 3.3 Source Contribution Tracking
- Track token contribution per source within each domain

### 3.4 Daily Snapshot Logging
- Store daily cumulative token counts
- Enable trend analysis over time

---

## 4. Output Files

### 4.1 token_budget_live.json

    {
      "timestamp": "ISO8601",
      "total_tokens": int,
      "shards_written": int,
      "domains": {
        "english": int,
        "korean": int,
        ...
      }
    }

- Real-time snapshot  
- Overwritten on each export  

---

### 4.2 domain_progress.json

    {
      "english": {
        "tokens": int,
        "target": int,
        "progress": float
      }
    }

- Progress ratio per domain  
- Used for quota monitoring  

---

### 4.3 source_contribution.csv

    domain,source,tokens
    english,refinedweb,123456
    korean,news_corpus,45678

- Tracks token contribution per source  

---

### 4.4 token_budget_daily.csv

    date,total_tokens
    2026-03-17,12345678

- Append-only daily log  
- Enables long-term trend tracking  

---

## 5. Core Methods

### 5.1 export(quota_controller, shard_index)

Main entry point:

- collects:
  - total tokens  
  - domain tokens  
  - source tokens  
- triggers all export functions  

---

### 5.2 _export_live_budget()

- Writes real-time snapshot  
- Includes shard index and timestamp  

---

### 5.3 _export_domain_progress()

- Computes progress ratio:

    progress = tokens / target

- Handles zero-target safely  

---

### 5.4 _export_source_contribution()

- Writes CSV of:
  - domain
  - source
  - token count  

---

### 5.5 _export_daily_snapshot()

- Appends daily token total  
- Creates header if file does not exist  

---

## 6. Logging & Evidence

### Evidence Produced

- token growth over time  
- domain balance status  
- source contribution distribution  
- shard generation progress  

These outputs are required for:
- audit reports  
- dashboard visualization  
- progress validation  

---

## 7. Metrics

### Core Metrics

- total_tokens  
- tokens_per_domain  
- progress_ratio_per_domain  
- tokens_per_source  
- daily_token_growth  

---

## 8. Reproducibility

- Deterministic given same quota state  
- Depends on:
  - QuotaController state integrity  
  - consistent token counting  

Daily logs provide:
- historical trace  
- reproducibility evidence  

---

## 9. Failure Handling

| Scenario              | Behavior |
|----------------------|----------|
| Missing directory    | auto-create |
| File exists          | overwrite (JSON), append (CSV) |
| Partial write        | not handled explicitly |

---

## 10. Risks

### 10.1 Timestamp Inconsistency
- Uses `datetime.utcnow()` (naive)
- No timezone standardization

---

### 10.2 Overwrite Risk
- live JSON files overwritten each run
- no version history

---

### 10.3 No Error Handling
- file write failures not caught

---

### 10.4 CSV Growth
- daily CSV grows indefinitely
- potential storage issue

---

## 11. Improvements

### 11.1 Timezone Standardization

Replace:

    datetime.utcnow()

With:

    datetime.now(UTC)

---

### 11.2 Versioned Snapshots

- keep historical JSON snapshots  
- not just latest state  

---

### 11.3 Error Handling

- wrap file writes with try/except  
- log failures  

---

### 11.4 Log Rotation

- rotate CSV by size or date  
- compress old logs  

---

## 12. Compliance with Requirements

| Requirement                     | Status |
|--------------------------------|--------|
| Real-time token tracking       | OK     |
| Domain progress monitoring     | OK     |
| Source contribution tracking   | OK     |
| Daily summary export           | OK     |
| Error handling                 | Missing|
| Versioned logging              | Missing|

---

## 13. Conclusion

The `DailyReporter` module provides essential visibility into pipeline execution, enabling real-time monitoring and historical analysis of dataset construction.

It fulfills core reporting requirements but requires enhancements in error handling, logging robustness, and time standardization to meet full production-grade standards.