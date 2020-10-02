import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from loguru import logger

from ..basestorage.storage import RawConnection

T = TypeVar("T")
db_title = Path(__file__).parent.parent.parent.parent.parent / 'data' / 'db.db'  # db file supposed to be in data folder


class SqliteDBConn:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        if exc_val:
            raise


class SqliteConnection(RawConnection):
    @staticmethod
    def __make_request(
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False
    ) -> Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]:
        with SqliteDBConn(db_title) as conn:
            c = conn.cursor()
            try:
                if isinstance(params, list):
                    c.executemany(sql, params)
                else:
                    c.execute(sql, params)
            except Exception as e:
                logger.error(e)
            if fetch:
                if mult:
                    r = c.fetchall()
                else:
                    r = c.fetchone()
                return r
            else:
                conn.commit()

    @staticmethod
    def _convert_to_model(data: Optional[dict], model: Type[T]) -> Optional[T]:
        if data is not None:
            return model(**data)
        else:
            return None

    @staticmethod
    def _make_request(
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False,
            model_type: Type[T] = None
    ) -> Optional[Union[List[T], T]]:
        raw = SqliteConnection.__make_request(sql, params, fetch, mult)
        if raw is None:
            if mult:
                return []
            else:
                return None
        else:
            if mult:
                if model_type is not None:
                    return [SqliteConnection._convert_to_model(i, model_type) for i in raw]
                else:
                    return [i for i in raw]
            else:
                if model_type is not None:
                    return SqliteConnection._convert_to_model(raw, model_type)
                else:
                    return raw
