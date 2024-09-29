import uuid
from typing import Any, Dict, Optional, List


class Query:

    def __init__(self, sql: str, vars: Optional[Dict[str, Any]] = None) -> None:
        self.sql: str = sql
        self._vars: Optional[Dict[str, Any]] = vars
        self._result: Optional[List[Dict[str, Any]]] = None
        self.id: str = str(uuid.uuid4())
        # self.result: Optional[] = None

    @property
    def vars(self) -> Dict[str, Any]:
        if self._vars is None:
            return {}
        return self._vars

    @property
    def query_params(self):
        return {
            "id": self.id,
            "method": "query",
            "params": [
                self.sql,
                self.vars
            ]
        }