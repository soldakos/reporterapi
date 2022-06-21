from logging import Logger
import logging.config

import settings
from app.tools import get_element

console_logger: Logger
gunicorn_logger: Logger


def init():
    global gunicorn_logger, console_logger

    frmt = logging.Formatter('{"time": "%(asctime)s", "process": "%(process)s", "thread": "%(threadName)s", "level": "%(levelname)s", "x_forwarded_for": "%(x_forwarded_for)s", "url": "%(url)s", "status": "%(status)s", "msg": "%(message)s", "elapsed": "%(elapsed)s"}')

    gunicorn_logger = logging.getLogger('gunicorn.error')
    gunicorn_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    console_logger = logging.getLogger(name='console')
    console_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    chandler = logging.StreamHandler()
    chandler.setFormatter(frmt)
    console_logger.addHandler(chandler)


def log(msg, level: int = logging.INFO, kwargs=None):
    ip, url, status, elapsed = get_element(kwargs, 'ip', ''), get_element(kwargs, 'url', ''), get_element(kwargs, 'status', ''), get_element(kwargs, 'elapsed', 0.0)
    console_logger.log(level=level, msg=str(msg), extra={"x_forwarded_for": ip, "url": url, "status": status, "elapsed": elapsed})
    # gunicorn_logger.log(level=level, msg=str(msg), extra={"x_forwarded_for": ip, "url": url})


def logerror(msg, kwargs=None):
    log(msg=msg, level=logging.ERROR, kwargs=kwargs)


def loginfo(msg, kwargs=None):
    log(msg=msg, level=logging.INFO, kwargs=kwargs)


def logdebug(msg, kwargs=None):
    if settings.DEBUG:
        log(msg=msg, level=logging.DEBUG, kwargs=kwargs)


def logresponse(msg, kwargs=None):
    log(msg=msg, level=logging.INFO, kwargs=kwargs)


def logconsole(msg, kwargs=None):
    log(msg=msg, level=logging.INFO, kwargs=kwargs)
