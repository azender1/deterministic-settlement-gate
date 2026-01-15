from __future__ import annotations
from .models import Case, CaseState


class InvalidTransition(Exception):
    pass


def set_state(case: Case, new_state: CaseState) -> None:
    # Deterministic transitions only
    allowed = {
        CaseState.OPEN: {CaseState.RESOLVED_PROVISIONAL, CaseState.IN_RECONCILIATION},
        CaseState.RESOLVED_PROVISIONAL: {CaseState.IN_RECONCILIATION, CaseState.FINAL},
        CaseState.IN_RECONCILIATION: {CaseState.FINAL},  # only exit when resolved
        CaseState.FINAL: {CaseState.SETTLED},
        CaseState.SETTLED: set(),
    }

    if new_state not in allowed[case.state]:
        raise InvalidTransition(f"{case.state} -> {new_state} not allowed")
    case.state = new_state
