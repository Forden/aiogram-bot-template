import typing
import uuid

import orjson
import pydantic


def orjson_dumps(
    v: typing.Any,
    *,
    default: typing.Optional[typing.Callable[[typing.Any], typing.Any]],
) -> str:
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class BaseModel(pydantic.BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

        json_encoders = {uuid.UUID: lambda x: f"{x}"}
