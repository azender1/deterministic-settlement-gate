# Deterministic Settlement Gate

A reference implementation of a deterministic settlement and dispute-containment control layer  
for systems that rely on external outcome resolution (oracles, AI agents, referees, APIs, or humans).

This pattern sits between outcome resolution and payout and prevents money from moving unless  
the system can prove the outcome is final and unambiguous.

> CI Verified: GitHub Actions runs `python examples/simulate.py` on every push.

---

## Why this exists

Many real-money and high-liability systems suffer from recurring failure modes:

- conflicting oracle or data signals  
- premature settlement on bad or incomplete data  
- double settlement / replay  
- arbitration loops  
- AI agents executing on inference instead of verified outcomes  

Most platforms handle these with ad hoc rules, retries, or manual intervention.

This project demonstrates a formal control-plane architecture that eliminates those failure modes  
by enforcing deterministic state transitions, reconciliation, and exactly-once settlement.

---

## High-level flow

Outcome Signals  
→ Reconciliation (conflict detection & containment)  
→ Finality Gate (blocks settlement unless FINAL)  
→ Settlement (exactly-once)

---

## Architecture (Control Plane)

```mermaid
flowchart LR
    A["Outcome Signals"]
    B["Reconciliation"]
    C["Finality Gate"]
    D["Settlement Execution"]
    E["Ledger / Payout"]

    A --> B --> C --> D --> E
```

---

## State machine

OPEN  
→ RESOLVED_PROVISIONAL  
→ IN_RECONCILIATION  
→ FINAL  
→ SETTLED  

- Ambiguous signals go to IN_RECONCILIATION  
- Settlement impossible unless FINAL  
- Settlement is idempotent (exactly-once)  
- Late signals ignored after finality  

---

## Running the example

From project root:

```bash
python examples/simulate.py
```

This demonstrates:

- deterministic settlement lifecycle  
- conflict detection  
- reconciliation  
- finality enforcement  
- replay-safe settlement  

---

## Example trace artifacts (proof without running code)

Running the simulation writes deterministic receipts to:

```
examples/traces/
```

Included in this repo:

- examples/traces/scenario_clean_case_1.json  
- examples/traces/scenario_conflict_case_2.json  
- examples/traces/scenario_duplicate_and_late_case_3.json  
- examples/traces/scenario_three_oracles_majority_case_4.json  

Quick skim (duplicate + late signal case):

```json
{
  "scenario": "scenario_duplicate_and_late",
  "case_id": "case_3",
  "state": "CaseState.SETTLED",
  "final_outcome": "YES",
  "settlement_id": "...",
  "timestamp_utc": "..."
}
```

---

## Reference implementation structure

```
models.py            case + signal models  
state_machine.py     deterministic transitions  
reconciliation.py    conflict detection  
gate.py              exactly-once settlement enforcement  
store.py             in-memory persistence  
examples/simulate.py runnable scenarios  
```

This repository is intentionally minimal to expose the control pattern clearly.  
It is not a framework.

---

## Scope & intent

This repository is **not a product** and **not a trading system**.

It exists solely to demonstrate a **settlement integrity control pattern** for systems that  
rely on external or probabilistic outcome resolution.

Intended for engineers working on:

- prediction markets  
- escrow platforms  
- peer-to-peer wagering  
- AI-agent execution systems  
- oracle-resolved systems  
- regulated payout infrastructure  

This code is provided as a **reference implementation**, not a deployable platform.

---

## License

Apache-2.0