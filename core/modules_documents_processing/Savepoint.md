# Savepoint Module

## 1. Overview
The `Savepoint` module provides checkpointing and recovery functionality for the data pipeline. It enables the system to resume processing from the last saved state in case of interruption, failure, or restart.

This module is critical for ensuring **reproducibility, fault tolerance, and long-running pipeline stability**, which are mandatory requirements in production-grade dataset engineering.

---

## 2. Role in Pipeline

### Execution Role

- Runs periodically during pipeline execution
- Stores intermediate processing state
- Enables resume capability after interruption

### Functional Position

Not part of the data transformation pipeline itself, but operates as a **control and reliability layer** across all stages:

Raw → ... → Processing → (Savepoint) → Continue

---

## 3. Responsibilities

### 3.1 Snapshot Management
- Save current pipeline state
- Load previous state for recovery

### 3.2 History Logging
- Append time-series execution logs
- Track pipeline progress over time

### 3.3 Failure Recovery
- Enable restart from last processed dataset and index
- Prevent full pipeline restart

---

## 4. State Structure

### Snapshot File (`pipeline_checkpoint.json`)

    {
      "dataset": "dataset_name",
      "total_docs": int,
      "total_tokens": int,
      "stats_tmp": {...},
      "quota_state": {...}
    }

---

### History Log (`history.jsonl`)

Each line:

    {
      "timestamp": "ISO8601",
      "dataset": "...",
      "total_docs": int,
      "total_tokens": int,
      "stats_tmp": {...},
      "quota_state": {...}
    }

---

## 5. Core Methods

### 5.1 load()

- Loads latest snapshot
- Returns `None` if:
  - file does not exist
  - file is empty
  - JSON is corrupted

---

### 5.2 save(state)

Performs two operations:

#### (1) Atomic Snapshot Save

    temp_path = self.path.with_suffix(".tmp")

    json.dump(state, temp_path)
    temp_path.replace(self.path)

- Prevents partial writes
- Ensures snapshot consistency

#### (2) Append History Log

    self._append_history(state)

---

### 5.3 _append_history(state)

Appends execution log:

    {
      "timestamp": datetime.now(UTC).isoformat(),
      ...
    }

- Stored in JSONL format
- Enables time-series tracking

---

### 5.4 clear()

- Deletes snapshot file
- Used for full reset

---

## 6. Logging & Evidence

### Current Behavior

- Snapshot: latest pipeline state
- History: append-only execution log

### Evidence Produced

- processing progress over time
- token accumulation
- dataset-level progress
- quota state evolution

---

## 7. Metrics & Monitoring Integration

Savepoint enables:

- recovery success rate
- checkpoint frequency
- progress delta over time
- token accumulation trends

These logs feed into:
- daily reports
- monitoring dashboards

---

## 8. Reproducibility

This module is essential for reproducibility:

- preserves intermediate states
- enables exact restart point
- ensures deterministic continuation

Reproducibility depends on:
- consistent tokenizer
- stable upstream processing logic

---

## 9. Failure Handling

| Scenario              | Behavior        |
|----------------------|----------------|
| Missing file         | return None    |
| Empty file           | return None    |
| Corrupted JSON       | return None    |
| Partial write        | prevented via atomic save |

---

## 10. Risks

### 10.1 Silent Failure

- `except:` without logging
- hides JSON corruption or IO errors

### 10.2 State Incompleteness

- does not store:
  - current index explicitly
  - shard state
  - module-level internal states

### 10.3 History Growth

- JSONL file grows indefinitely
- potential disk usage issue

---

## 11. Improvements

### 11.1 Exception Logging

Replace:

    except:
        return None

With:

    except Exception as e:
        log_error(e)

---

### 11.2 State Expansion

Include:

- current dataset index
- shard index
- processing stage

---

### 11.3 History Rotation

- rotate logs daily or by size
- compress old logs

---

### 11.4 Incremental Save Strategy

- save only delta instead of full state
- reduce IO overhead

---

## 12. Compliance with Production Requirements

| Requirement              | Status |
|--------------------------|--------|
| Checkpointing            | OK     |
| Atomic write             | OK     |
| Recovery support         | OK     |
| History logging          | OK     |
| Error transparency       | Missing|
| State completeness       | Partial|

---

## 13. Conclusion

The `Savepoint` module ensures pipeline robustness by enabling checkpointing and recovery. It is essential for long-running data processing tasks and production stability.

However, to meet full production-grade standards, improvements are required in error handling, state completeness, and log management.