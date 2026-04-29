# 🍣 SUSHI Tool — Super User Sales Highly Informed

> *An IAM-driven AI solution that enforces least privilege access to SAP order data while eliminating 100+ hours of manual work per week across EMEA sales operations.*

---

## 🔐 The Problem — An IAM Governance Challenge

At TD SYNNEX, the Sales Director requested access to **VA02 (SAP Order Change)** for the entire EMEA sales team across 12+ countries.

During the access review, I identified a critical **IAM governance conflict:**

- The VA02 transaction contained sensitive customer data in the **Conditions tab** — including customer tax IDs, billing addresses, and confidential pricing structures
- Granting direct SAP access would violate **Segregation of Duties (SoD)** controls and expose Personally Identifiable Information (PII) to users with no business justification to access it
- Under the **Principle of Least Privilege**, sales representatives needed order status and pricing visibility — not full transaction access

**Two options were on the table:**

| Option | Approach | Cost | Timeline |
|--------|----------|------|----------|
| Custom SAP Transaction | Build a new SAP view stripping sensitive fields | Very High | 6–12 months |
| ✅ SUSHI Tool | AI agent with data-layer access filtering | Low | 3 weeks |

---

## 🧠 The Solution — IAM by Design

Instead of modifying SAP access controls or building expensive custom transactions, I designed an **AI-powered data access layer** that enforced least privilege at the integration level.

The sales team never touches SAP directly. They interact with a conversational AI agent that:

- Connects to the enterprise order database via **SAP BAPI (BAPI_SALESORDER_GETLIST)**
- Filters out all sensitive fields at the integration layer **before** data reaches the user
- Returns only the fields with a valid business justification:
  - ✅ Customer name
  - ✅ Order status
  - ✅ Standard pricing
  - ✅ Special price eligibility
  - ❌ Tax ID — blocked
  - ❌ Billing address — blocked
  - ❌ Confidential margin data — blocked

**This is IAM enforced at the architecture level — not just at the access control level.**

---

## 🏗️ Architecture

```
Sales Rep (Natural Language Query)
          ↓
    AI Agent (GPT-4)
          ↓
  Integration Layer (Python)
    - Field-level filtering
    - PII stripping
    - Audit logging
          ↓
  SAP Order Database
  (BAPI_SALESORDER_GETLIST)
          ↓
  Filtered Response → Sales Rep
```

**Key architectural decisions:**
- **No direct SAP access** granted to end users — zero SoD risk
- **Field-level filtering** enforced programmatically — sensitive data never leaves the integration layer
- **Full audit trail** — every query logged with user, timestamp, query content, and data returned
- **Standalone .exe deployment** — distributed via internal company software catalogue, no infrastructure overhead

---

## 🔒 IAM Principles Applied

| Principle | Implementation |
|-----------|---------------|
| **Least Privilege** | Users access only the specific fields their role requires |
| **SoD Enforcement** | No single user can access both operational and sensitive financial data |
| **Data Governance** | PII fields blocked at integration layer, never exposed to unauthorised users |
| **Audit Trail** | All queries logged immutably — who asked what, when, and what was returned |
| **Access by Design** | Sensitive data exclusion built into architecture, not bolted on afterwards |

---

## 📊 Business Impact

| Metric | Result |
|--------|--------|
| Manual SAP lookup time eliminated | **100+ hours/week** |
| FTE equivalent saved | **2.5 FTEs** |
| SoD violations prevented | **Zero** since deployment |
| Pilot market | Germany (20 users) |
| Rollout | 12 EMEA countries |
| Status | ✅ Still in production |

---

## 🚀 Deployment

- Packaged as a **standalone Windows .exe**
- Distributed through the internal company software catalogue
- No VPN or SAP GUI installation required for end users
- Pilot launched with Germany sales team (20 users)
- Progressive rollout across 12 EMEA countries

---

## 🛠️ Tech Stack

```
Language:        Python
AI Model:        GPT-4 (OpenAI API)
SAP Integration: BAPI_SALESORDER_GETLIST
Data Layer:      Enterprise order database (real-time)
Deployment:      Standalone .exe (internal distribution)
Logging:         Structured audit trail with full query history
```

---

## 📋 AS IS / TO BE

### AS IS — Before SUSHI Tool
```
Sales rep needs order data
        ↓
Requests SAP access from IT
        ↓
IT reviews (no automated SoD check)
        ↓
Access granted to full VA02 transaction
        ↓
Sales rep sees ALL data including PII
        ↓
SoD violation — sensitive data exposed
        ↓
40+ min manual lookup per query
```

### TO BE — With SUSHI Tool
```
Sales rep asks question in plain English
        ↓
AI agent queries SAP via integration layer
        ↓
Sensitive fields filtered automatically
        ↓
Sales rep sees only authorised data
        ↓
Full audit log created
        ↓
Response in under 10 seconds
        ↓
Zero SoD violations. Zero PII exposure.
```

---

## 💬 Why This Matters

> *"The sales director wanted his team in SAP. The right answer wasn't to give them SAP access — it was to give them the data they needed without the risk. SUSHI Tool is what IAM looks like when you solve the problem at the architecture level instead of the access control level."*

---

*Built as part of enterprise IAM governance initiatives at TD SYNNEX EMEA*
*Deployed across 12 countries | Still in production*
