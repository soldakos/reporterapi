from starlette.requests import Request
from starlette.responses import Response

from app.decorator import func_timer
# from app.models import PatchFilePaths, PatchFileSave, PatchCreate, RedmineRoot, FillInstallSql
from app.models import PatchFileSave, PatchCreate, RedmineRoot, FillInstallSql, SVN, RedmineCreate
from app.responses import global_resp
from app.subject import patches, redmine, svn


@func_timer
def patchlist(req: Request, resp: Response, bv_id, **kwargs):
    return global_resp(resp=resp, data=patches.patchlist(bv_id), kwargs=kwargs)


@func_timer
def patchedit(req: Request, resp: Response, dir, patchnum, alias, **kwargs):
    return global_resp(resp=resp, data=patches.patchedit(dir, patchnum, alias), kwargs=kwargs)


# def patchedit(req: Request, resp: Response, bv_id, patchnum, **kwargs):
#     return global_resp(resp=resp, data=patches.patchedit(bv_id, patchnum), kwargs=kwargs)


@func_timer
def deleteFile(req: Request, resp: Response, path, **kwargs):
    return global_resp(resp=resp, data=patches.deleteFile(path), kwargs=kwargs)


# def deleteFile(req: Request, resp: Response, body: PatchFilePaths, **kwargs):
#     return global_resp(resp=resp, data=patches.deleteFile(body.patchdir, body.path), kwargs=kwargs)


@func_timer
def saveFile(req: Request, resp: Response, body: PatchFileSave, **kwargs):
    return global_resp(resp=resp, data=patches.saveFile(body.path, body.alias, body.filetext), kwargs=kwargs)


@func_timer
def openFile(req: Request, resp: Response, path, **kwargs):
    return global_resp(resp=resp, data=patches.openFile(path), kwargs=kwargs)


# def openFile(req: Request, resp: Response, body: PatchFilePaths, **kwargs):
#     return global_resp(resp=resp, data=patches.openFile(body.patchdir, body.path), kwargs=kwargs)


@func_timer
def patchStructure(req: Request, resp: Response, patchdir: str, **kwargs):
    return global_resp(resp=resp, data=patches.patchStructure(patchdir), kwargs=kwargs)


@func_timer
def patchCreate(req: Request, resp: Response, body: PatchCreate, **kwargs):
    print('patchCreate', body)
    return global_resp(resp=resp,
                       data=patches.patchCreate(body.bv_id, body.patchdir, body.patchdirserv, body.patchusers, body.scriptdirs, body.scriptfiles,
                                                body.readmehead, body.readmebody, body.readmefoot, body.project, body.clientdir),
                       kwargs=kwargs)


@func_timer
def patchInstall(req: Request, resp: Response, patchdirserv, **kwargs):
    print('patchInstall', patchdirserv)
    return global_resp(resp=resp,
                       data=patches.patchInstall(patchdirserv),
                       kwargs=kwargs)


@func_timer
def commitSVN(req: Request, resp: Response, body: SVN, **kwargs):
    print('commitSVN', body)
    return global_resp(resp=resp,
                       data=svn.commit_svn(body.url_root, body.url_patch, body.patchnum, body.patchdir, body.usr, body.pwd),
                       kwargs=kwargs)


@func_timer
def redmineIssues(req: Request, resp: Response, body: RedmineRoot, **kwargs):
    return global_resp(resp=resp, data=redmine.redmine_issues(body.username, body.password, body.urlroot, body.urlissues, body.redmine_project_url), kwargs=kwargs)


@func_timer
def svnData(req: Request, resp: Response, path: str, **kwargs):
    return global_resp(resp=resp, data=svn.svnData(path), kwargs=kwargs)


@func_timer
def fillInstallSql(req: Request, resp: Response, body: FillInstallSql, **kwargs):
    return global_resp(resp=resp, data=patches.fillInstallSql(body), kwargs=kwargs)


@func_timer
def redmineCreateTask(req: Request, resp: Response, body: RedmineCreate, **kwargs):
    return global_resp(resp=resp, data=redmine.execute_create_redmine_issue(body), kwargs=kwargs)
