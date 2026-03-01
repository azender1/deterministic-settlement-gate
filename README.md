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
- Automated trading systems dependent on external signals  

Common failure modes:

- Conflicting outcome signals  
- Premature settlement before finality  
- Replay / double settlement  
- Arbitration loops  
- Late conflicting data after a case is "final"  

Most implementations rely on retries, flags, or manual overrides.

This project demonstrates a deterministic control-plane architecture that enforces:

- Deterministic state transitions  
- Conflict containment before payout  
- Explicit finalization  
- Exactly-once settlement (idempotent execution)  

---

## High-Level Flow

Outcome Signals  
→ Reconciliation  
→ Finality Gate  
→ Settlement (exactly-once)  

---

## Architecture (Control Plane)

Outcome Signals  
  ↓  
Reconciliation (conflict detection & containment)  
  ↓  
Finality Gate (blocks settlement unless FINAL)  
  ↓  
Settlement Execution (exactly-once / idempotent)  
  ↓  
Ledger / Payout  

---

## State Machine

OPEN  
→ RESOLVED_PROVISIONAL  
→ IN_RECONCILIATION  
→ FINAL  
→ SETTLED  

- Ambiguous signals transition to IN_RECONCILIATION  
- Settlement is impossible unless state is FINAL  
- Settlement is idempotent (replay-safe)  
- Late signals are ignored after finality  

---

# Modern Integrations

## 1) AI-Agent Outcome Simulation

Demonstrates multiple AI agents generating outcome signals  
(including conflict scenarios).

Run:

```bash
python examples/simulate_ai.py
```

Shows:

- AI-generated signals  
- Conflict isolation  
- Reconciliation  
- Finalization  
- Exactly-once settlement  
- Trace artifacts written to `examples/traces/`  

---

## 2) Prediction Market Style Demo

Demonstrates a toy prediction market payout flow:

- Participants stake YES / NO  
- External resolution signals arrive  
- Settlement gate enforces finality  
- Payout receipt generated  

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
models.py                     case + signal models  
state_machine.py              deterministic transitions  
reconciliation.py             conflict detection  
gate.py                       exactly-once settlement enforcement  
store.py                      in-memory persistence  

settlement/ai_oracle.py       AI-style outcome generator  

examples/simulate.py                  base scenarios  
examples/simulate_ai.py               AI-integrated demo  
examples/prediction_market_demo.py    prediction market demo  
```

---

## Scope & Intent

This repository is **not a trading bot** and **not a production exchange**.

It is a reference control-layer pattern for:

- AI-driven execution systems  
- Prediction markets  
- Escrow workflows  
- Oracle-based resolution  
- High-liability payout infrastructure  

The focus is settlement integrity, not strategy alpha.

---

## Production Hardening Additions

The current reference implementation now includes:

### Durable Persistence (SQLiteStore)

- Case state and signals are persisted to SQLite.
- Settlement state survives process restarts.
- ACID transactions via SQLite provide single-node crash safety.
- Designed as a minimal durable layer (can later migrate to Postgres or event sourcing).

### Request-ID (Nonce) Deduplication Layer

- Settlement attempts require a unique `request_id`.
- Replays using the same `request_id` return the cached settlement result.
- New request_ids after settlement resolve to the same settlement_id.
- Prevents duplicate settlement effects across retries or multiple actors.
- Moves from pure state-based idempotency to explicit request-level deduplication.

These additions close the major single-instance production gaps identified in earlier architectural reviews while preserving the simplicity of the control-plane pattern.

## Licensing

For commercial licensing or integration discussions, see:

`LICENSING.md`

---

## License

Apache-2.0