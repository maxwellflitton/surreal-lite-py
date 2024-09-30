"""
The query module contains the Query class.
"""
import uuid
from typing import Any, Dict, Optional, List

from sblpy.sql_adapter import SqlAdapter


class Query:
    """
    Defines the data needed to run a query on the database.

    Attributes:
        sql: The SQL query to run.
        _vars: The variables to use in the query.
        id: The ID of the query.
    """
    def __init__(self, sql: str, vars: Optional[Dict[str, Any]] = None) -> None:
        """
        The constructor for the Query class.

        :param sql: (str) the SQL query to run
        :param vars: (Optional[Dict[str, Any]]) the variables to use in the query
        """
        self.sql: str = sql
        self._vars: Optional[Dict[str, Any]] = vars
        self.id: str = str(uuid.uuid4())

    @staticmethod
    def from_docstring(docstring: str) -> "Query":
        """
        Creates a Query object from a docstring.

        :param docstring: (str) the docstring to create the query from
        :return: (Query) the query object created from the docstring
        """
        return Query(SqlAdapter.from_docstring(docstring))

    @staticmethod
    def from_list(commands: List[str]) -> "Query":
        """
        Creates a Query object from a list of commands.

        :param commands: (List[str]) the list of commands to create the query from
        :return: (Query) the query object created from the list of commands
        """
        return Query(SqlAdapter.from_list(commands))

    @staticmethod
    def from_file(file_path: str) -> "Query":
        """
        Creates a Query object from a file.

        :param file_path: (str) the path to the file to create the query from
        :return: (Query) the query object created from the file
        """
        return Query(SqlAdapter.from_file(file_path))

    @property
    def vars(self) -> Dict[str, Any]:
        if self._vars is None:
            return {}
        return self._vars

    @property
    def query_params(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "method": "query",
            "params": [
                self.sql,
                self.vars
            ]
        }