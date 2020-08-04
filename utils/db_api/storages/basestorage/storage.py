from typing import List, Type, TypeVar, Union

T = TypeVar("T")


class RawConnection:
    @staticmethod
    def __make_request(
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False
    ):
        """
        You have to override this method for all synchronous databases (e.g., Sqlite).
        :param sql:
        :param params:
        :param fetch:
        :param mult:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def _make_request(
            sql: str,
            params: Union[tuple, List[tuple]] = None,
            fetch: bool = False,
            mult: bool = False,
            model_type: Type[T] = None
    ):
        """
        You have to override this method for all synchronous databases (e.g., Sqlite).
        :param sql:
        :param params:
        :param fetch:
        :param mult:
        :param model_type:
        :return:
        """
        raise NotImplementedError
