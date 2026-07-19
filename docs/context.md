# Context: Privacy-First AI Bank Statement Analyzer

## 1. Project Overview

A **privacy-focused bank statement analyzer** that ingests raw CSV, XLS, XLSX, TXT, Delimited, XLS, XLSX, TXT, Delimited bank statements, auto-detects the bank format, categorizes transactions using **rule-based logic** and **local/in-memory ML** (no external API calls), and delivers interactive spending dashboards with behavioral insights. All user data stays local — zero data is sent to cloud LLMs.

### Core Value Proposition
- **Privacy-first**: No bank account linking, no third-party cloud LLM calls. All processing is offline/local.
- **Zero friction**: Auto-detects bank format from uploaded file — no manual configuration.
- **Actionable insights**: Interactive dashboards, fun behavioral facts, and avoidable/unavoidable spend breakdowns.
- **Human-in-the-loop**: Users can manually override AI categorizations.

---

## 2. Target Users

| Persona | Status | Description |
|---|---|---|
| **Retail Users** | ✅ Primary (Phase 1) | Privacy-conscious individuals tracking monthly cash flow without sharing bank credentials. |
| **Enterprise Users** | 🔜 Upcoming (Phase 2) | Finance teams / auditors analyzing enterprise fund movements and macro-spending trends. |
| **Risk & Compliance** | 🔜 Upcoming (Phase 3) | Analysts detecting individual or corporate financial fraud patterns. |

---

## 3. System Workflow & Modules

### Module 1: Data Ingestion & Preprocessing

**Goal:** Accept raw bank statements and normalize them into a standard schema.

- **Input Formats:** CSV, XLS, XLSX, TXT, Delimited, Excel (`.csv`, `.xls`, `.xlsx`)
- **Auto-Detection Logic:**
  - Identify the bank (e.g., HDFC, SBI, ICICI, Axis, Kotak, etc.) by inspecting **column headers** and **data structures/patterns**.
  - Normalize all formats into a **standard internal schema**:
    | Field | Type | Description |
    |---|---|---|
    | `date` | Date | Transaction date |
    | `description` | String | Raw transaction narration/description |
    | `amount` | Float | Transaction amount |
    | `type` | Enum | `CREDIT` or `DEBIT` |
    | `balance` | Float | Running balance (if available) |
- **Future Scope (PDF):** Integration of AI frameworks (LangGraph / document parsers) to extract tabular data from PDF bank statements.

### Module 2: Categorization Engine (Privacy-First)

**Goal:** Classify each transaction into a spending category — entirely offline.

#### Layer 1 — Rule-Based Logic (RegEx)
- Parse known **UPI formats** to extract payee names (e.g., `UPI/merchant@bank/txnid`).
- Match merchant names against a curated keyword dictionary.
- Handle common patterns: ATM withdrawals, NEFT/RTGS/IMPS transfers, EMI debits, etc.

#### Layer 2 — Local ML Model
- **Model choices** (lightweight, offline):
  - scikit-learn Naive Bayes / SVM
  - SpaCy text classifier
  - Small local transformer (e.g., DistilBERT fine-tuned)
- **Training data:** Labeled transaction descriptions → categories.
- **Categories:**
  | Category | Examples |
  |---|---|
  | Food | Swiggy, Zomato, restaurant UPI payments |
  | Entertainment | Netflix, BookMyShow, gaming |
  | Investments | Mutual funds, stocks, FD |
  | Rent | Monthly rent transfers |
  | Self-Transfers | Own account transfers, savings sweeps |
  | Utilities | Electricity, water, internet, phone recharge |
  | Transport | Uber, Ola, fuel, metro |
  | Shopping | Amazon, Flipkart, retail stores |
  | EMI/Loans | EMI debits, loan repayments |
  | Salary/Income | Salary credits |
  | Others | Uncategorized |

- **Key constraint:** Zero data is sent to external APIs (OpenAI, Groq, etc.).

### Module 3: Analytics & Insights Layer

**Goal:** Derive meaningful financial insights from categorized data.

#### 3a. Salary Auto-Detection
- Programmatically identify the **largest incoming credit(s)** of each month.
- Tag as baseline **Salary/Income**.
- Support multiple salary credits (split payroll, bonuses).

#### 3b. Anomaly Filtering
- Exclude **non-standard expenses** from "average daily spend" calculations:
  - Rent (large, one-time monthly)
  - Self-transfers (not real expenses)
  - Investments (savings, not spending)
  - EMIs (fixed obligations)
- Prevents these from skewing daily/weekly average metrics.

#### 3c. Avoidability Engine
- **Auto-flag** categories:
  - `Avoidable`: Entertainment, Food (dining out), Shopping
  - `Unavoidable`: Rent, Utilities, EMI, Insurance
- **Human-in-the-Loop override**: Users can toggle any individual transaction's avoidable/unavoidable status via the UI.

#### 3d. Fun Insights / Behavioral Facts
- Generate personalized, quirky text snippets:
  - *"₹850 is your most common transaction amount this month!"*
  - *"35% of your salary income went strictly toward rent and investments."*
  - *"You spent on Food the most on Sundays!"*
  - *"On the 8th of the month you spent the most."*
- Insights are computed from patterns: mode amounts, day-of-week trends, category ratios, peak spending dates, streaks, etc.

### Module 4: Advanced Modules (Placeholders — Future Phases)

#### 4a. Enterprise Statement Analysis (Phase 2)
- Dedicated B2B view for:
  - Cash flow tracking
  - Vendor payment analysis
  - Fund movement across multiple accounts
  - Macro-spending trend reports

#### 4b. Fraud Analysis Module (Phase 3)
- Detect suspicious anomalies:
  - Repetitive micro-transactions
  - Unusual late-night UPI transfers
  - Mismatched payee details
  - Cyclic money laundering patterns
- Applicable to both individual and enterprise users.

### Module 5: Output & UI Display

#### 5a. Dashboard Visualizations
- **Time-series chart:** Spending mapped across the month (line/bar chart by day/week).
- **Pie/donut chart:** Avoidable vs. Unavoidable spend breakdown.
- **Category breakdown chart:** Spend per category (bar/pie).
- **Income vs. Expense summary cards.**
- **Monthly trend comparison** (if multi-month data is uploaded).

#### 5b. Fun Insights Card
- A dedicated UI card/section that surfaces the behavioral insights (see 3d above).

#### 5c. Avoidable/Unavoidable Toggle
- Interactive table/list of transactions where users can manually toggle the flag.
- Dashboard updates dynamically on toggle.

#### 5d. Export
- Downloadable **CSV, XLS, XLSX, TXT, Delimited file** of the categorized and enriched statement (with categories, avoidable flags, etc.).

---

## 4. Technical Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (UI)                     │
│  Upload → Dashboard → Insights → Export             │
│  (React / Next.js / Vite + Charts library)          │
└──────────────────────┬──────────────────────────────┘
                       │ REST API / Local bridge
┌──────────────────────▼──────────────────────────────┐
│                  Backend / Core                     │
│  ┌──────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │ Ingestion│ │Categorization│ │   Analytics &   │ │
│  │ & Parser │→│   Engine     │→│   Insights      │ │
│  └──────────┘ └──────────────┘ └─────────────────┘ │
│                                                     │
│  ┌────────────────────┐  ┌────────────────────────┐ │
│  │ Enterprise Module  │  │   Fraud Detection      │ │
│  │   (Placeholder)    │  │    (Placeholder)       │ │
│  └────────────────────┘  └────────────────────────┘ │
│                                                     │
│  Python (FastAPI / Flask)                           │
│  ML: scikit-learn / SpaCy / local transformer      │
└─────────────────────────────────────────────────────┘
         │
    Local Storage / SQLite / In-memory
    (No cloud DB — privacy-first)
```

### Recommended Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Frontend** | React (Vite) or Next.js | Modern, fast, component-based |
| **Charts** | Recharts / Chart.js / Plotly | Interactive, responsive charts |
| **Backend** | Python (FastAPI) | Excellent ML ecosystem, fast API framework |
| **ML / NLP** | scikit-learn, SpaCy, or small local transformer | Offline, lightweight, privacy-safe |
| **Data Processing** | Pandas, openpyxl | CSV, XLS, XLSX, TXT, Delimited, XLS, XLSX, TXT, Delimited parsing, data wrangling |
| **Storage** | SQLite / In-memory (Pandas DataFrames) | No cloud dependency |
| **Export** | Python CSV, XLS, XLSX, TXT, Delimited writer / Pandas `to_csv` | Simple, reliable |

---

## 5. Supported Bank Formats (Initial Set)

The auto-detection module should support at minimum these popular Indian banks:

| Bank | Common CSV, XLS, XLSX, TXT, Delimited Column Patterns |
|---|---|
| HDFC | `Date`, `Narration`, `Withdrawal Amt`, `Deposit Amt`, `Closing Balance` |
| SBI | `Txn Date`, `Description`, `Debit`, `Credit`, `Balance` |
| ICICI | `Transaction Date`, `Transaction Remarks`, `Withdrawal Amount`, `Deposit Amount` |
| Axis | `Tran Date`, `PARTICULARS`, `DR`, `CR`, `BAL` |
| Kotak | `Date`, `Description`, `Debit`, `Credit`, `Balance` |

The detection system should be **extensible** — easy to add new bank format definitions.

---

## 6. Key Features Checklist

### Phase 1 — MVP (Retail)
- [ ] CSV, XLS, XLSX, TXT, Delimited, XLS, XLSX, TXT, Delimited file upload UI
- [ ] Auto bank format detection and normalization
- [ ] Rule-based categorization (RegEx for UPI, known merchants)
- [ ] Local ML-based categorization for remaining transactions
- [ ] Salary auto-detection
- [ ] Anomaly filtering from average spend
- [ ] Avoidable/Unavoidable auto-tagging
- [ ] Human-in-the-loop toggle (override avoidable flag per transaction)
- [ ] Dashboard: time-series spending chart
- [ ] Dashboard: category breakdown chart
- [ ] Dashboard: avoidable vs. unavoidable pie chart
- [ ] Fun insights card (behavioral facts)
- [ ] Export categorized statement as CSV, XLS, XLSX, TXT, Delimited

### Phase 2 — Enterprise (Placeholder)
- [ ] Multi-account upload and cross-account analysis
- [ ] Vendor payment tracking
- [ ] Cash flow summary dashboard
- [ ] Macro-spending trend reports

### Phase 3 — Fraud Detection (Placeholder)
- [ ] Micro-transaction repetition detection
- [ ] Late-night transaction flagging
- [ ] Payee mismatch alerts
- [ ] Cyclic transfer pattern detection

---

## 7. Privacy & Security Constraints

1. **No external API calls** for data processing or categorization.
2. **No cloud LLMs** — all ML inference runs locally / in-memory.
3. **No bank account linking** — works entirely on uploaded files.
4. **Data stays local** — no telemetry, no server-side storage in cloud.
5. **Session-based processing** — data can be discarded after the session, or optionally stored locally.

---

## 8. UX / Design Principles

- **Frictionless onboarding**: Upload a file → instant results. No signup, no config.
- **Interactive dashboards**: Hover tooltips, clickable chart segments, drill-down views.
- **Human-in-the-loop**: Easy toggle switches for avoidable/unavoidable on each transaction row.
- **Fun & engaging**: The insights card should feel delightful — not just data, but personality.
- **Responsive**: Works on desktop and mobile browsers.
- **Dark mode / modern aesthetic**: Premium feel with glassmorphism, smooth gradients, micro-animations.

---

## 9. Data Flow Summary

```
User uploads CSV, XLS, XLSX, TXT, Delimited, XLS, XLSX, TXT, Delimited
        │
        ▼
┌─────────────────────┐
│ Bank Auto-Detection  │ ← Match column headers against known bank patterns
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ Schema Normalization │ → Standardized: Date, Description, Amount, Type, Balance
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ Categorization       │
│  1. RegEx rules      │ → UPI parsing, known merchant matching
│  2. Local ML model   │ → Classify remaining into categories
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ Analytics Engine     │
│  • Salary detection  │
│  • Anomaly filtering │
│  • Avoidable tagging │
│  • Fun insights gen  │
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ UI Dashboard         │ → Charts, insights card, transaction table with toggles
└─────────┬───────────┘
          ▼
     Export CSV, XLS, XLSX, TXT, Delimited (enriched)
```

---

## 10. Open Questions / Decisions

| # | Question | Impact |
|---|---|---|
| 1 | **Monorepo or separate repos** for frontend & backend? | Project structure |
| 2 | **Which ML model** to start with — Naive Bayes (simplest), SpaCy, or a small transformer? | Accuracy vs. setup complexity |
| 3 | **Pre-trained category model** or train from scratch on sample data? | Time to MVP |
| 4 | **SQLite for persistence** or purely in-memory per session? | Data retention, UX |
| 5 | **Multi-month support** in Phase 1 or single-month only? | Scope |
| 6 | **PDF support** — defer entirely to Phase 2+ or basic support in Phase 1? | Scope |
| 7 | **Authentication** — needed for Phase 1 (local use) or only for Enterprise phase? | Complexity |
