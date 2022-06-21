from starlette.requests import Request

import time


def request_info(method_to_decorate):
    def info(*args, **kwargs):
        request = Request(args[0])
        kwargs.setdefault('url', request.url.path)
        kwargs.setdefault('ip', request.client.host)
        return method_to_decorate(*args, **kwargs)

    return info


def func_timer(method_to_decorate):
    def info(*args, **kwargs):
        kwargs.setdefault('startTime', time.time())
        return method_to_decorate(*args, **kwargs)

    return info
