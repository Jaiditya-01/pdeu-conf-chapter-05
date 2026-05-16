# Anomaly Detection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a `detect_anomalies` tool to find fraud patterns (duplicates, ghost payments, and outliers) in the consolidated audit database.

**Architecture:** A new tool `detect_anomalies` will be added to `audit_agent.py`. It will perform multi-stage SQL analysis on `consolidated_audit.db` and return a structured JSON summary of findings.

**Tech Stack:** Python, SQLite, JSON.

---

### Task 1: Implement the Detection Tool and Agent Integration

**Files:**
- Modify: `audit_agent.py`

- [ ] **Step 1: Implement `detect_anomalies` function**
Add the function to `audit_agent.py`. It must query `consolidated_audit.db`.

- [ ] **Step 2: Update `build_agent` and `SYSTEM_PROMPT`**
Add the new tool to the `tools` list in `build_agent`. Update `SYSTEM_PROMPT` to include: "Use detect_anomalies to proactively scan for fraud, duplicates, and ghost payments."

- [ ] **Step 3: Update `DB_PATH` and `_connect`**
Point `DB_PATH` to `consolidated_audit.db`. Update `_connect` to ensure it uses the correct path.

- [ ] **Step 4: Commit**
`git add audit_agent.py && git commit -m "feat: add anomaly detection tool and switch to consolidated database"`

---

### Task 2: Verification

**Files:**
- Create: `tests/test_anomalies.py`

- [ ] **Step 1: Write verification tests**
Test `detect_anomalies` returns the expected structure.

- [ ] **Step 2: Run tests**
`pytest tests/test_anomalies.py -v`

- [ ] **Step 3: Commit**
`git add tests/test_anomalies.py && git commit -m "test: add anomaly detection verification tests"`
