# Logging (TeeStream & enable_file_logging) Module

## 1. Overview
The logging module redirects standard output (`stdout`) and error output (`stderr`) to both the console and a file simultaneously. It enables persistent logging of pipeline execution without modifying existing print-based code.

This module supports **Monitoring and Reporting (Stage N)** by ensuring all runtime messages are recorded as evidence.

---

## 2. Role in Pipeline

### Execution Role

- Initialized at pipeline start  
- Wraps global output streams  

### Functional Position

Pipeline Start → **Logging Enabled** → All Modules → Logs Persisted

- Affects entire pipeline globally  
- Captures:
  - debug logs  
  - errors  
  - progress messages  

---

## 3. Responsibilities

### 3.1 Dual Output Logging
- Print to console  
- Write to file simultaneously  

---

### 3.2 Error Capture
- Capture `stderr` messages  
- Persist runtime errors  

---

### 3.3 Log Persistence
- Save logs to file in real time  
- Ensure no loss of output  

---

## 4. Core Components

### 4.1 TeeStream

Custom stream wrapper:

    class TeeStream:
        def __init__(self, *streams):
            self.streams = streams

#### write(data)

    for s in streams:
        s.write(data)
        s.flush()

- Writes to multiple streams  
- Forces immediate flush  

---

### 4.2 enable_file_logging(log_path)

Steps:

1. Create directory:

    log_path.parent.mkdir(parents=True, exist_ok=True)

2. Open log file:

    open(log_path, "a", encoding="utf-8", buffering=1)

3. Redirect streams:

    sys.stdout = TeeStream(sys.stdout, log_file)
    sys.stderr = TeeStream(sys.stderr, log_file)

---

## 5. Input / Output

### Input

- log_path (string or Path)

### Output

- log file created and appended  

---

## 6. Logging Behavior

- Mode: append (`"a"`)  
- Encoding: UTF-8  
- Buffering: line-buffered (1)  

Output includes:

- all print() outputs  
- all exception traces  
- all warnings  

---

## 7. Logging & Evidence

### Evidence Produced

- full pipeline execution trace  
- error logs  
- progress logs  

Supports:

- debugging  
- audit verification  
- monitoring system integration  

---

## 8. Metrics

Indirectly enables:

- error rate tracking  
- processing speed logs  
- failure pattern analysis  

---

## 9. Reproducibility

- logs provide execution history  
- enable replay and debugging  

Reproducibility depends on:
- completeness of logs  
- consistency of pipeline behavior  

---

## 10. Failure Handling

| Scenario              | Behavior |
|----------------------|----------|
| Log directory missing| auto-create |
| File open failure    | not handled |
| Stream error         | propagated |

---

## 11. Risks

### 11.1 Global Stream Override

- overrides `sys.stdout` and `sys.stderr`  
- may affect external libraries  

---

### 11.2 Performance Overhead

- flush on every write  
- potential slowdown  

---

### 11.3 No Log Rotation

- file grows indefinitely  
- disk usage risk  

---

### 11.4 No Structured Logging

- plain text logs only  
- difficult for automated analysis  

---

## 12. Improvements

### 12.1 Log Rotation

- rotate by size or date  
- compress old logs  

---

### 12.2 Structured Logging

- JSON logs  
- include timestamps, levels  

---

### 12.3 Logging Levels

- INFO / WARNING / ERROR  
- filter verbosity  

---

### 12.4 Async Logging

- buffer logs  
- reduce I/O overhead  

---

## 13. Compliance with Requirements

| Requirement              | Status |
|--------------------------|--------|
| Runtime logging          | OK     |
| Error capture            | OK     |
| Persistent logs          | OK     |
| Structured logging       | Missing|
| Log management           | Missing|

---

## 14. Conclusion

The logging module ensures full visibility into pipeline execution by duplicating console output into persistent log files.

While effective for basic monitoring and debugging, enhancements such as structured logging, rotation, and performance optimization are required for production-grade deployment.