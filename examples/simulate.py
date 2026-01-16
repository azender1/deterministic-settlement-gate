import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from settlement.models import Case, OutcomeSignal
from settlement.store import InMemoryStore
from settlement.reconciliation import ingest_signal, resolve_reconciliation
from settlement.gate import attempt_settlement, SettlementError


def scenario_clean():
    print("\n--- scenario_clean ---")
    store = InMemoryStore()
    case = Case(case_id="case_1")
    store.put_case(case)

    ok, reason = ingest_signal(case, OutcomeSignal(case_id="case_1", source="oracle_A", outcome="YES"))
    print("ingest 1:", ok, reason, "state:", case.state)

    # finalize without dispute
    resolve_reconciliation(case, chosen_outcome="YES")
    print("finalized:", case.final_outcome, "state:", case.state)

    sid = attempt_settlement(case)
    print("settled:", sid, "state:", case.state)

    # replay settlement
    sid2 = attempt_settlement(case)
    print("replay settled:", sid2, "(same id)", sid2 == sid)


def scenario_conflict():
    print("\n--- scenario_conflict ---")
    store = InMemoryStore()
    case = Case(case_id="case_2")
    store.put_case(case)

    ok, reason = ingest_signal(case, OutcomeSignal(case_id="case_2", source="oracle_A", outcome="YES"))
    print("ingest A:", ok, reason, "state:", case.state)

    ok, reason = ingest_signal(case, OutcomeSignal(case_id="case_2", source="oracle_B", outcome="NO"))
    print("ingest B:", ok, reason, "state:", case.state, "recon:", case.reconciliation_reason)

    try:
        attempt_settlement(case)
    except SettlementError as e:
        print("settlement blocked:", e)

    resolve_reconciliation(case, chosen_outcome="YES")
    print("resolved:", case.final_outcome, "state:", case.state)

    sid = attempt_settlement(case)
    print("settled:", sid, "state:", case.state)    # Replay / double-settlement attempts (should be safe)
    for i in (1, 2):
        try:
            replay_result = gate.settle(case_id)
            print(f"replay settle attempt {i}: {replay_result}")
        except Exception as e:
            print(f"replay settle attempt {i}: blocked ({type(e).__name__}: {e})")


if __name__ == "__main__":
    scenario_clean()
    scenario_conflict()

