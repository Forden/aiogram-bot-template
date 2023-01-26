import aioredis


class BaseCache:
    def __init__(
            self,
            connection: aioredis.Redis,
            namespace_prefix: str = 'cache',
            namespace_separator: str = ':'
    ):
        self._conn = connection
        self._prefix = (namespace_prefix,)
        self._separator = namespace_separator

    def _generate_key(self, *parts) -> str:
        return self._separator.join(self._prefix + tuple(map(str, parts)))
