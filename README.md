# Deterministic Settlement Gate

A reference implementation of a deterministic settlement and dispute-containment control layer  
for systems that rely on external outcome resolution (oracles, AI agents, referees, APIs, or humans).

This pattern sits between outcome resolution and payout and prevents money from moving unless  
the system can prove the outcome is final and unambiguous.

---

## Why this exists

Modern automated systems increasingly rely on external or probabilistic outcomes:

- AI agents generating decisions
- Oracle-resolved prediction markets
- Referee / API-based match resolution
- Automated trading strategies dependent on external signals

Common failure modes:

- conflicting outcome signals  
- premature settlement before finality  
- replay / double settlement  
- arbitration loops  
- late conflicting data after a case is “final”  

Most systems handle this with retries, flags, or manual overrides.

This project demonstrates a deterministic control-plane architecture that eliminates those failure modes by enforcing:

- deterministic state transitions  
- conflict containment before payout  
- explicit finalization  
- exactly-once settlement  

---

## High-Level Flow

Outcome Signals  
→ Reconciliation  
→ Finality Gate  
→ Settlement (exactly-once)  

---

## Architecture (Control Plane)

Outcome Signals
|
v
Reconciliation
|
v
Finality Gate
|
v
Settlement Execution
|
v
Ledger / Payout

```

---

## State Machine

OPEN  
→ RESOLVED_PROVISIONAL  
→ IN_RECONCILIATION  
→ FINAL  
→ SETTLED  

- Ambiguous signals go to IN_RECONCILIATION  
- Settlement is impossible unless FINAL  
- Settlement is idempotent (replay-safe)  
- Late signals ignored after finality  

---

# Modern Integrations

## 1. AI-Agent Outcome Simulation

Demonstrates multiple AI agents generating outcome signals  
(including conflict scenarios).

Run:

```bash
python examples/simulate_ai.py
```

Shows:

- AI-generated signals
- conflict isolation
- reconciliation
- finalization
- exactly-once settlement
- trace artifacts written to `examples/traces/`

---

## 2. Prediction Market Style Demo

Demonstrates a toy prediction market payout flow:

- participants stake YES/NO
- external resolution signals arrive
- settlement gate enforces finality
- payout receipt generated

Run:

```bash
python examples/prediction_market_demo.py
```

Writes payout receipt to:

```
examples/receipts/
```

---

## Core Implementation Structure

```
models.py                case + signal models  
state_machine.py         deterministic transitions  
reconciliation.py        conflict detection  
gate.py                  exactly-once settlement enforcement  
store.py                 in-memory persistence  

settlement/ai_oracle.py  AI-style outcome generator  
examples/simulate.py     base scenarios  
examples/simulate_ai.py  AI-integrated demo  
examples/prediction_market_demo.py prediction market demo  
```

---

## Scope & Intent

This repository is **not a trading bot** and **not a production exchange**.

It is a reference control-layer pattern for:

- AI-driven execution systems  
- prediction markets  
- escrow workflows  
- oracle-based resolution  
- high-liability payout infrastructure  

The focus is settlement integrity, not strategy.

---

## Licensing

For commercial licensing or integration discussions, see:

`LICENSING.md`