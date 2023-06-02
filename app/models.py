from pydantic.main import BaseModel
from pydantic import Field


class PureStrReq(BaseModel):
    stringval: str = Field(title='Строковое значение')


class Query(BaseModel):
    filialId: int = Field(title='Server')
    bvId: int = Field(title='Bittl vers')
    queryId: int = Field(title='Query')
    sqlText: str = Field(title='SQL text')
    rowsBeg: int = Field(title='rows slice begin')
    rowsEnd: int = Field(title='rows slice end')


class DetailQuery(BaseModel):
    filialId: int = Field(title='Server')
    sqlTemplate: str = Field(title='SQL template')
    param: str = Field(title='Param for sql')


class FileSave(BaseModel):
    path: str = Field(title='Patch file path')
    encoding: str = Field(title='Patch file encoding')
    alias: str = Field(title='Patch install TNS names alias')
    filetext: str = Field(title='Patch file text')


class PatchCreate(BaseModel):
    bv_id: int = Field(title='Bittl vers')
    patchdir: str = Field(title='Patch dir path')
    patchdirserv: str = Field(title='Patch path + server dir')
    patchusers: str = Field(title='Patch users')
    scriptdirs: list = Field(title='Patch script subdirs in user directory')
    scriptfiles: list = Field(title='Patch script subfiles')
    readmehead: str = Field(title='Readme head')
    readmebody: str = Field(title='Readme body')
    readmefoot: str = Field(title='Readme foot')
    project: str = Field(title='Project name')
    clientdir: bool = Field(title='Create client directory option')


class RedmineRoot(BaseModel):
    username: str = Field(title='Redmine username')
    password: str = Field(title='Redmine password')
    urlroot: str = Field(title='Redmine root url')
    urlissues: str = Field(title='Redmine issues url')
    redmine_project_url: str = Field(title='Redmine my projects url')


class RedmineCreate(BaseModel):
    username: str = Field(title='Redmine username')
    password: str = Field(title='Redmine password')
    urlroot: str = Field(title='Redmine root url')
    urlissues: str = Field(title='Redmine issues url')
    project_id: str = Field(title='Redmine project id')
    subject: str = Field(title='Redmine task subject')
    description: str = Field(title='Redmine task description')
    svn_url: str = Field(title='Patch svn url')
    assigned_to_id: str = Field(title='Redmine tester id')
    parent_issue_id: str = Field(title='Redmine parent issue')
    what_todo: str = Field(title='Redmine task what to do')


class FillInstallSql(BaseModel):
    patchdirserv: str = Field(title='Patch dir serv')
    patchnum: str = Field(title='Patch number')
    patchalias: str = Field(title='Patch tnsnames alias')
    patchowner: str = Field(title='Patch history table owner')
    isbinstall: str = Field(title='Patch ISB install option')


class SVN(BaseModel):
    url_root: str = Field(title='svn root url')
    url_patch: str = Field(title='svn patch url')
    patchnum: str = Field(title='Patch num')
    patchdir: str = Field(title='Patch path')
    usr: str = Field(title='svn user')
    pwd: str = Field(title='svn pwd')
