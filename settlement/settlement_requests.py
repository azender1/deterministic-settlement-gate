from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Dict

from settlement.gate import attempt_settlement, SettlementError
from settlement.models import Case


@dataclass
class SettlementRequestResult:
    ok: bool
    settlement_id: Optional[str]
    reason: str


class SettlementRequestRegistry:
    """
    Minimal request-id (nonce) dedup layer.

    - First time a request_id is seen for a FINAL case, it attempts settlement.
    - Re-using the same request_id returns the same settlement_id (dedup).
    - A different request_id after settlement returns the existing settlement_id.
    - Uses simple in-memory map (for demo); can be persisted using SQLiteStore later.
    """

    def __init__(self) -> None:
        # request_id -> settlement_id
        self._requests: Dict[str, str] = {}
        self._created_at: Dict[str, float] = {}

    def submit(self, case: Case, request_id: str) -> SettlementRequestResult:
        if not request_id or not request_id.strip():
            return SettlementRequestResult(False, None, "missing_request_id")

        # If we've seen this exact request before, return cached result.
        if request_id in self._requests:
            return SettlementRequestResult(True, self._requests[request_id], "dedup_same_request_id")

        # If already settled, return existing settlement id (dedup across request ids).
        if getattr(case, "settlement_id", None):
            sid = case.settlement_id
            self._requests[request_id] = sid
            self._created_at[request_id] = time.time()
            return SettlementRequestResult(True, sid, "already_settled")

        # Otherwise attempt settlement through the existing gate.
        try:
            sid = attempt_settlement(case)
        except SettlementError as e:
            return SettlementRequestResult(False, None, f"settlement_blocked:{e}")

        self._requests[request_id] = sid
        self._created_at[request_id] = time.time()
        return SettlementRequestResult(True, sid, "settled")
