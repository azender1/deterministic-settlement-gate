from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional
from .models import Case


@dataclass
class InMemoryStore:
    cases: Dict[str, Case] = field(default_factory=dict)

    def get_case(self, case_id: str) -> Optional[Case]:
        return self.cases.get(case_id)

    def put_case(self, case: Case) -> None:
        self.cases[case.case_id] = case
