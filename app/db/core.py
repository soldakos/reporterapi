from app.db.datasources import get_conn
from app.logapi import logerror

""" 
модуль выполнения SQL-запросов и хранимых процедур
"""


def exec_query(conn=None, querytext='', filial_id=0, queryparams=None, db=None, divtitle=False, withoutRN=False, kwargs=None):
    """
    Выполняет запрос с параметрами
    """
    data, titles, errcode, error = [], [], 0, ''
    try:
        if not conn:
            conn = get_conn(filial_id, db)
        cur = conn.cursor()
        cur.execute(querytext, queryparams or [])
        titles, data = get_cursor_data(cur, divtitle, withoutRN)
        # print('cur, titles, data = ',cur, titles, data)
    except Exception as exc:
        errcode = 1
        error = str(exc)
        logerror(msg=f'{error} |oper| {querytext}: {queryparams}', kwargs=kwargs)

    return {'data': data or [], 'titles': titles if divtitle else [], 'errcode': errcode or 0, 'error': error or ''}


def exec_query_pure(conn=None, querytext='', filial_id=0, queryparams=None, db=None, array=False, kwargs=None):
    """
    Выполняет запрос с параметрами
    """
    data, errcode, error = None, 0, None
    try:
        if not conn:
            conn = get_conn(filial_id, db)
        cur = conn.cursor()
        cur.execute(querytext, queryparams or [])
        data = cur.fetchall()
        data = [x[0] for x in data] if array else data
    except Exception as exc:
        errcode = 1
        error = str(exc)
        logerror(msg=f'{error} |oper| {querytext}: {queryparams}', kwargs=kwargs)

    return {'data': data or [], 'errcode': errcode or 0, 'error': error or ''}


def exec_cmd(conn=None, cmdtext='', filial_id=0, cmdparams=None, db=None, kwargs=None):
    """
    Выполняет команду с параметрами
    """
    cur, errcode, error = None, 0, None
    try:
        if not conn:
            conn = get_conn(filial_id, db)
        cur = conn.cursor()
        cur.execute(cmdtext, cmdparams or [])
    except Exception as exc:
        errcode = 1
        error = str(exc)
        logerror(msg=f'{error} |oper| {cmdtext}: {cmdparams}', kwargs=kwargs)

    return {'errcode': errcode or 0, 'error': error or ''}


def get_cursor_data(cursor, divtitle, withoutRN):
    """
    fetch ораклового курсора с формированием стандартного словаря с именами полей для значений
    :param cursor:
    :return:
    """
    # columns = [col[0] for col in cursor.description if col[0] != 'RN' and withoutRN]
    columns = [col[0] for col in cursor.description][:-1 if withoutRN else None]
    # print('cursor.description = ', cursor.description)
    # print('columns = ', columns)
    if divtitle:
        data = [x[:-1 if withoutRN else None] for x in cursor.fetchall()]
        # print('data = ', data)
    else:
        data = []
        for row in cursor:
            rec = {}
            for i, col in enumerate(columns):
                rec[col] = row[i]
            data.append(rec)
    return columns, data
