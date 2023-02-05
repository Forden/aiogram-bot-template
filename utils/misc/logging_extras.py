import functools
import typing


def add_fsm_scene(scene_name: str):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if 'logger' in kwargs:
                kwargs['logger'] = kwargs['logger'].bind(fsm_scene=scene_name)
            result = await func(*args, **kwargs)
            return result

        return wrapped

    return wrapper


def add_fsm_scene_step(step_name: str):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if 'logger' in kwargs:
                kwargs['logger'] = kwargs['logger'].bind(fsm_scene_step=step_name)
            result = await func(*args, **kwargs)
            return result

        return wrapped

    return wrapper


def add_fsm_data():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if 'logger' in kwargs and 'state' in kwargs:
                kwargs['logger'] = kwargs['logger'].bind(fsm_data=await kwargs['state'].get_data())
            result = await func(*args, **kwargs)
            return result

        return wrapped

    return wrapper


def add_handler_name():
    def wrapper(func: typing.Callable):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if 'logger' in kwargs:
                kwargs['logger'] = kwargs['logger'].bind(handler_name=func.__name__)
            result = await func(*args, **kwargs)
            return result

        return wrapped

    return wrapper
