# Edge Cases: Privacy-First AI Bank Statement Analyzer

> Comprehensive edge case catalog derived from [context.md](file:///c:/Users/aksha/Downloads/PMF/bank%20statement%20analyser/context.md), [architecture.md](file:///c:/Users/aksha/Downloads/PMF/bank%20statement%20analyser/architecture.md), and [implementation_plan.md](file:///c:/Users/aksha/Downloads/PMF/bank%20statement%20analyser/implementation_plan.md)

---

## Table of Contents

1. [File Upload & Ingestion](#1-file-upload--ingestion)
2. [Bank Format Detection](#2-bank-format-detection)
3. [Data Parsing & Normalization](#3-data-parsing--normalization)
4. [Categorization Engine](#4-categorization-engine)
5. [Salary Auto-Detection](#5-salary-auto-detection)
6. [Anomaly Filtering](#6-anomaly-filtering)
7. [Avoidability Engine](#7-avoidability-engine)
8. [Fun Insights Generator](#8-fun-insights-generator)
9. [Analytics Computation](#9-analytics-computation)
10. [Human-in-the-Loop (Toggle Overrides)](#10-human-in-the-loop-toggle-overrides)
11. [API & Session Management](#11-api--session-management)
12. [Frontend & UI](#12-frontend--ui)
13. [Export](#13-export)
14. [Performance & Scale](#14-performance--scale)
15. [Security & Privacy](#15-security--privacy)
16. [ML Model](#16-ml-model)

---

## 1. File Upload & Ingestion

### 1.1 File Type & Format Issues

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 1.1.1 | **Empty file uploaded** (0 bytes) | Return `400` with message: "The uploaded file is empty." | 🔴 High |
| 1.1.2 | **File with only headers, no data rows** | Return `400` with message: "No transactions found in the file." | 🔴 High |
| 1.1.3 | **Non-CSV, XLS, XLSX, TXT, Delimited, XLS, XLSX, TXT, Delimited file with renamed extension** (e.g., a `.png` renamed to `.csv`) | Detect malformed content during parsing; return `400`: "File content does not match expected format." | 🔴 High |
| 1.1.4 | **Corrupted Excel file** (truncated / incomplete binary) | Catch `openpyxl` / `xlrd` exception; return `400`: "The file appears to be corrupted." | 🔴 High |
| 1.1.5 | **Password-protected Excel file** | `openpyxl` raises exception; return `400`: "Password-protected files are not supported." | 🟡 Medium |
| 1.1.6 | **File exceeds MAX_UPLOAD_SIZE_MB** (>50MB) | Reject before full read; return `413`: "File size exceeds the 50MB limit." | 🔴 High |
| 1.1.7 | **CSV, XLS, XLSX, TXT, Delimited with wrong delimiter** (semicolon `;`, tab `\t`, pipe `|` instead of comma) | Attempt auto-detection via `csv, xls, xlsx, txt, delimited.Sniffer` or Pandas `sep=None`; fall back to common delimiters. | 🟡 Medium |
| 1.1.8 | **Excel file with multiple sheets** | Use the first sheet by default; optionally prompt user to select. | 🟡 Medium |
| 1.1.9 | **Excel file where data starts on row 3+** (bank logo/headers in rows 1-2) | Scan for the first row that looks like column headers; skip preceding rows. | 🟡 Medium |
| 1.1.10 | **CSV, XLS, XLSX, TXT, Delimited with BOM (Byte Order Mark)** encoding | Use `encoding='utf-8-sig'` in Pandas `read_csv`. | 🟢 Low |
| 1.1.11 | **File with mixed encodings** (Latin-1 / Windows-1252 characters in descriptions) | Try UTF-8 first, fall back to `latin-1`; catch `UnicodeDecodeError`. | 🟡 Medium |
| 1.1.12 | **File with trailing empty rows/columns** | Strip trailing NaN rows and empty columns after reading. | 🟢 Low |
| 1.1.13 | **CSV, XLS, XLSX, TXT, Delimited with quoted fields containing commas** (e.g., `"Rent, June 2025"`) | Pandas handles this by default with `quotechar='"'`. Verify. | 🟢 Low |
| 1.1.14 | **Duplicate file upload** (same file uploaded twice) | Create separate sessions each time — no dedup; each upload is independent. | 🟢 Low |
| 1.1.15 | **File with `.xlsx` extension but actually `.xls` format (or vice versa)** | Catch engine mismatch error; retry with alternate engine. | 🟡 Medium |

### 1.2 Concurrency Issues

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 1.2.1 | **Multiple simultaneous uploads** from different browser tabs | Each gets its own session UUID; no cross-contamination. | 🟡 Medium |
| 1.2.2 | **User navigates away during upload** | Backend should clean up partial upload file; session remains incomplete. | 🟡 Medium |
| 1.2.3 | **Upload timeout** (very large file on slow connection) | Frontend shows timeout error; backend cleans up temp file. | 🟡 Medium |

---

## 2. Bank Format Detection

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 2.1 | **Completely unknown bank format** (none of the 5 parsers match) | Return user-friendly error: "We couldn't identify your bank format. Supported banks: HDFC, SBI, ICICI, Axis, Kotak." | 🔴 High |
| 2.2 | **Two banks score equally** in detection (e.g., Kotak and SBI both use `Date`, `Description`, `Debit`, `Credit`, `Balance`) | Use additional heuristics as tiebreaker: check date formats, specific keywords in descriptions, row patterns. | 🔴 High |
| 2.3 | **Column headers with extra whitespace or casing differences** (e.g., `"  Date  "`, `"DATE"`, `"date"`) | Normalize all headers: `strip().lower()` before matching. | 🟡 Medium |
| 2.4 | **Column headers in a regional language** (Hindi headers in some SBI exports) | Currently unsupported; return unknown format error. Document as known limitation. | 🟡 Medium |
| 2.5 | **Bank changed their CSV, XLS, XLSX, TXT, Delimited export format** (added/renamed columns in a new version) | Detection score drops below threshold; error returned. Fix: update parser definition. | 🟡 Medium |
| 2.6 | **Merged cells in Excel header row** | Pandas may read `NaN` for merged cells; handle gracefully by collapsing/skipping. | 🟡 Medium |
| 2.7 | **Credit card statement instead of bank account statement** | Different schema (no balance column, different narration format); may misdetect or fail. Clearly communicate: "Only savings/current account statements are supported." | 🟡 Medium |
| 2.8 | **Joint account statement** (two account holders) | Should work normally — same format as regular statement. No special handling needed. | 🟢 Low |
| 2.9 | **Statement from a bank with no parser** (e.g., Yes Bank, IndusInd) | Clear error message listing supported banks. Extensibility note in docs. | 🟡 Medium |
| 2.10 | **Custom/exported CSV, XLS, XLSX, TXT, Delimited from third-party apps** (e.g., Google Pay, PhonePe export) | Not a bank statement — detection should fail gracefully. Future: add parsers for payment app exports. | 🟢 Low |

---

## 3. Data Parsing & Normalization

### 3.1 Date Parsing

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 3.1.1 | **Ambiguous date format** — `01/02/2025` (Jan 2 or Feb 1?) | Use `dayfirst=True` for Indian bank statements (DD/MM/YYYY is standard). Document assumption. | 🔴 High |
| 3.1.2 | **Multiple date formats in same file** (e.g., `01-Jan-2025` and `01/01/2025` mixed) | Apply `pd.to_datetime` with `infer_datetime_format=True`; catch failures per row. | 🟡 Medium |
| 3.1.3 | **Date with time component** (`01/01/2025 14:30:00`) | Extract date part only; discard time. | 🟢 Low |
| 3.1.4 | **Invalid/missing dates** (`NaN`, empty string, `00/00/0000`) | Skip row or mark as invalid; don't crash. Log warning. | 🔴 High |
| 3.1.5 | **Future dates** (dates after today) | Allow but flag with a warning — could indicate bank processing lag or data error. | 🟢 Low |
| 3.1.6 | **Very old dates** (year 1900, Excel epoch issues) | Excel stores dates as numbers; `xlrd` / `openpyxl` can misinterpret. Validate date is within reasonable range (2000–current year). | 🟡 Medium |
| 3.1.7 | **Date column contains non-date text** (e.g., `"OPENING BALANCE"` in date field) | These are often header/summary rows injected by the bank. Detect and skip. | 🟡 Medium |

### 3.2 Amount Parsing

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 3.2.1 | **Amount with comma formatting** (`"1,25,000.50"` — Indian lakhs format) | Remove commas before parsing: `str.replace(',', '')`. | 🔴 High |
| 3.2.2 | **Amount as negative number** for debits (`-450.00`) | Take absolute value and set `type = DEBIT`. | 🟡 Medium |
| 3.2.3 | **Amount with currency symbol** (`"₹450.00"`, `"INR 450"`, `"Rs.450"`) | Strip currency symbols/prefixes before parsing. | 🟡 Medium |
| 3.2.4 | **Zero amount transactions** (`0.00`) | Keep in dataset — could be fee waivers or statement markers. Don't exclude. | 🟢 Low |
| 3.2.5 | **Very large amounts** (>₹1 crore / 10 million) | No special handling — but ensure chart Y-axis scales correctly. | 🟢 Low |
| 3.2.6 | **Amount field contains text** (e.g., `"N/A"`, `"---"`, `"Nil"`) | Parse as `NaN`; skip transaction or set amount to 0 with warning. | 🟡 Medium |
| 3.2.7 | **Both debit and credit columns have values in the same row** | Shouldn't happen normally — if it does, treat as two separate transactions or prioritize whichever is non-zero. | 🟡 Medium |
| 3.2.8 | **Fractional paisa amounts** (`₹0.01`, `₹0.50`) | Support — valid micro-transactions (bank interest, rounding). | 🟢 Low |
| 3.2.9 | **Amount in scientific notation** (`1.5E+04`) | `pd.to_numeric` handles this by default. Verify. | 🟢 Low |

### 3.3 Description / Narration Parsing

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 3.3.1 | **Empty description** (blank narration field) | Set description to `"Unknown Transaction"`. Categorize as `Others`. | 🟡 Medium |
| 3.3.2 | **Description is just a transaction ID** (e.g., `"TXN20250615001"`) | No meaningful text to categorize → ML fallback → likely `Others`. | 🟢 Low |
| 3.3.3 | **Very long description** (200+ characters, some banks include full address) | Truncate for display (UI), but use full text for categorization. | 🟢 Low |
| 3.3.4 | **Description with special characters** (`/`, `-`, `@`, `*`, Unicode) | Don't strip before categorization — UPI patterns use `/` and `@`. Only clean for ML preprocessing. | 🟡 Medium |
| 3.3.5 | **Description in regional language** (Hindi, Tamil, etc.) | ML model may not handle — classify as `Others`. Future: multilingual model. | 🟡 Medium |
| 3.3.6 | **Multi-line description** (newlines embedded in CSV, XLS, XLSX, TXT, Delimited field) | Collapse to single line (replace `\n` with space). | 🟢 Low |
| 3.3.7 | **Description that matches multiple categories** (e.g., `"Amazon Prime Video"` → Shopping or Entertainment?) | First rule match wins. Ensure merchant dict ordering prioritizes specific matches: `"prime video" → Entertainment` before `"amazon" → Shopping`. | 🟡 Medium |

### 3.4 Balance Column

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 3.4.1 | **No balance column in the file** | Set `balance = None` for all rows. Dashboard skips balance-related features. | 🟡 Medium |
| 3.4.2 | **Balance doesn't reconcile** (previous balance ± amount ≠ next balance) | Don't validate reconciliation — user may have partial statement. | 🟢 Low |
| 3.4.3 | **Negative balance** (overdraft) | Support negative balance values. Display correctly in UI. | 🟢 Low |
| 3.4.4 | **Balance resets mid-file** (statement crosses fiscal year or account change) | Ignore — treat each transaction independently. | 🟢 Low |

---

## 4. Categorization Engine

### 4.1 UPI Parser Edge Cases

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 4.1.1 | **Non-standard UPI format** (`"UPI 450.00 SWIGGY"` instead of `"UPI/SWIGGY@bank/TXN"`) | Fallback to merchant keyword match on full description string. | 🟡 Medium |
| 4.1.2 | **UPI payee is a person's name** (not a merchant) (e.g., `"UPI/RAHUL SHARMA@upi/"`) | No merchant match → ML fallback → likely `Others` or `Self-Transfers`. | 🟡 Medium |
| 4.1.3 | **UPI payee name is abbreviated** (`"SWGY"` instead of `"SWIGGY"`) | Exact keyword match fails; ML model should catch it if trained on variants. | 🟡 Medium |
| 4.1.4 | **Multiple UPI transactions to same payee** | All should get the same category — consistency check. | 🟢 Low |
| 4.1.5 | **UPI reversal/refund** (`"UPI/CR/REFUND/..."`) | Should be tagged as `CREDIT`. Category should match original transaction's category if possible, otherwise `Others`. | 🟡 Medium |
| 4.1.6 | **UPI with VPA containing numbers** (`"merchant123@bank"`) | Regex should handle numeric characters in payee name. | 🟢 Low |
| 4.1.7 | **Google Pay / PhonePe format differences** | Different prefixes (`GPay/`, `PhonePe/`) — ensure regex handles all variants. | 🟡 Medium |

### 4.2 Merchant Dictionary Edge Cases

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 4.2.1 | **Merchant name is a substring of another** (`"ola"` matching `"COLA"` or `"SCHOLARSHIP"`) | Use word boundary matching or context: `\bola\b` instead of plain `"ola" in desc`. | 🔴 High |
| 4.2.2 | **New/unknown merchant** not in dictionary | Falls through to ML classifier. | 🟡 Medium |
| 4.2.3 | **Merchant name in ALL CAPS** (`"NETFLIX"` vs `"netflix"`) | Case-insensitive matching (already handled via `.lower()`). | 🟢 Low |
| 4.2.4 | **Merchant with typo in bank narration** (`"AMAZN"`, `"NETFLX"`) | Exact match fails; ML model may catch. Consider fuzzy matching as enhancement. | 🟡 Medium |
| 4.2.5 | **Same merchant across categories** (Amazon sells groceries, electronics, and entertainment) | Default to `Shopping`. User can override via toggle. Document limitation. | 🟡 Medium |
| 4.2.6 | **Merchant dictionary has overlapping keywords** (`"amazon prime" → Entertainment` vs `"amazon" → Shopping`) | Ensure longer/more-specific keywords are checked first (sort by length descending). | 🔴 High |

### 4.3 Rule-Based Pattern Edge Cases

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 4.3.1 | **NEFT to a merchant (not self-transfer)** (`"NEFT/LANDLORD/RENT"`) | Initial rule tags as `Self-Transfers`, but merchant dict should override to `Rent`. Ensure pipeline priority: UPI → Merchant Dict → Pattern Rules (not pattern rules first). | 🔴 High |
| 4.3.2 | **ATM withdrawal description varies by bank** (`"ATM WDR"`, `"ATM CASH"`, `"CW ATM"`, `"ATM/CASH WITHDRAWAL"`) | RegEx pattern must cover all variants. | 🟡 Medium |
| 4.3.3 | **Interest credit** (`"INT PAID"`, `"INTEREST CREDIT"`) | Tag as `Salary/Income` (passive income) or create separate `Interest` sub-category under `Others`. | 🟡 Medium |
| 4.3.4 | **Cash deposit** (`"CASH DEP"`, `"CDM DEPOSIT"`) | Credit type. Not salary. Tag as `Others` or `Self-Transfers`. | 🟢 Low |
| 4.3.5 | **Cheque transaction** (`"CHQ DEP"`, `"CHQ PAID"`) | Handle both cheque deposits (credit) and cheque payments (debit). Category depends on payee if available. | 🟢 Low |

### 4.4 ML Classifier Edge Cases

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 4.4.1 | **ML model file not found** (`.pkl` missing or corrupted) | Log error; fall back to rule-based only. Don't crash. Return `Others` for unmatched. | 🔴 High |
| 4.4.2 | **ML predicts with very low confidence** (<30%) | Set category but flag low confidence. UI could show "?" indicator. | 🟡 Medium |
| 4.4.3 | **Description language the model wasn't trained on** (Hindi, transliterated Hindi) | ML returns low-confidence garbage. Fallback to `Others`. | 🟡 Medium |
| 4.4.4 | **Very short description** (1–2 words, e.g., `"PAYMENT"`) | TF-IDF sparse vector; low-confidence prediction likely. | 🟡 Medium |
| 4.4.5 | **Description identical to a training sample** | Should predict correctly with high confidence. Not really an edge case but worth verifying (no overfitting). | 🟢 Low |
| 4.4.6 | **New category emerges** that model wasn't trained for (e.g., `Healthcare`) | Model forces into nearest known category. Fix: retrain with new category. | 🟡 Medium |

---

## 5. Salary Auto-Detection

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 5.1 | **No credits in the statement** (debit-only) | No salary detected; `detected_salary = null`. Dashboard shows "No income detected." | 🟡 Medium |
| 5.2 | **Multiple salary credits in one month** (base + variable pay, split payroll) | Detect both if they are the top 2 recurring credits. Sum as total salary. | 🟡 Medium |
| 5.3 | **Salary amount varies each month** (freelancer, commission-based) | Tolerance-based matching (±5%). If variance is too high, may miss detection. Flag: "Possible salary detected with low confidence." | 🟡 Medium |
| 5.4 | **Self-transfer is larger than salary** (user transferred ₹5L from another account) | Should NOT be tagged as salary. Cross-check: exclude known self-transfer patterns before salary detection. | 🔴 High |
| 5.5 | **Loan disbursement as large credit** (₹10L home loan credited) | Could be misdetected as salary. Heuristic: one-time large credits that don't repeat are not salary. | 🔴 High |
| 5.6 | **Single month data** — no recurrence signal | Use largest credit as "probable salary" with lower confidence. | 🟡 Medium |
| 5.7 | **Salary paid on different dates each month** (25th, 28th, 1st) | Group by month, not by date. Should still detect if amounts are similar. | 🟢 Low |
| 5.8 | **Statement has only 1 week of data** | Very few transactions; salary may not appear. Skip salary detection gracefully. | 🟡 Medium |
| 5.9 | **Multiple recurring credits of similar amounts** (salary + rental income) | Both could be flagged. Limit to top 2-3 recurring credits. | 🟡 Medium |
| 5.10 | **Salary comes via NEFT/IMPS, not UPI** | Description may say `"NEFT CR COMPANY NAME SALARY"`. Keyword "SALARY" in description is a strong signal — use it as a prioritized rule. | 🟡 Medium |

---

## 6. Anomaly Filtering

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 6.1 | **All transactions are in anomaly categories** (only rent + investments) | Average daily spend = ₹0. Dashboard shows "No regular daily expenses found." | 🟡 Medium |
| 6.2 | **No transactions in anomaly categories** | All transactions included in average — no filtering needed. | 🟢 Low |
| 6.3 | **Category misclassified** — real daily expense tagged as `Investments` | Average daily spend will be slightly off. User can re-categorize via toggle to fix. | 🟡 Medium |
| 6.4 | **Self-transfer followed by immediate spend** (user transfers to wallet → spends from wallet) | Transfer is filtered; wallet spend may not appear if it's from a different account. Partial view is expected. | 🟢 Low |
| 6.5 | **Only 1 day of data** | Average daily spend = that day's total. Not very meaningful — add disclaimer. | 🟡 Medium |
| 6.6 | **Month with zero spending days** (e.g., holidays) | Divide by actual days with transactions, not calendar days. Decide: calendar days vs active days. | 🟡 Medium |

---

## 7. Avoidability Engine

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 7.1 | **Category is `Others` — avoidable or unavoidable?** | Default to `Avoidable`. User can override. | 🟢 Low |
| 7.2 | **Food could be groceries (unavoidable) or dining out (avoidable)** | Default to `Avoidable`. Cannot distinguish without sub-categories. Document as limitation. | 🟡 Medium |
| 7.3 | **Medical/healthcare expense** — currently has no category | Falls under `Others` → tagged `Avoidable`. **This is incorrect.** Consider adding `Healthcare` as unavoidable category. | 🟡 Medium |
| 7.4 | **Insurance premium** — no explicit category | Falls under `Others` or `EMI/Loans`. Should be `Unavoidable`. Add insurance to pattern rules. | 🟡 Medium |
| 7.5 | **User toggles avoidable, then re-uploads file** | New session is created; old overrides don't carry over. Each session is independent. | 🟡 Medium |
| 7.6 | **Credit transactions** (income) | `is_avoidable` should be `false` / not applicable for credits. Don't show toggle for credit rows. | 🟡 Medium |
| 7.7 | **100% of spend is avoidable** | Pie chart shows 100% avoidable, 0% unavoidable. Handle: don't render an empty segment. | 🟢 Low |
| 7.8 | **100% of spend is unavoidable** | Same — handle empty avoidable segment in chart. | 🟢 Low |

---

## 8. Fun Insights Generator

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 8.1 | **Too few transactions** (<5) to generate meaningful insights | Show fewer insights or a message: "Upload a larger statement for more insights!" | 🟡 Medium |
| 8.2 | **All transactions are the same amount** (e.g., recurring ₹500 SIP) | Mode = ₹500. Insight: "All your transactions this month were ₹500!" Not very "fun" — skip or rephrase. | 🟢 Low |
| 8.3 | **No mode** — all amounts are unique | `mode()` returns the first value or NaN. Skip "most common amount" insight. | 🟡 Medium |
| 8.4 | **Only credits, no debits** | Spending insights don't apply. Show income-focused insights: "Your total income was ₹X this month." | 🟡 Medium |
| 8.5 | **Single day of data** | "Top spending day of week" = that day. Insight is trivially true — skip it. | 🟢 Low |
| 8.6 | **Salary is ₹0** (not detected) | Salary allocation ratio can't be computed. Skip "X% of salary went to…" insight. | 🟡 Medium |
| 8.7 | **All spending on one category** | "You spent 100% on Food!" — valid but might look like a bug. Add context: "across {N} transactions." | 🟢 Low |
| 8.8 | **Weekend has zero spending** | "You spent ₹0 on weekends" — valid insight, but rephrase: "You didn't spend anything on weekends this month! 🎉" | 🟢 Low |
| 8.9 | **Division by zero** in percentage calculations (salary = 0, total = 0) | Guard all divisions with `if denominator > 0` checks. Return empty insights if data is insufficient. | 🔴 High |
| 8.10 | **Very large insight text** (long merchant name or large numbers) | Truncate merchant names; format large numbers with lakhs/crore notation (₹1.5L). | 🟢 Low |

---

## 9. Analytics Computation

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 9.1 | **Statement spans multiple months** (e.g., Jan–Mar) | Compute monthly breakdown for each month. Charts should show multi-month timeline. | 🟡 Medium |
| 9.2 | **Statement has 1 transaction** | All aggregations are trivial. Summary shows totals = that transaction. Charts have 1 data point. | 🟡 Medium |
| 9.3 | **All transactions are credits** (income-only statement) | `total_expense = 0`, `savings_rate = 100%`, no spending charts. Handle gracefully. | 🟡 Medium |
| 9.4 | **All transactions are debits** (expense-only statement) | `total_income = 0`, `savings_rate = -∞` → cap at 0% or show "No income detected." | 🟡 Medium |
| 9.5 | **Negative savings** (spent more than earned) | `net_savings = negative`. Show in red. `savings_rate = negative %`. Display correctly. | 🟡 Medium |
| 9.6 | **Extremely high transaction count** (5000+ transactions) | Analytics computation may be slow. Use chunked processing. Consider progress indicator. | 🟡 Medium |
| 9.7 | **Date gaps in data** (transactions on day 1, 5, 15, 28 — nothing in between) | Time-series chart should show zero-spend on missing days (fill gaps) or connect points. Design choice. | 🟡 Medium |
| 9.8 | **Category breakdown has 0 in every category** | All transactions uncategorized → everything is `Others`. Charts should still render. | 🟢 Low |
| 9.9 | **Analytics cache invalidation** — user toggles avoidable, old cache serves stale data | On PATCH toggle → invalidate and recompute affected cache keys (avoidable_split, insights). | 🔴 High |
| 9.10 | **Concurrent analytics computation** (user requests analytics while background processing is still running) | Return `202 Accepted` with "still processing" status, or block until ready. | 🟡 Medium |

---

## 10. Human-in-the-Loop (Toggle Overrides)

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 10.1 | **User rapidly toggles the same transaction** multiple times | Debounce API calls (frontend); only send final state. Backend handles idempotent PATCH. | 🟡 Medium |
| 10.2 | **User toggles all transactions to avoidable** | Valid user choice. Dashboard shows 100% avoidable. No error. | 🟢 Low |
| 10.3 | **Toggle request for non-existent transaction ID** | Return `404`: "Transaction not found." | 🟡 Medium |
| 10.4 | **Toggle request for a different session's transaction** | Validate `session_id` matches `transaction.session_id`. Return `403` if mismatch. | 🔴 High |
| 10.5 | **User toggles a credit transaction** | Credits shouldn't have avoidable toggles. Frontend should hide toggle for credits. Backend rejects with `400`. | 🟡 Medium |
| 10.6 | **Session expired but user still has the page open** | Return `410 Gone`: "This session has expired. Please upload a new file." | 🟡 Medium |
| 10.7 | **Optimistic UI update fails** (network error) | Revert toggle state in frontend; show error toast: "Failed to update. Please try again." | 🟡 Medium |

---

## 11. API & Session Management

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 11.1 | **Request with invalid session_id** (malformed UUID) | Return `400`: "Invalid session ID format." | 🟡 Medium |
| 11.2 | **Request with non-existent session_id** | Return `404`: "Session not found." | 🟡 Medium |
| 11.3 | **Expired session accessed** | Return `410 Gone`. Clean up DB records on next scheduled cleanup. | 🟡 Medium |
| 11.4 | **Session cleanup deletes active session** (user is still using it) | Only cleanup sessions older than `SESSION_EXPIRY_HOURS`. Extend expiry on every API access. | 🔴 High |
| 11.5 | **SQLite concurrent write locks** | SQLite handles single-writer. Use connection pooling with `check_same_thread=False`. For high concurrency, queue writes. | 🟡 Medium |
| 11.6 | **Database file is locked** (another process accessing `.db`) | Catch `sqlite3.OperationalError`; retry with backoff or return `503`. | 🟡 Medium |
| 11.7 | **Disk full — can't write to SQLite or upload dir** | Catch `IOError`; return `507`: "Server storage is full." | 🔴 High |
| 11.8 | **API receives malformed JSON** in PATCH request | Pydantic validation → `422 Unprocessable Entity` with field-level errors. | 🟢 Low |
| 11.9 | **Pagination: page number exceeds total pages** | Return empty transactions list with `total` and `page` metadata. | 🟢 Low |
| 11.10 | **Pagination: negative page or size** | Validate: `page >= 1`, `1 <= size <= 200`. Return `400` if invalid. | 🟢 Low |

---

## 12. Frontend & UI

### 12.1 Chart Rendering

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 12.1.1 | **Empty data for charts** (no transactions after filtering) | Show "No data to display" placeholder inside chart container. Don't render empty SVG. | 🟡 Medium |
| 12.1.2 | **Single data point in time-series** | Show a dot instead of a line. Or show bar chart for single point. | 🟢 Low |
| 12.1.3 | **Too many categories in pie chart** (11 slices) | Group small categories (<2%) into "Others" for chart clarity. Show full breakdown in table. | 🟢 Low |
| 12.1.4 | **Very long category names in chart legend** | Truncate with ellipsis in legend; show full name on hover tooltip. | 🟢 Low |
| 12.1.5 | **Chart renders before data arrives** | Show loading skeleton / shimmer effect while API call is in flight. | 🟡 Medium |
| 12.1.6 | **Chart data updates after toggle** | Recharts should re-render when props change. Verify smooth transition without flicker. | 🟡 Medium |
| 12.1.7 | **Negative values in chart** (negative savings) | Recharts handles negative Y-axis. Verify bars/lines render below zero line correctly. | 🟡 Medium |

### 12.2 Responsive Design

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 12.2.1 | **Mobile screen (<480px)** | Single column layout. Charts stack vertically. Table scrolls horizontally. | 🟡 Medium |
| 12.2.2 | **Very wide screen (>2560px / 4K)** | Content should be max-width constrained (e.g., 1400px centered). Don't stretch full width. | 🟢 Low |
| 12.2.3 | **Table on small screen** — too many columns | Prioritize: Date, Description, Amount, Category. Hide Method and Balance on mobile. | 🟡 Medium |
| 12.2.4 | **Touch device** — toggle switch usability | Toggle should be large enough for finger tap (min 44x44px touch target). | 🟡 Medium |
| 12.2.5 | **User zooms browser to 200%** | Layout should not break. Use relative units (rem, %, vw/vh). | 🟢 Low |

### 12.3 Navigation & State

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 12.3.1 | **User navigates to `/dashboard` without uploading** | Redirect to `/` (Upload page). Show message: "Please upload a statement first." | 🔴 High |
| 12.3.2 | **User refreshes dashboard page** (F5) | Session ID should persist (localStorage or URL param). Re-fetch analytics from API. | 🔴 High |
| 12.3.3 | **User presses browser back button** from dashboard | Navigate to upload page. Optionally: confirm "Leave analysis?" | 🟡 Medium |
| 12.3.4 | **User opens multiple tabs** with same session | Both tabs should work independently against the same session. | 🟢 Low |
| 12.3.5 | **User has JavaScript disabled** | App won't work at all (React SPA). Show `<noscript>` message. | 🟢 Low |
| 12.3.6 | **Slow network / API timeout** on dashboard load | Show loading state for 10s, then error: "Analysis is taking longer than expected. Please try again." | 🟡 Medium |

---

## 13. Export

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 13.1 | **Export with zero transactions** (all filtered out) | Return empty CSV, XLS, XLSX, TXT, Delimited with headers only. Or `404` with message. | 🟢 Low |
| 13.2 | **Exported CSV, XLS, XLSX, TXT, Delimited has Unicode characters** (₹ symbol, Hindi text) | Use UTF-8 encoding with BOM for Excel compatibility: `encoding='utf-8-sig'`. | 🟡 Medium |
| 13.3 | **Description contains commas** | CSV, XLS, XLSX, TXT, Delimited properly quotes fields containing commas. Pandas `to_csv` handles this. | 🟢 Low |
| 13.4 | **Very large export** (10K+ transactions) | Should still work — CSV, XLS, XLSX, TXT, Delimited is lightweight. Add Content-Length header for download progress. | 🟢 Low |
| 13.5 | **User clicks export multiple times rapidly** | Debounce button; disable during download. Each click returns the same CSV, XLS, XLSX, TXT, Delimited. | 🟢 Low |
| 13.6 | **Exported CSV, XLS, XLSX, TXT, Delimited opened in Excel misinterprets dates** | Force date format to `YYYY-MM-DD` in export to avoid Excel's locale-dependent date parsing. | 🟡 Medium |
| 13.7 | **Filename collision on download** | Generate unique filename: `{bank_name}_statement_analyzed_{session_id_short}.csv`. | 🟢 Low |

---

## 14. Performance & Scale

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 14.1 | **File with 50,000+ transactions** (enterprise-scale) | Use Pandas chunked reading. Consider async processing with status polling. | 🟡 Medium |
| 14.2 | **ML inference bottleneck** — 5000 transactions × ML predict | Batch vectorization: `vectorizer.transform(all_descriptions)` then `model.predict(batch)`. NOT one-by-one. | 🔴 High |
| 14.3 | **SQLite bloat** — many sessions accumulate over time | Background cleanup job deletes expired sessions + orphaned records. | 🟡 Medium |
| 14.4 | **Temp upload files not cleaned up** | Delete temp file after parsing completes (success or failure). Add cleanup on startup. | 🟡 Medium |
| 14.5 | **Frontend renders 5000 rows in transaction table** | Virtual scrolling with `react-window`. Don't render all DOM nodes. | 🔴 High |
| 14.6 | **Chart re-renders on every state change** | Memoize chart components with `React.memo`. Only re-render when chart data actually changes. | 🟡 Medium |
| 14.7 | **ML model load time on startup** | Load model in `lifespan` startup event. First request should not pay loading cost. If model is large, log warning. | 🟡 Medium |
| 14.8 | **Pandas memory usage** for large DataFrames | Use appropriate dtypes (`category` for type column, `float32` for amounts). | 🟢 Low |

---

## 15. Security & Privacy

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 15.1 | **Path traversal in uploaded filename** (`"../../etc/passwd.csv"`) | Sanitize filename: use `secure_filename()` or generate UUID-based name. Never use user-provided filename for storage path. | 🔴 Critical |
| 15.2 | **Malicious CSV, XLS, XLSX, TXT, Delimited** (CSV, XLS, XLSX, TXT, Delimited injection — formulas like `=CMD(...)`) | Export protection: prepend `'` to cells starting with `=`, `+`, `-`, `@` in exported CSV, XLS, XLSX, TXT, Delimited. Ingestion: Pandas reads as strings, no formula execution. | 🔴 Critical |
| 15.3 | **CORS bypass attempt** | FastAPI CORS middleware restricts to `localhost:5173`. Reject cross-origin requests from unknown origins. | 🔴 High |
| 15.4 | **Session ID guessing** (sequential IDs) | Use UUID4 — cryptographically random, infeasible to guess. | 🔴 High |
| 15.5 | **Uploaded file contains malware** (not actually a bank statement) | File is only parsed with Pandas (no execution). Risk is minimal but validate file type and size. | 🟡 Medium |
| 15.6 | **Sensitive data in server logs** | Don't log transaction descriptions, amounts, or file contents. Log only session IDs, counts, and errors. | 🔴 High |
| 15.7 | **Data persists after session expires** | Cleanup job must delete: DB records (session + transactions + cache) + temp upload files. | 🔴 High |
| 15.8 | **SQLite DB file accessible from browser** | Serve from `data/` directory which is NOT in `public/` or served by the frontend. Backend only. | 🔴 High |
| 15.9 | **Zip bomb disguised as Excel** (.xlsx is a ZIP) | Validate file size before and after extraction. Set parsing timeout. | 🟡 Medium |
| 15.10 | **Request body too large** (non-file POST body) | FastAPI max body size config. Reject payloads > reasonable limit. | 🟡 Medium |

---

## 16. ML Model

| # | Edge Case | Expected Behavior | Severity |
|---|---|---|---|
| 16.1 | **Model version mismatch** (scikit-learn upgraded, `.pkl` incompatible) | Catch `ModuleNotFoundError` or `UnpicklingError`. Log clear message: "ML model is incompatible with current scikit-learn version. Retrain required." Fall back to rule-based only. | 🔴 High |
| 16.2 | **Model file tampered with** (corrupted `.pkl`) | Catch unpickling error. Fall back to rule-based only. | 🟡 Medium |
| 16.3 | **TF-IDF vectorizer and classifier mismatch** (trained separately with different data) | Feature dimension mismatch → error during `predict`. Validate dimensions on load. | 🔴 High |
| 16.4 | **Training data heavily imbalanced** (90% Food, 5% Rent, 5% Others) | Model will over-predict `Food`. Use class weights or SMOTE during training. Validate with confusion matrix. | 🟡 Medium |
| 16.5 | **Zero-length input to classifier** (empty string after preprocessing) | `TfidfVectorizer.transform([""])` returns zero vector. Model predicts, likely low confidence. Guard against. | 🟡 Medium |
| 16.6 | **Input contains only stop words / noise** (e.g., `"UPI CR DR"`) | After preprocessing removes noise words → empty. Same as 16.5. | 🟡 Medium |
| 16.7 | **Prediction returns category not in the known category list** | Shouldn't happen if model is trained properly. Add assertion check; fall back to `Others`. | 🟢 Low |

---

## Summary: Severity Distribution

| Severity | Count | Action |
|---|---|---|
| 🔴 **Critical** | 2 | Must fix before any release — security vulnerabilities |
| 🔴 **High** | 20 | Must handle in MVP — causes crashes, data corruption, or wrong results |
| 🟡 **Medium** | 63 | Should handle in MVP — degrades UX or produces misleading output |
| 🟢 **Low** | 30 | Nice to have — cosmetic or unlikely scenarios |
| **Total** | **115** | |

---

## Recommended Priority Order

### Must Handle Before MVP Launch (Critical + High)

1. **15.1** — Path traversal in filenames
2. **15.2** — CSV, XLS, XLSX, TXT, Delimited injection protection
3. **1.1.1** — Empty file upload
4. **1.1.4** — Corrupted file handling
5. **2.1** — Unknown bank format error messaging
6. **2.2** — Ambiguous bank format tiebreaker
7. **3.1.1** — Ambiguous date format (DD/MM vs MM/DD)
8. **3.2.1** — Indian comma-formatted amounts
9. **4.2.1** — Substring matching false positives (`"ola"` in `"scholarship"`)
10. **4.2.6** — Overlapping merchant keywords priority
11. **4.3.1** — NEFT to merchant misclassified as self-transfer
12. **4.4.1** — Missing ML model file graceful fallback
13. **5.4** — Self-transfer > salary misdetection
14. **5.5** — Loan disbursement misdetected as salary
15. **8.9** — Division by zero in insights
16. **9.9** — Analytics cache invalidation on toggle
17. **10.4** — Cross-session transaction toggle
18. **11.4** — Session cleanup vs active session
19. **12.3.1** — Direct URL to dashboard without upload
20. **12.3.2** — Page refresh loses session
21. **14.2** — ML batch inference (not one-by-one)
22. **14.5** — Virtual scrolling for large tables
