import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from settlement.models import Case
from settlement.store import InMemoryStore
from settlement.reconciliation import ingest_signal, resolve_reconciliation
from settlement.gate import attempt_settlement, SettlementError
from settlement.ai_oracle import generate_ai_signals, AIGeneratorConfig


def write_trace(name: str, case):
    def normalize_signal(s):
        if isinstance(s, dict):
            return {"source": s.get("source"), "outcome": s.get("outcome"), "raw": s}
        if isinstance(s, str):
            if ":" in s:
                left, right = s.split(":", 1)
                return {"source": left.strip(), "outcome": right.strip(), "raw": s}
            if "|" in s:
                left, right = s.split("|", 1)
                return {"source": left.strip(), "outcome": right.strip(), "raw": s}
            return {"source": None, "outcome": None, "raw": s}
        source = getattr(s, "source", None)
        outcome = getattr(s, "outcome", None)
        if source is not None or outcome is not None:
            return {"source": source, "outcome": outcome, "raw": repr(s)}
        return {"source": None, "outcome": None, "raw": repr(s)}

    signals = getattr(case, "signals", [])
    artifact = {
        "scenario": name,
        "case_id": getattr(case, "case_id", None),
        "state": str(getattr(case, "state", None)),
        "final_outcome": getattr(case, "final_outcome", None),
        "signals": [normalize_signal(s) for s in (signals or [])],
        "reconciliation_reason": getattr(case, "reconciliation_reason", None),
        "settlement_id": getattr(case, "settlement_id", None),
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    }

    os.makedirs("examples/traces", exist_ok=True)
    path = os.path.join("examples", "traces", f"{name}_{artifact['case_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)
    print(f"trace written: {path}")


def scenario_ai_clean():
    print("\n--- scenario_ai_clean ---")
    store = InMemoryStore()
    case = Case(case_id="ai_case_1")
    store.put_case(case)

    prompt = "Team A wins the match by a clear victory."
    signals = generate_ai_signals(
        case_id=case.case_id,
        prompt=prompt,
        config=AIGeneratorConfig(seed=1, n_agents=3, conflict_rate=0.0),
    )

    for s in signals:
        ok, reason = ingest_signal(case, s)
        print("ingest:", s.source, s.outcome, ok, reason, "state:", case.state)

    resolve_reconciliation(case, chosen_outcome="YES")
    print("finalized:", case.final_outcome, "state:", case.state)

    sid = attempt_settlement(case)
    print("settled:", sid, "state:", case.state)

    sid2 = attempt_settlement(case)
    print("replay settled:", sid2, "(same id)", sid2 == sid)

    write_trace("scenario_ai_clean", case)


def scenario_ai_conflict():
    print("\n--- scenario_ai_conflict ---")
    store = InMemoryStore()
    case = Case(case_id="ai_case_2")
    store.put_case(case)

    prompt = "Outcome looks unclear; some sources claim Team B lost, others say Team B won."
    signals = generate_ai_signals(
        case_id=case.case_id,
        prompt=prompt,
        config=AIGeneratorConfig(seed=7, n_agents=3, conflict_rate=0.8),
    )

    for s in signals:
        ok, reason = ingest_signal(case, s)
        print("ingest:", s.source, s.outcome, ok, reason, "state:", case.state)

    try:
        attempt_settlement(case)
    except SettlementError as e:
        print("settlement blocked:", e)

    # choose a final outcome after reconciliation (simulates human / policy decision)
    resolve_reconciliation(case, chosen_outcome="YES")
    print("resolved:", case.final_outcome, "state:", case.state)

    sid = attempt_settlement(case)
    print("settled:", sid, "state:", case.state)

    write_trace("scenario_ai_conflict", case)


def scenario_ai_majority_policy():
    print("\n--- scenario_ai_majority_policy ---")
    store = InMemoryStore()
    case = Case(case_id="ai_case_3")
    store.put_case(case)

    prompt = "Team A wins."
    signals = generate_ai_signals(
        case_id=case.case_id,
        prompt=prompt,
        config=AIGeneratorConfig(seed=42, n_agents=5, conflict_rate=0.35),
    )

    tally = {"YES": 0, "NO": 0}
    for s in signals:
        ok, reason = ingest_signal(case, s)
        tally[s.outcome] = tally.get(s.outcome, 0) + 1
        print("ingest:", s.source, s.outcome, ok, reason, "state:", case.state)

    # majority policy
    chosen = "YES" if tally.get("YES", 0) >= tally.get("NO", 0) else "NO"
    resolve_reconciliation(case, chosen_outcome=chosen)
    print("majority chosen:", chosen, "finalized:", case.final_outcome, "state:", case.state)

    sid = attempt_settlement(case)
    print("settled:", sid, "state:", case.state)

    write_trace("scenario_ai_majority_policy", case)


if __name__ == "__main__":
    scenario_ai_clean()
    scenario_ai_conflict()
    scenario_ai_majority_policy()
