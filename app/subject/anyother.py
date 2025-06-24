import os
import sys
from pathlib import Path

from starlette.requests import Request
from starlette.responses import Response

from app import toolkit
from app.models import FileSave
from app.responses import global_resp
from app.toolkit import get_tns_path


def admin():
    error = ''
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    print(BASE_DIR, sys.path[1])
    try:
        os.system(rf"{BASE_DIR}\sqlite-gui\sqlite-gui.exe {BASE_DIR}\db.sqlite3")
    except Exception as e:
        error = str(e)

    return {"error": error}


def saveFile(req: Request, resp: Response, body: FileSave, **kwargs):
    return global_resp(resp=resp,
                       data=toolkit.saveFile(body.path, body.encoding, body.alias, body.filetext),
                       kwargs=kwargs)


def open_file(req: Request, resp: Response, path, **kwargs):
    error = ''
    try:
        toolkit.file_open(path=path)
    except Exception as e:
        error = str(e)

    return global_resp(resp=resp,
                       data={"data": None, "error": error},
                       kwargs={"errcode": 500 if error else 0, "error": error})


def read_file(req: Request, resp: Response, path, encoding, **kwargs):
    filetext, error = '', ''
    try:
        path = get_tns_path() if path == 'TNSNAMES' else path
        filetext = toolkit.read_file(path=path, encoding=encoding)
    except Exception as e:
        error = str(e)

    return global_resp(resp=resp,
                       data={"path": path, "filetext": filetext, "error": error},
                       kwargs={"errcode": 500 if error else 0, "error": error})


def write_file(req: Request, resp: Response, path, body, **kwargs):
    error = ''
    try:
        toolkit.write_file(path=path, text=body['text'], rewrite=True)
    except Exception as e:
        error = str(e)

    return global_resp(resp=resp,
                       data={"data": None, "error": error},
                       kwargs={"errcode": 500 if error else 0, "error": error})


def delete_file(req: Request, resp: Response, path, **kwargs):
    error = ''
    try:
        toolkit.deleteFile(path)
    except Exception as e:
        error = str(e)

    return global_resp(resp=resp,
                       data={"data": None, "error": error},
                       kwargs={"errcode": 500 if error else 0, "error": error})


def file_browser(req: Request, resp: Response, path, **kwargs):
    error = ''
    try:
        toolkit.file_browser(path=path)
    except Exception as e:
        error = str(e)

    return global_resp(resp=resp,
                       data={"data": None, "error": error},
                       kwargs={"errcode": 500 if error else 0, "error": error})
