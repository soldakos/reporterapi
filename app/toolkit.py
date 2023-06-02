from pathlib import Path
import cx_Oracle, os, datetime, copy

# from datetime import datetime

from fastapi.encoders import jsonable_encoder
from pydantic.main import BaseModel


ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'
WIN_FORMAT = '%d.%m.%Y %H:%M:%S.%f'
USR_FORMAT = '%d.%m.%Y %H:%M:%S'


words = ['Теперь', 'Для этого берём начало', 'добавляем HTML-теги',
         'Не стоит опасаться', 'добавляем теги',
         'Мы говорили', 'За это отвечает',
         'Чтобы каждый',
         'немного вперёд',
         'Алгоритм',
         'шаблонные слова', 'Вот как',
         'Как видим', 'Можно делать',
         'находим все']
phrases = ['Теперь можно собрать письмо в одно целое', 'Для этого берём начало, середину и концовку', 'добавляем HTML-теги и соединяем всё в одну строку',
           'Не стоит опасаться того, что всё будет выглядеть некрасиво', 'для этого мы как раз и добавляем теги, чтобы они разметили наш текст правильно и красиво',
           'Мы говорили, что сделаем так, чтобы алгоритм сам выбирал', 'За это отвечает переменная mood: если она равна 0, то стиль будет официальным',
           'Чтобы каждый раз это число определялось случайным образом, добавим функцию, которая возвращает случайное число в заданном диапазоне',
           'Чтобы было понятно, что будет происходить дальше в коде, заглянем немного вперёд',
           'Алгоритм будет действовать так: возьмёт структуру письма и раз за разом будет находить все шаблонные слова со знаком доллара',
           'Так алгоритм будет работать до тех пор, пока не закончатся все шаблонные слова', 'Вот как, например, может выглядеть наше письмо с тегами на каждом проходе алгоритма',
           'Как видим, алгоритм сначала заменил все шаблонные слова первого уровня, а затем — второго уровня', 'Можно делать сколько угодно вложений — алгоритм заменит их все на нормальные слова',
           'находим все слова, где есть значки доллара']


def load_json(data):
    import json
    try:
        data = json.loads(data)
    except BaseException as e:
        msg = f'Ошибка преобразования. Возможно данные не согласуются с форматом JSON. {e}'
        raise Exception(msg)
    return data


def req_to_json(model: BaseModel, raiseexc=True):
    try:
        data = jsonable_encoder(model)
        return data
    except Exception as e:
        msg = f'Ошибка преобразования. Возможно данные не согласуются с форматом JSON. {e}'
        if raiseexc:
            raise Exception(msg)
        return msg


def get_element(data, elem, default=None, raiseerr_empty_msg=None):
    if raiseerr_empty_msg and (not data or elem not in data or not data[elem]):
        raise ValueError(raiseerr_empty_msg)
    return default if not data or elem not in data or not isinstance(data, dict) else data[elem]


def find_element_value(data, elem, val):
    for rec in data:
        if elem in rec and rec[elem] == val:
            return True
    return False


def get_element_deep(data, elem_tree, default=None):
    import copy
    data_ = copy.deepcopy(data)
    for item in elem_tree:
        if item not in data_:
            return default
        data_ = data_[item]
    return data_


def to_iso(date):
    if not date:
        return ''
    return date.strftime(ISO_FORMAT)


def to_win(date):
    if not date:
        return ''
    return date.strftime(WIN_FORMAT)


def is_number(str):
    try:
        float(str)
        return True
    except Exception:
        return False


def check_date(datestr, format=ISO_FORMAT, raiseerr=True):
    if not datestr:
        return None
    try:
        if datetime.strptime(datestr, format):
            return None
    except Exception as e:
        if raiseerr:
            raise e
        return str(e)


def to_date(datestr, format=ISO_FORMAT):
    if not datestr:
        return None
    return datetime.strptime(datestr, format)


def check_param(parname, parval, res, required=True, checknum=False, datefrm=None):
    """
    Проверка наличия параметра и его валидация по требованию
    Результат возвращается + записывается (накопительно) по типу out-параметра в res[0]
    :param parname: параметр (имя)
    :param parval: параметр (значение)
    :param res: inout-параметр результат
    :param required: параметр обязательный или нет
    :param checknum: требуется проверка на число или нет
    :param datefrm: требуется проверка на дату в указанном формате
    :return:
    """
    def concat():
        return f"{res[0]} " if res[0] else ''

    try:
        if parval == '' or parval is None:
            if not required:
                return res[0]
            res[0] = f'{concat()}Не передан параметр [{parname}].'
        elif checknum and not is_number(parval):
            res[0] = f'{concat()}Параметр [{parname}] должен содержать только цифры.'
        elif datefrm:
            is_date_err = check_date(parval, datefrm, False)
            if is_date_err:
                res[0] = f'{concat()}Параметр [{parname}] не соответствует формату даты [{datefrm}]: {is_date_err}.'
    except Exception as exc:
        raise Exception(f'{exc}. parname={parname}, parval={parval}')
    return res[0]


def check_query_param(request, param, res, required=True, checknum=False):
    """
    Проверка наличия query-параметра в запросе и его валидация по требованию
    Результат возвращается + записывается по типу out-параметра в res[0]
    :param request: http-запрос
    :param param: query-параметр запроса
    :param res: аут-параметр результат
    :param required: параметр обязательный или нет
    :param checknum: требуется проверка на число или нет
    :return:
    """
    res[0] = ''
    parval = request.GET.get(param)
    if parval == '' or parval is None:
        if not required:
            return res[0]
        res[0] = f'Не передан параметр [{param}].'
    elif checknum and not parval.isnumeric():
        res[0] = f'параметр [{param}] должен содержать только цифры.'

    return res[0]


def get_copied_changed_array(orig_array, new_data):
    """
    Возвращает физическую копию массива orig_array (List) с измененными в нем элементами, описанными в new_data.
    Подходит для инициализации параметров оракловых процедур, передавая нужные значения в new_data
    :param orig_array: Оригинальный list типа [{"name": "", "value": "", "dir": "", ... },]
    :param new_data: list-шаблон новых значений элементов типа [{"name": "", "value": ""},]
    :return: физическая копия orig_array c изменнными в нем значениями элементов по шаблону new_data
    """
    import copy
    result_array = copy.deepcopy(orig_array)
    for new_data_elem in new_data:
        for result_array_elem in result_array:
            if new_data_elem["name"] == result_array_elem["name"]:
                result_array_elem["value"] = new_data_elem["value"]
                break
    return result_array


def get_quote_or_null(value):
    """
    Для подстановки значения (value) в SQL-запрос.
    Оборачивает строковое значение в ковычки если оно не пустое,
    иначе возвращает строку NULL без ковычек соответственно
    :param value: строковое значение
    :return: обработанный результат
    """
    return f'\'{value}\'' if value else 'null'


def read_file(path, encoding='utf-8', error=False):
    if not Path(path).exists():
        return ''
    try:
        with Path(path).open(mode='r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        if encoding == 'utf-8' and not error:
            print(f'Can\'t read file {path} with encoding {encoding}')
            return read_file(path, 'windows-1251', error=True)
        elif encoding == 'windows-1251' and not error:
            print(f'Can\'t read file {path} with encoding {encoding}')
            return read_file(path, 'utf-8', error=True)
        raise Exception(f'Can\'t read file "{path}" with error {e}')


def write_file(path, text='', encoding='utf-8', rewrite=False, newline=None):
    if Path(path).exists() and not rewrite:
        return
    try:
        with Path(path).open(mode='w', encoding=encoding, newline=newline) as f:
            f.writelines(text)
    except Exception as e:
        print(f'Can\'t write file {path} with error {e}')
        raise Exception(f'Can\'t write file {path} with error {e}')


def deleteFile(path):
    try:
        Path(path).unlink() if not Path(path).is_dir() else Path(path).rmdir()
    except Exception as e:
        raise Exception(f'Can\'t delete file {path} with error {e}')


def file_open(path):
    if not Path(path).exists():
        return
    try:
        os.system(path)
    except Exception as e:
        raise Exception(f'Can\'t open {path} with error {e}')


def file_browser(path):
    if not Path(path).exists():
        return
    try:
        import subprocess
        subprocess.run(f'explorer / ,"{Path(path)}"')
    except Exception as e:
        raise Exception(f'Can\'t open explorer on {path} with error {e}')


def get_tns_path():
    return Path(os.environ['TNS_ADMIN'], 'tnsnames.ora')


def saveFile(path, encoding, alias, filetext):
    error, patchserveraddr, aliaspos = '', '', ''
    try:
        write_file(get_tns_path() if path == 'TNSNAMES' else Path(path), filetext.split('\r'), encoding=encoding, rewrite=True)
        if alias:
            tnsnamesinfo = get_server_info(alias, filetext)
            patchserveraddr = tnsnamesinfo['addr']
            aliaspos = tnsnamesinfo['aliaspos']
    except Exception as e:
        error = str(e)

    return {"patchserveraddr": patchserveraddr, "aliaspos": aliaspos, "error": error}


def get_server_info(alias, ftext=''):
    ftext = (read_file(get_tns_path()) if not ftext else ftext).upper()
    # ftext = ftext.upper()
    alias = alias.upper()
    aliaspos, linealiaspos = -1, -1
    host, port, service = '', '', ''
    for line in ftext.replace(' ', '').splitlines():
        if linealiaspos == -1:
            linealiaspos = line.find(alias + '=', 0, len(alias + '='))
        if linealiaspos == -1:
            continue
        if host == '':
            hostind = line.find('HOST=')
            if hostind == -1:
                continue
            host = line[hostind + 5:line.find(')', hostind + 5)]
        if port == '' and host != '':
            portfind = line.find('PORT=')
            if portfind == -1:
                continue
            port = line[portfind + 5:portfind + 9]
        if service == '' and port != '':
            servicefind = line.find('SERVICE_NAME=')
            if servicefind == -1:
                servicefind = line.find('SID=')
            if servicefind == -1:
                continue
            servicefind = line.find('=', servicefind) + 1
            service = line[servicefind:line.find(')', servicefind)].lower()
            break
    if host != '':
        aliaspos = ftext.find(f"\n{alias} ") + 1

    # print("get_server_info ... ", f'{host}:{port} / {service}', "   alias = ", alias, "  ... aliaspos = ", aliaspos)
    return {"addr": f'{host}:{port} / {service}', "aliaspos": aliaspos}


def get_conn(source):
    usr = source.connectionstring[0:source.connectionstring.index('/')]
    pwd = source.connectionstring[source.connectionstring.index('/') + 1: -1]
    return cx_Oracle.connect(usr, pwd, source.dns, nencoding='UTF8')


def fetchallformat(data, cursor):
    def format(desc, row):
        print('desc =    ',desc)
        print('row =    ', row)
        return tuple(x[1].strftime("%Y.%m.%d %H:%M:%S.%f") if x[1] and x[0] in (cx_Oracle.DB_TYPE_TIMESTAMP, cx_Oracle.DB_TYPE_TIMESTAMP_TZ, cx_Oracle.DB_TYPE_TIMESTAMP_LTZ) else
                     # x[1].strftime("%Y.%m.%d %H:%M:%S").replace(' 00:00:00', '') if x[1] and x[0] == cx_Oracle.DB_TYPE_DATE else
                     x[1].strftime("%Y.%m.%d %H:%M:%S") if x[1] and x[0] == cx_Oracle.DB_TYPE_DATE else
                     str(x[1]) if x[1] and x[0] in (cx_Oracle.DB_TYPE_LONG_RAW, cx_Oracle.DB_TYPE_LONG, cx_Oracle.DB_TYPE_RAW, cx_Oracle.DB_TYPE_BLOB) else
                     x[1] for x in zip([x[1] for x in desc], row))

    return [format(cursor.description, row) for row in (x for x in data)]


def fetchallformat_(data, cursor):
    def rowfactory(row, cursor):
        casted = []
        for value, desc in zip(row, cursor.description):
            if value is not None and desc[1] in (cx_Oracle.TIMESTAMP, cx_Oracle.DATETIME):
                value = value.strftime("%Y.%m.%d %H:%M:%S.%f") if desc[1] == cx_Oracle.TIMESTAMP else value.strftime("%Y.%m.%d %H:%M:%S").replace(' 00:00:00', '')
            casted.append(value)
        return tuple(casted)

    # если в описании полей нет типов дат, то вернем как есть. ничего форматировать не будем
    if next((i for i, x in enumerate(zip(cursor.description)) if x[0][1] in [cx_Oracle.TIMESTAMP, cx_Oracle.DATETIME]), -1) == -1:
        return data

    result = []
    for x in zip(cursor.description):
        if x[0][1] in (cx_Oracle.TIMESTAMP, cx_Oracle.DATETIME):
            for row in data:
                result.append(rowfactory(row, cursor))
            break
    return result


def get_date_now_format(format):
    now = datetime.datetime.now()
    return datetime.date(now.year, now.month, now.day) if format == 'short' else now


def raise_error_from_dict(res):
    if res['errcode'] != 0:
        raise Exception(res['error'])


def choose_files (path, multiple=True, preview=True, filters=None):
    import plyer
    return plyer.filechooser.open_file(path=path, multiple=multiple, preview=preview, filters=filters)