# Project Navi Data Processing Addendum (DPA) — v1.0

This DPA forms part of the agreement between **Project Navi** (“Processor”) and **Client** (“Controller”) where Project Navi processes **Personal Data** on Client’s behalf.

> **Plain‑English summary (non‑binding):** We process only what’s needed, per your instructions, with appropriate security. We use vetted subprocessors. If there’s a breach, we tell you quickly. We help with data subject requests. When we’re done, we delete or return data. If data leaves your region, we use the proper transfer mechanisms.

---

## 1) Definitions

Capitalized terms have the meanings set out in applicable Data Protection Laws (e.g., GDPR, CCPA/CPRA).

## 2) Scope & Instructions

Project Navi will process Personal Data **solely**: (a) to provide Services under the Agreement; (b) per Client’s documented instructions; and (c) as required by law (in which case we will notify Client, unless legally prohibited). Client is responsible for the **lawfulness** of instructions.

## 3) Confidentiality

Project Navi ensures personnel are bound by confidentiality obligations and receive privacy/security training appropriate to their roles.

## 4) Security Measures

Project Navi implements **appropriate technical and organizational measures** to protect Personal Data (see **Annex 2**), including: access controls, encryption in transit and at rest (where applicable), secure key handling, change control, logging/monitoring, and incident response.

## 5) Subprocessors

Client authorizes Project Navi to use **Subprocessors** listed in **Annex 3**. Project Navi will impose data protection terms no less protective than this DPA and remain responsible for Subprocessors’ performance. We will notify Client of changes and allow objection for reasonable, documented grounds.

## 6) Personal Data Breach

Project Navi will notify Client **without undue delay and within 72 hours** of confirming a Personal Data Breach affecting Client Data, providing known details and ongoing updates.

## 7) Assistance

Project Navi will reasonably assist Client with **data subject requests**, **security**, **DPIAs**, and **consultations** with supervisory authorities, considering the nature of processing and available information.

## 8) International Transfers

Where Personal Data is transferred internationally, Project Navi will implement appropriate transfer mechanisms (e.g., **Standard Contractual Clauses (SCCs)**, UK IDTA/Addendum) and supplementary measures as needed.

## 9) Data Return & Deletion

Upon termination or upon Client’s written request, Project Navi will **delete or return** Personal Data (at Client’s choice), unless retention is required by law. Deletion will follow secure erasure practices.

## 10) Audits

Upon reasonable notice, Project Navi will make available information to demonstrate compliance and allow **audits** by Client or a mutually agreed auditor, **once annually** (and after significant incidents), subject to confidentiality and reasonable time/place limits.

## 11) Liability & Order of Precedence

Liability is governed by the Agreement. If there is a conflict between this DPA and the Agreement, this DPA controls with respect to data protection.

## 12) Term

This DPA remains in effect while Project Navi processes Personal Data for Client.

---

## Annex 1 — Details of Processing

**A. Subject matter and duration.** Processing Personal Data to provide Services under the Agreement; duration = term of the Agreement + retention required by law.
**B. Nature and purpose.** Consent‑first AI collaboration, including tokenization/minimization into **InsightCards**, Council facilitation, and audit via **hash‑only Gateway receipts**.
**C. Categories of data subjects.** Client’s employees, contractors, customers, or end users.
**D. Categories of Personal Data.** Contact identifiers (name, email), role/metadata, collaboration metadata; **no raw PII should cross the LLM boundary** (InsightCards only).
**E. Special categories.** Not intended; Client will not intentionally submit sensitive categories without lawful basis and safeguards.
**F. Retention.** As configured by Client policies and legal requirements; **Gateway receipts store hashes only**.

## Annex 2 — Security Measures

- **Governance:** Security policy, least privilege, background checks where lawful, mandatory training.
- **Access Controls:** Role‑based access, MFA, short‑lived tokens, key rotation.
- **Data Minimization:** Only **InsightCards** cross model boundary; raw prompts not persisted; receipts are **hash‑only**.
- **Encryption:** TLS in transit; encryption at rest for databases and object storage; secret hashing (API keys stored as prefix + hash).
- **Segregation:** Multi‑tenant scoping by **orgId**; optional row‑level security (RLS).
- **Logging/Monitoring:** AuditEvent/TelemetryEvent; anomaly alerts; immutable incident logs.
- **Redaction & Consent:** Double‑redaction patterns; **ConsentTickets** with TTL; fail‑closed policy checks.
- **Business Continuity:** Backups, PITR, disaster recovery testing.
- **Incident Response:** 24/7 escalation, triage, containment, customer comms, postmortems.

## Annex 3 — Subprocessors

| Provider | Purpose | Data types | Region | Notes |
|---|---|---|---|---|
| (add) |  |  |  |  |

**Signatures**
Project Navi (Processor): __________________  Date: ____
Client (Controller): _______________________  Date: ____
