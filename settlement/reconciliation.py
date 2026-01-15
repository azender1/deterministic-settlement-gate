from __future__ import annotations
from typing import Tuple
from .models import Case, CaseState, OutcomeSignal
from .state_machine import set_state


def ingest_signal(case: Case, sig: OutcomeSignal) -> Tuple[bool, str]:
    """
    Adds a signal and determines whether:
      - it is consistent (can move toward FINAL), or
      - it introduces conflict (must reconcile).
    Returns (ok, reason).
    """
    # Idempotent signal ingest: ignore duplicate signal_id
    if sig.signal_id in case.signals:
        return True, "duplicate_signal_ignored"

    case.signals[sig.signal_id] = sig

    # If already FINAL or SETTLED, we don't change the final outcome.
    if case.state in (CaseState.FINAL, CaseState.SETTLED):
        return True, "case_already_final_or_settled"

    # Determine if signals conflict.
    outcomes = {s.outcome for s in case.signals.values()}

    if len(outcomes) == 1:
        # No conflict so far; provisional resolution.
        if case.state == CaseState.OPEN:
            set_state(case, CaseState.RESOLVED_PROVISIONAL)
        return True, "consistent_outcome_signals"
    else:
        # Conflict detected → reconciliation required
        case.reconciliation_reason = f"conflicting_outcomes={sorted(list(outcomes))}"
        if case.state != CaseState.IN_RECONCILIATION:
            set_state(case, CaseState.IN_RECONCILIATION)
        return False, case.reconciliation_reason


def resolve_reconciliation(case: Case, chosen_outcome: str) -> None:
    """
    Operator/arbiter/automated rule chooses final outcome.
    This locks finality.
    """
    if case.state not in (CaseState.RESOLVED_PROVISIONAL, CaseState.IN_RECONCILIATION):
        raise ValueError("Can only finalize from RESOLVED_PROVISIONAL or IN_RECONCILIATION")

    case.final_outcome = chosen_outcome
    case.reconciliation_reason = None
    set_state(case, CaseState.FINAL)
