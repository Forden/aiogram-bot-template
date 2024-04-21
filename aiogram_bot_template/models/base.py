import typing
import uuid

import orjson
import pydantic


def orjson_dumps(
    v: typing.Any,
    *,
    default: typing.Callable[[typing.Any], typing.Any] | None,
) -> str:
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(json_encoders={uuid.UUID: lambda x: f"{x}"})
