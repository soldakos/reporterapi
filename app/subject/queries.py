import concurrent
import datetime

from app.db.api import databases
from app.db.core import exec_query, exec_cmd, exec_query_pure
from app.db.datasources import get_conn
from app.tools import fetchallformat, get_element, raise_error_from_dict


def getEmptyData():
    return {"data": [], "titles": [], "sysdate": "", "errcode": 0, "error": "", "report": { "columns": [], "columns_btn": [], "hiddencols": [], "error": [], "data": [] }}


def prepare_sqltext(sqltext, rowsbeg, rowsend):
    return f'select * from (select t.*, rownum rn from({sqltext})t) where rn between {rowsbeg} and {rowsend}'
    # return f'select * from({sqltext}) where rownum < 100000'


def get_ssp_server_data():
    res = exec_query(querytext='select * from ssp.server where dsn is not null', db='oracle')
    print('get_ssp_server_data = ', res)
    return res


def log_sql(db_id, query_id, sqltext):
    def getAllDbId(conn):
        res = exec_query_pure(conn=conn,
                              querytext="""select db.id from reporter_databases db where db.name = 'all'""")
        raise_error_from_dict(res)
        return res['data'][0][0]

    conn = get_conn()
    try:
        res = exec_cmd(conn=conn,
                       cmdtext=f"insert or ignore into reporter_sqltext(data) values (:data)",
                       cmdparams={'data': sqltext})
        raise_error_from_dict(res)
        # get sql text ID ....
        res = exec_query_pure(conn=conn,
                              querytext="select id from reporter_sqltext where data = :data",
                              queryparams={'data': sqltext})
        print('pure data = ', res)
        raise_error_from_dict(res)
        sqltext_id = res['data'][0][0]

        # insert query log ....
        # db_id = db_id or getAllDbId(conn)
        res = exec_cmd(conn=conn,
                       cmdtext=f"""insert into reporter_querylog(sysdate, query_id, sqltext_id, db_id) 
                                values (:sysdate, :query_id, :sqltext_id, :db_id)
                                on conflict(query_id, sqltext_id, db_id) do update set sysdate = :sysdate""",
                       cmdparams={'sysdate': datetime.datetime.now(), 'query_id': query_id, 'sqltext_id': sqltext_id, 'db_id': db_id or getAllDbId(conn)})
        raise_error_from_dict(res)

        # res = exec_query_pure(conn=conn,
        #                          querytext="select id from reporter_querylog where query_id = :query_id and sqltext_id = :sqltext_id and db_id = :db_id",
        #                          queryparams=[query_id, sqltext_id, db_id])
        # if res['errcode'] != 0:
        #     raise Exception(res['error'])
        # querylog_id = res['data'][0][0]
        # # print('querylog_id = ', querylog_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise


def get_query_data(filialId, queryId, sqlText, rowsBeg, rowsEnd):
    print('sqltext = ', sqlText)
    res = {}
    data = getEmptyData()
    try:
        conn = get_conn(filial_id=filialId, db='oracle')
        res = exec_query_pure(conn=conn,
                              querytext="""select to_char(sysdate, 'dd.mm.yyyy hh24:mi:ss') from dual""",
                              db='oracle')
        if res['error']:
            raise Exception(res['error'])

        sysdate = res['data'][0][0]
        data['sysdate'] = sysdate
        res = exec_query(conn=conn,
                         querytext=prepare_sqltext(sqlText, rowsBeg, rowsEnd),
                         filial_id=filialId,
                         db='oracle',
                         divtitle=True,
                         withoutRN=True)
        print('get_query_data = ', res)
        if res['error']:
            raise Exception(res['error'])

        data['titles'] = res['titles']
        data['data'] = res['data']
        log_sql(filialId, queryId, sqlText)
    except Exception as e:
        data['errcode'] = get_element(res, 'errcode', 1)
        data['error'] = str(e)

    return data


def get_report_data(sqltext, query_id, bv_id):
    # data = {'columns': [], 'columns_btn': [], 'hiddencols': [], 'error': [], 'report': []}
    data = getEmptyData()

    def do_report(rec_):
        dataset, conn, cur = None, None, None
        sd, error, rowcount = '', '', 0
        try:
            conn = get_conn(filial_id=rec_['id'], db='oracle')
            cur = conn.cursor()
            try:
                cur.execute(sqltext)
            except Exception as e:
                # reconnect with AQAPP user
                if 'ORA-00942' in str(e) or 'ORA-01031' in str(e):
                    conn = get_conn(filial_id=rec_['id'], db='oracle', alternate_user='aqapp', alternate_pwd='welcome')
                    cur = conn.cursor()
                    cur.execute(sqltext)
            [data['report']['columns'].append(cols[0]) for cols in cur.description] if not data['report']['columns'] else None
            dataset = fetchallformat(cur.fetchall(), cur)
            rowcount = cur.rowcount
            cur.execute("""select to_char(sysdate, 'dd.mm.yyyy hh24:mi:ss') from dual""")
            sd = cur.fetchone()[0]
        except Exception as exc:
            error = f"Error: {exc} ({rec_['name']} / {rec_['dsn']})"
        finally:
            cur.close() if cur else None
            conn.close() if conn else None
            print('RECORD = ', {"db": rec_['name'], "sd": sd, "er": error, "rc": rowcount, "data": dataset})
            data['report']['data'].append({"db": rec_['name'], "sd": sd, "er": error, "rc": rowcount, "data": dataset or []})

    starttime = datetime.datetime.now()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        future = {pool.submit(do_report, (rec)): rec for rec in databases(bv_id=bv_id, report=1)['data']}
        for thread in concurrent.futures.as_completed(future):
            rec = future[thread]
            try:
                thread.res()
            except Exception as exc:
                print('%r generated an exception: %s' % (rec, exc))
    elapsed = datetime.datetime.now() - starttime
    print('report time elapsed: ', elapsed)

    # query/server sql log
    log_sql(None, query_id, sqltext)

    return data
