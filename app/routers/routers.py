from typing import Dict, Union

from fastapi import Request, Response, APIRouter, Query as fastapiQuery, Path

from app.routers import queryExec, patchManager
# from app.models import Query, PureStrReq, DetailQuery, PatchFilePaths, FileSave, PatchCreate, RedmineRoot, FillInstallSql
from app.models import Query, DetailQuery, FileSave, PatchCreate, RedmineRoot, FillInstallSql, SVN, RedmineCreate
from app.subject import anyother, tools

router = APIRouter()


@router.get(path='/settings',
            description="global settings",
            tags=['system']
            )
def settings(req: Request, resp: Response):
    return queryExec.settings(req, resp)


@router.get(path='/databases',
            description="oracle databases ",
            tags=['queries']
            )
def databases(req: Request, resp: Response):
    return queryExec.databases(req, resp)


@router.get(path='/queries',
            description="sql queries ",
            tags=['queries']
            )
def queries(req: Request, resp: Response):
    return queryExec.queries(req, resp)


@router.get(path='/query_log',
            description="sql query log ",
            tags=['queries']
            )
def query_log(req: Request, resp: Response, db_id, qr_id):
    return queryExec.query_log(req, resp, db_id, qr_id)


@router.post(path='/detail_data',
             description="sql query detail ",
             tags=['queries']
             )
def detail_data(req: Request, resp: Response, body: DetailQuery):
    return queryExec.detail_data(req, resp, body)


@router.post(path='/query_data',
             description="execute sql query ",
             tags=['queries'],
             )
def exec(req: Request, resp: Response, body: Query):
    print('body = ', body)
    return queryExec.query_data(req, resp, body)


@router.post(path='/query_report',
             description="execute sql query for all servers",
             tags=['queries'],
             )
def exec(req: Request, resp: Response, body: Query):
    return queryExec.query_report(req, resp, body)


# @router.get(path='/svnurl',
#             description="svn urls",
#             tags=['patches']
#             )
# def svnurl(req: Request, resp: Response):
#     return queryExec.svnurl(req, resp)


@router.get(path='/patches_root_properties',
            description="patches root directory and other properties",
            tags=['patches']
            )
def patches_root_properties(req: Request, resp: Response):
    return queryExec.patches_root_properties(req, resp)


@router.get(path='/patches_install_comments',
            description="install comments",
            tags=['patches']
            )
def patches_install_comments(req: Request, resp: Response):
    return queryExec.patches_install_comments(req, resp)


@router.get(path='/unique_projects',
            description="unique projects names",
            tags=['patches']
            )
def patches_projects(req: Request, resp: Response):
    return queryExec.unique_projects(req, resp)


@router.get(path='/patches_user_subdirs',
            description="oracle scheme's subdirectories",
            tags=['patches']
            )
def patches_user_subdirs(req: Request, resp: Response):
    return queryExec.patches_user_subdirs(req, resp)


@router.get(path='/patches_user_subdir_files',
            description="subdirectory's files",
            tags=['patches']
            )
def patches_user_subdir_files(req: Request, resp: Response):
    return queryExec.patches_user_subdir_files(req, resp)


@router.get(path='/patchlist',
            description="patches list",
            tags=['patches']
            )
def patchlist(req: Request, resp: Response, bv_id):
    return patchManager.patchlist(req, resp, bv_id)


@router.get(path='/patchedit',
            description="patch for show|edit",
            tags=['patches']
            )
def patchedit(req: Request, resp: Response, dir, patchnum, alias):
    return patchManager.patchedit(req, resp, dir, patchnum, alias)


@router.delete(path='/deleteFile',
               description="delete file",
               tags=['others']
               )
def deleteFile(req: Request, resp: Response, path):
    return anyother.delete_file(req, resp, path)


@router.post(path='/saveFile',
             description="save text to file",
             tags=['patches']
             )
def saveFile(req: Request, resp: Response, body: FileSave):
    return anyother.saveFile(req, resp, body)


@router.get(path='/patchStructure',
            description="get patch file structure",
            tags=['patches']
            )
def patchStructure(req: Request, resp: Response, patchdir: str):
    return patchManager.patchStructure(req, resp, patchdir)


@router.get(path='/copyToFolder',
            description="copy some project files to patch folder",
            tags=['patches']
            )
def copyToFolder(req: Request, resp: Response, path, project, bv_id):
    return patchManager.copyToFolder(req, resp, path, project, bv_id)


@router.post(path='/patchCreate',
             description="create patch",
             tags=['patches']
             )
def patchCreate(req: Request, resp: Response, body: PatchCreate):
    return patchManager.patchCreate(req, resp, body)


@router.get(path='/patchInstall',
            description="install patch",
            tags=['patches']
            )
def patchInstall(req: Request, resp: Response, patchdirserv):
    return patchManager.patchInstall(req, resp, patchdirserv)


@router.post(path='/commitSVN',
             description="patch repo commit",
             tags=['patches']
             )
def commitSVN(req: Request, resp: Response, body: SVN):
    return patchManager.commitSVN(req, resp, body)


@router.post(path='/redmineIssues',
             description="get redmine issues",
             tags=['patches']
             )
def redmineIssues(req: Request, resp: Response, body: RedmineRoot):
    return patchManager.redmineIssues(req, resp, body)


@router.get(path='/svnData',
            description="get patch SVN data",
            tags=['patches']
            )
def svnData(req: Request, resp: Response, path: str):
    return patchManager.svnData(req, resp, path)


@router.post(path='/fillInstallSql',
             description="fill istall.sql script",
             tags=['patches']
             )
def fillInstallSql(req: Request, resp: Response, body: FillInstallSql):
    return patchManager.fillInstallSql(req, resp, body)


@router.post(path='/redmineCreateTask',
             description="create redmine task",
             tags=['patches']
             )
def redmineCreateTask(req: Request, resp: Response, body: RedmineCreate):
    return patchManager.redmineCreateTask(req, resp, body)


@router.post(path='/tools',
             description="tools",
             tags=['tools']
             )
def tools_exec(req: Request, resp: Response, key: str, body: Dict):
    return tools.post(req, resp, key, body)


@router.get(path='/tools',
            description="tools",
            tags=['tools']
            )
def tools_exec(req: Request, resp: Response, key: str):
    return tools.get(req, resp, key)


@router.get(path='/openFile',
            description="openFile",
            tags=['others']
            )
def openFile(req: Request, resp: Response, path: str):
    return anyother.open_file(req, resp, path)


@router.get(path='/readFile',
            description="readFile",
            tags=['others']
            )
def readFile(req: Request, resp: Response, path: str, encoding: Union[str, None] = "utf-8"):
    return anyother.read_file(req, resp, path, encoding)


@router.post(path='/writeFile',
             description="writeFile",
             tags=['others']
             )
def writeFile(req: Request, resp: Response, path: str, body: Dict):
    return anyother.write_file(req, resp, path, body)


@router.get(path='/fileBrowser',
            description="fileBrowser",
            tags=['others']
            )
def fileBrowser(req: Request, resp: Response, path: str):
    return anyother.file_browser(req, resp, path)


@router.get(path='/admin',
            description="run admin console",
            tags=['system']
            )
def admin(req: Request, resp: Response):
    return anyother.admin()
