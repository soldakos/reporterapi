from starlette.requests import Request
from starlette.responses import Response

from app.decorator import func_timer
from app.models import Query, DetailQuery
from app.responses import global_resp
from app.subject import queries as queries_subject
from app.db import api as dbapi


@func_timer
def settings(req: Request, resp: Response, **kwargs):
    return global_resp(resp=resp, data=dbapi.settings(), kwargs=kwargs)


@func_timer
def databases(req: Request, resp: Response, **kwargs):
    return global_resp(resp=resp, data=dbapi.databases(), kwargs=kwargs)


@func_timer
def queries(req: Request, resp: Response, **kwargs):
    return global_resp(resp=resp, data=dbapi.queries(), kwargs=kwargs)


# @func_timer
# def svnurl(req: Request, resp: Response, **kwargs):
#     return global_resp(resp=resp, data=dbapi.svnurl(), kwargs=kwargs)


@func_timer
def patches_root_properties(req: Request, resp: Response, **kwargs):
    return global_resp(resp=resp, data=dbapi.patches_root_properties(), kwargs=kwargs)


@func_timer
def patches_install_comments(req: Request, resp: Response, **kwargs):
    return global_resp(resp=resp, data=dbapi.patches_install_comments(), kwargs=kwargs)


@func_timer
def patches_projects(req: Request, resp: Response, **kwargs):
    return global_resp(resp=resp, data=dbapi.patches_projects(), kwargs=kwargs)


@func_timer
def patches_user_subdirs(req: Request, resp: Response, **kwargs):
    return global_resp(resp=resp, data=dbapi.patches_user_subdirs(), kwargs=kwargs)


@func_timer
def patches_user_subdir_files(req: Request, resp: Response, **kwargs):
    return global_resp(resp=resp, data=dbapi.patches_user_subdir_files(), kwargs=kwargs)


@func_timer
def query_log(req: Request, resp: Response, db_id, qr_id, **kwargs):
    return global_resp(resp=resp,
                       data=dbapi.query_log(db_id, qr_id),
                       kwargs=kwargs)


@func_timer
def detail_data(req: Request, resp: Response, body: DetailQuery, **kwargs):
    return global_resp(resp=resp,
                       data=dbapi.data_by_template(body.filialId, body.sqlTemplate, body.param),
                       kwargs=kwargs)


@func_timer
def query_data(req: Request, resp: Response, body: Query, **kwargs):
    return global_resp(resp=resp,
                       data=queries_subject.get_query_data(body.filialId, body.queryId, body.sqlText, body.rowsBeg, body.rowsEnd),
                       kwargs=kwargs)


@func_timer
def query_report(req: Request, resp: Response, body: Query, **kwargs):
    return global_resp(resp=resp,
                       data=queries_subject.get_report_data(body.sqlText, body.queryId, body.bvId),
                       kwargs=kwargs)
