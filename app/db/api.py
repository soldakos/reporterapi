from app.db.core import exec_query, exec_query_pure


def settings():
    res = exec_query(querytext="""select * from reporter_settings""")
    print('settings = ', res)
    return res


def databases(bv_id=None, report=None):
    res = exec_query(querytext="""select db.id, db.name, db.alias, db.usr, db.pwd, db.dsn, bv.id bv_id, bv.name bv_name 
                                  from reporter_databases db, reporter_bittlvers bv 
                                  where bv.id = db.bittlvers_id and 
                                        db.name != 'all' and 
                                        (db.report = :report or :report is null) and 
                                        (bv.id = :bv_id or :bv_id is null)
                                  order by bv.id, db.'order'""",
                     queryparams={'bv_id': bv_id, 'report': report})
    print('databases = ', res)
    return res


def queries():
    res = exec_query(querytext="""select qr.*, st.data sqltext, bv.id bv_id, bv.name bv_name 
                                  from reporter_queries qr, reporter_bittlvers bv, reporter_sqltext st 
                                  where st.id = qr.sqltext_id and qr.bittlvers_id = bv.id
                                  order by qr.'order'""")
    print('queries = ', res)
    return res


# def svnurl(bv_id):
#     res = exec_query_pure(querytext="""select url from reporter_svnurl where bittlvers_id = :bittlvers_id""",
#                           queryparams=[bv_id])
#     print('svnurl = ', res)
#     return res


def patches_root_properties(bv_id=None):
    res = exec_query(querytext="""select p.name, p.dir, p.alias, p.phowner, p.bittlvers_id bv_id, p.redmine_project_url, p.svn_url, bv.name bv_name, bv.namefull
                                  from reporter_patchesrootprops p, reporter_bittlvers bv
                                  where p.bittlvers_id = bv.id and (bv.id = :bv_id or :bv_id is null)
                                  order by p.'order'""",
                     queryparams=[bv_id])
    print('patches_root_properties = ', res)
    return res


def patches_install_comments():
    res = exec_query_pure(querytext="""select text from reporter_patchesinstallcomment order by id""", array=True)
    print('patches_install_comments = ', res)
    return res


def patches_user_subdirs():
    res = exec_query_pure(querytext="""select name from reporter_patchesusersubdir order by 'order'""", array=True)
    print('patches_user_subdirs = ', res)
    return res


def patches_user_subdir_files():
    res = exec_query_pure(querytext="""select name from reporter_patchesusersubdirfiles order by 'order'""", array=True)
    print('patches_user_subdir_files = ', res)
    return res


def patches_user_subdir_order(name):
    res = exec_query_pure(querytext="""select t.'order' from reporter_patchesusersubdir t where name = :name""",
                          queryparams=[name],
                          array=True)
    print('patches_user_subdir_order = ', res)
    return res


def patches_user_subdir_file_order(name):
    res = exec_query_pure(querytext="""select t.'order' from reporter_patchesusersubdirfiles t where name = :name""",
                          queryparams=[name],
                          array=True)
    print('patches_user_subdir_file_order = ', res)
    return res


def tnsnames():
    res = exec_query(querytext="""select path from reporter_tnsnames t where active = 1 order by 'order'""")
    print('tnsnames = ', res)
    return res


def services():
    res = exec_query(querytext="""select name, url, servertype from reporter_services t where active = 1 order by 'order'""")
    print('services = ', res)
    return res


def projects(unique=False, global_name=None, bv_id=None):
    print(' api projects bv_id = ',bv_id)
    columns = '*' if not unique else 'distinct global_name'
    where = f" and lower(global_name) = '{global_name.lower()}'" if global_name else ''
    where = f"{where} and bittlvers_id in ({bv_id}, 3)" if bv_id else where
    querytext = f"""select {columns} from reporter_projects t where active = 1 {where} order by 'order', name"""
    res = exec_query(querytext=querytext)
    print('projects, querytext = ', res, querytext)
    return res


def query_log(db_id, qr_id):
    res = exec_query(querytext="""select st.data, ql.sysdate
                                from reporter_querylog ql, reporter_sqltext st, reporter_databases db                                 
                                where st.id = ql.sqltext_id and ql.query_id = :query_id and (ql.db_id = :db_id or db.name = 'all') and db.id = ql.db_id 
                                order by ql.sysdate desc""",
                     queryparams={'db_id': db_id, 'query_id': qr_id})
    print('query_log = ', res)
    return res


def data_by_template(filial_id, sql_template, param):
    res = exec_query_pure(querytext=sql_template,
                          queryparams=[param],
                          filial_id=filial_id,
                          db='oracle')
    print('data_by_template = ', res)
    return res
