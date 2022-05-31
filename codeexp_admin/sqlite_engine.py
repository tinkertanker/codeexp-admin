import sqlite3
import os


class SqliteEngine:
    def __init__(self, file_path: str):
        self.database_location = os.path.abspath(file_path)
        self._conn = sqlite3.connect(self.database_location)

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    @property
    def cursor(self) -> sqlite3.Cursor:
        return self.connection.cursor()

    def exec_file(self, file_path: str):
        with open(os.path.abspath(file_path), "r") as f:
            self.cursor.executescript(f.read())

