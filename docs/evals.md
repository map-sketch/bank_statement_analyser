# Evaluation Strategy: Privacy-First AI Bank Statement Analyzer

> Evaluation metrics and strategies derived from [architecture.md](file:///c:/Users/aksha/Downloads/PMF/bank%20statement%20analyser/architecture.md), [implementation_plan.md](file:///c:/Users/aksha/Downloads/PMF/bank%20statement%20analyser/implementation_plan.md), and [edgecases.md](file:///c:/Users/aksha/Downloads/PMF/bank%20statement%20analyser/edgecases.md)

---

## Table of Contents

1. [Categorization Engine Evaluation](#1-categorization-engine-evaluation)
2. [Data Ingestion & Parsing Evaluation](#2-data-ingestion--parsing-evaluation)
3. [Analytics & Insights Evaluation](#3-analytics--insights-evaluation)
4. [Human-in-the-Loop (HITL) Metrics](#4-human-in-the-loop-hitl-metrics)
5. [System Performance & Security Metrics](#5-system-performance--security-metrics)
6. [Evaluation Datasets (Gold Standards)](#6-evaluation-datasets-gold-standards)

---

## 1. Categorization Engine Evaluation

The core of the system is the two-layer categorization engine (Rule-based + ML fallback). We must evaluate its accuracy across the 11 predefined categories.

### 1.1 Metrics
- **Precision, Recall, and F1-Score**: Computed per category (Food, Entertainment, Rent, etc.) and macro-averaged.
- **Coverage Ratio**: Percentage of transactions successfully categorized vs. those falling into `Others`.
- **Pipeline Contribution Ratio**: Percentage of transactions categorized by Layer 1 (Rules/RegEx) vs. Layer 2 (ML model).
- **Confidence Calibration**: Correlation between the ML model's confidence score and its actual accuracy (Expected: High confidence = High accuracy).

### 1.2 Evaluation Scenarios (from Edge Cases)
| Scenario | Expected Evaluation Outcome |
|---|---|
| Ambiguous Merchants (e.g., "Amazon" vs "Amazon Prime") | High precision on specific rules (Entertainment) over generic (Shopping). |
| Non-standard UPI Formats | Rule-based engine gracefully falls back to ML without crashing; ML maintains > 70% accuracy on unseen text. |
| Regional/Transliterated Text | Should confidently map to `Others` if untrainable, rather than misclassifying as `Food` or `Rent`. |
| Out-of-Vocabulary (OOV) Descriptions | ML model should not hallucinate categories; confidence score should be low (<0.4). |

---

## 2. Data Ingestion & Parsing Evaluation

Evaluates the robustness of the file upload and format auto-detection logic.

### 2.1 Metrics
- **Format Detection Accuracy**: Percentage of uploaded files correctly mapped to the right bank parser (HDFC, SBI, ICICI, etc.).
- **Data Yield**: Percentage of valid transaction rows successfully extracted and normalized compared to the total rows in the raw file.
- **Error Gracefulness**: Percentage of unsupported/corrupted files that yield a user-friendly error instead of a server crash (Target: 100%).

### 2.2 Evaluation Scenarios (from Edge Cases)
| Scenario | Expected Evaluation Outcome |
|---|---|
| Tie-breaker Detection | When column headers overlap (e.g., Kotak vs SBI), the secondary heuristics accurately distinguish them 100% of the time. |
| Malformed/Missing Dates | Parser flags invalid rows but processes the rest of the document successfully. |
| Mixed Delimiters/Encodings | Auto-detection successfully processes UTF-8, Latin-1, and BOM encodings without data loss. |

---

## 3. Analytics & Insights Evaluation

Evaluates the accuracy of the financial logic (Salary detection, Anomalies, Avoidability).

### 3.1 Metrics
- **Salary Detection Accuracy**: True Positive Rate (correctly identifying salary) and False Positive Rate (mislabeling large self-transfers or loans as salary).
- **Anomaly Detection Rate**: Percentage of accurately filtered non-standard expenses (Rent, EMI, Investments) from the daily average spend.
- **Avoidable Splitting Accuracy**: Baseline accuracy of default avoidable/unavoidable tags before user override.

### 3.2 Evaluation Scenarios (from Edge Cases)
| Scenario | Expected Evaluation Outcome |
|---|---|
| High-Variance Income (Freelancers) | System identifies recurring but variable credits as salary within a specified tolerance, or flags with low confidence. |
| Self-Transfers vs. Salary | System accurately differentiates a ₹5L self-transfer (NEFT) from a ₹1L salary credit. |
| Insight Edge Cases (e.g., Zero Spend) | System handles division by zero and zero-spend days gracefully without producing malformed insights. |

---

## 4. Human-in-the-Loop (HITL) Metrics

Since privacy is paramount and data is not sent back to a central server, we measure UX effectiveness through aggregate, anonymized session heuristics (if telemetry is ever opted-in) or during controlled UAT (User Acceptance Testing).

### 4.1 Metrics
- **Override Rate**: Percentage of transactions where the user manually toggles the `Avoidable` status or corrects a category. (Lower is better; Target: < 5%).
- **Time-to-Value (TTV)**: Average time from clicking "Upload" to viewing the fully rendered dashboard.
- **Export Utilization**: Percentage of sessions that end with the user exporting the enriched CSV, XLS, XLSX, TXT, Delimited file.

---

## 5. System Performance & Security Metrics

Evaluates the non-functional requirements vital for a local, privacy-first tool.

### 5.1 Metrics
- **End-to-End Latency**: Time taken to parse, categorize, and compute analytics for a 5,000-row statement. (Target: < 3 seconds).
- **Memory Footprint**: Peak RAM usage during the processing of a 50MB file. (Target: < 250MB to ensure smooth local running).
- **Session Cleanup Reliability**: 100% success rate in deleting SQLite records and temporary files after the `SESSION_EXPIRY_HOURS`.

### 5.2 Security Evals (from Edge Cases)
| Scenario | Expected Evaluation Outcome |
|---|---|
| Path Traversal / Malicious Files | System rejects `../../` filenames and safely sandboxes parsed data. |
| CSV Injection | Exported files prepend `'` to cells starting with `=`, `+`, `-`, `@`. |
| Cross-Session Isolation | UUIDs prevent user A from accessing user B's transaction data via API manipulation. |

---

## 6. Evaluation Datasets (Gold Standards)

To run these evaluations, the following offline datasets must be curated during Phase 1C:

1. **The Clean Dataset (1,000 txns)**: Perfectly formatted statements from all 5 supported banks. Used for baseline regression testing.
2. **The Edge Case Dataset (500 txns)**: Contains anomalies, missing dates, weird formatting, and regional text. Used to test robustness.
3. **The Categorization Gold Standard (2,000 txns)**: Manually labeled transactions spanning all 11 categories perfectly balanced. Used exclusively for cross-validation of the ML model and RegEx rules.
4. **The Security/Malware Dataset (20 files)**: Corrupted files, zip bombs, CSV injections, and password-protected Excels. Used to test the ingestion API's defense mechanisms.
