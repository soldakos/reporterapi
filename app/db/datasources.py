from app.tools import get_element, get_element_deep

connections = {}


def checkErr(res):
    if res['errcode'] != 0:
        print(res, 'raise ',res['error'])
        raise Exception(res['error'])


def get_conn(filial_id=0, db='sqllite', alternate_user='', alternate_pwd=''):
    # global connections
    if db == 'oracle':
        import cx_Oracle
        conn = cx_Oracle.connect(user=alternate_user if alternate_user else get_element_deep(connections, [str(filial_id), 'usr']),
                                 password=alternate_pwd if alternate_pwd else get_element_deep(connections, [str(filial_id), 'pwd']),
                                 dsn=get_element_deep(connections, [str(filial_id), 'dsn']))
    else:
        import sqlite3
        conn = sqlite3.connect('db.sqlite3')
    return conn


def init():
    global connections

    def add(key, val):
        connections[key] = val

    connections.clear()
    print('Loading config server data ...')
    from app.db.api import databases
    res = databases()
    # raise_error_from_dict(res)
    if res['errcode'] != 0:
        return
    data = res['data']
    [add(str(x['id']), {'filial_name': x['name'],
                        'db': x['bv_name'],
                        'usr': x['usr'],
                        'pwd': x['pwd'],
                        'dsn': x['dsn']}) for x in data]
    print(connections)

    # [add(str(0 if x['name'].lower() == 'bimeg' else x['id']), {'filial_name': x['name'],
    #                                                            'db': x['bv_name'],
    #                                                            'usr': x['usr'],
    #                                                            'pwd': x['pwd'],
    #                                                            'dsn': x['dsn']}) for x in get_dbs()['data']]
    # add("0", {'filial_name': 'Bimeg',
    #           'db': '1.3.5',
    #           'usr': 'reporter',
    #           'pwd': 'ciuyrhvv',
    #           'dsn': """(DESCRIPTION = (ADDRESS_LIST = (LOAD_BALANCE = no) (ADDRESS = (PROTOCOL = TCP)(HOST = 10.8.8.145)(PORT = 1521))
    #                     (ADDRESS = (PROTOCOL = TCP)(HOST = 10.8.8.139)(PORT = 1521)) ) (CONNECT_DATA = (SERVER = DEDICATED) (SERVICE_NAME = megaline.telecom)
    #                     (FAILOVER_MODE = (TYPE = SELECT) (METHOD = BASIC) (RETRIES = 10) (DELAY = 3) ) ) )"""})
    #
    # print('Loading ssp server data ...')
    # [add(str(x['ID']), {'filial_name': x['NAME'],
    #                     'db': '1.3',
    #                     'usr': x['USR'],
    #                     'pwd': x['PWD'],
    #                     'dsn': x['DSN']}) for x in get_ssp_server_data()['data']]
