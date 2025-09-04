# dao/base.py
from connection import get_connection


class BaseDAO:
    def __init__(self, conn=None):
        # allow dependency injection for tests
        self._external_conn = conn

    def _conn(self):
        return self._external_conn or get_connection()
