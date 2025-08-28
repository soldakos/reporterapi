from app.logapi import logerror
from app.toolkit import get_type, to_single_row, format_traceback, get_attr_value


class PoolNotFound(Exception):
    """Raised when connect pool for datasource not found"""

    def __init__(self, name: str | None = None):
        self.name = name
        super().__init__(self.name)

    def __str__(self):
        return f'{get_type(self)}: Не найден пул сессий для БД {self.name}'


class ParamNotFoundInAppSettings(Exception):
    """Raised with no data in application settings (e.g. settings.py) """

    def __init__(self, key: str):
        self.key = key
        super().__init__(self.key)

    def __str__(self):
        return f'{get_type(self)}: Параметр {self.key} не найден в настройках приложения.'


class KeyErrorDetail(Exception):
    """Raised with KeyError exc """

    def __init__(self, dataname: str, key: str):
        self.dataname = dataname
        self.key = key
        super().__init__(self.dataname)
        super().__init__(self.key)

    def __str__(self):
        return f'{get_type(self)}: Элемент {self.key} не найден в коллекции {self.dataname}.'


class GeneralException(Exception):
    """Raised with global user defined exc (internal error code or oracle db error code, error message and operation) """

    def __init__(self, code: int, msg: str = '', exc: Exception | None = None, operation: str = '', kwargs=None):
        type_and_code = f"{get_type(exc)} ({code})" if exc else ''
        msg = f"{msg}{'.' if msg and exc else ''} {exc if exc else ''}".strip()
        msg = to_single_row(f"{type_and_code}{'.' if type_and_code else ''} {msg}".strip())
        kwargs = get_attr_value(exc, 'kwargs') or kwargs or dict()
        kwargs['errCode'] = code
        msg = msg[:help_pos - 1 if (help_pos := msg.find('Help: http') > 0) else None]  # вырезаем урл-ссылку хелпа оракла из сообщения
        kwargs['errMsg'] = msg
        kwargs['traceback'] = format_traceback()
        kwargs['operation'] = operation
        logerror(msg, kwargs=kwargs)
        self.msg = msg

    def __str__(self):
        return self.msg


class BusinessLogicException(GeneralException):
    """Raised with global user defined exc (based on GeneralException + additional 'status' element with HTTP status code) """

    def __init__(self, status: int, code: int, msg: str = '', exc: Exception | None = None, kwargs=None):
        super().__init__(code=code, msg=msg, exc=exc, kwargs=kwargs)
        self.status = status
        if kwargs:
            kwargs['statusCode'] = self.status


def get_status_code_by_internal_code(ok_code, kwargs) -> int:
    """ get http status code by internal or postgresql code """

    err_code = kwargs.get('errCode') or 0
    if err_code == 0:  # if code = 0 or None then 200
        return ok_code
    if 200 <= abs(float(err_code)) <= 600:  # if code from 200 to 600 then it is
        return err_code

    return 500  # else 500


def get_http_code_by_db_errcode(db_error_code) -> int:
    """ if user defined oracle errors then 422 else 500"""

    return 422 if 20000 <= abs(float(db_error_code)) <= 20999 else 500
