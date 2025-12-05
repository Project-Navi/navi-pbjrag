# License Package — How to Choose & Comply (v2.2)

This folder contains:

- **PNEUL‑C v2.2** — Client & Services License (plain‑language, enterprise‑friendly).  
- **PNEUL‑D v2.2** — Developer Dual License (AGPL‑3 or Commercial).  
- **DPA v1.0** — Data Processing Addendum (attach when Personal Data is processed).  
- **NOTICE_TEMPLATE.md** — for AGPL use.  
- **ATTRIBUTION_GUIDE.md** — where/how to credit, and how to request a waiver.

## Which path should a user pick?

- **Using our software under open source terms** → Choose **AGPL‑3** (PNEUL‑D Option A). Keep notices and provide source for network use (AGPL §13). Add a `NOTICE` file and optionally an “About/Credits” UI entry as an **Appropriate Legal Notice** (§5). No ethics/donation conditions apply under AGPL.

- **Needing closed-source/proprietary rights** → Choose **Commercial** (PNEUL‑D Option B). Sign an Order Form referencing v2.2. Ethics (consent/safety) and **Give‑Back** apply. Attribution is reasonable and **waivable on request**.

- **Services engagements** (consulting/design) → Covered by **PNEUL‑C v2.2**. If Personal Data is processed, attach the **DPA**.

## Where to put files in a repo

- Root: `LICENSE` (short pointer to PNEUL‑D), `NOTICE` (if AGPL).  
- `/legal/` or `/docs/legal/`: keep full texts (`PNEUL-C_v2.2.md`, `PNEUL-D_v2.2.md`, `DPA_v1.0.md`).  
- UI “About” modal or docs site: link to the license chosen and **Attribution**.

## Attribution waiver

Email `legal@projectnavi.ai` with subject `Attribution Waiver Request`, include: product name, reason (confidentiality/regulatory/white‑label), duration. We’ll respond in writing.

## Change control

- Bump versions when material edits are made.  
- Keep a CHANGELOG (see below) and tag releases.

### CHANGELOG (excerpt)
- **v2.2** — definitions tightened; attribution waiver; export/sanctions; DPA reference; 72h breach notice; liability carve‑outs; Pause & Review due‑process; change‑of‑control; narrow IP indemnity.  
- **v2.1** — initial public draft (client + developer).
