import base64
import time
from fastapi import Response
from starlette.status import HTTP_200_OK

from app.logapi import logerror, logresponse, logconsole
from app.tools import get_element


def global_resp(resp: Response, data=None, log_response=True, errcode: int = HTTP_200_OK, error: str = '', kwargs=None):
    elapsed = "%.1f" % float(time.time() - kwargs["startTime"]) if get_element(kwargs, "startTime") else 0.0
    resp.status_code = HTTP_200_OK if errcode < HTTP_200_OK else errcode
    print(' ----- RESPONSE data = ', data)
    kwargs['status'] = resp.status_code
    kwargs['elapsed'] = elapsed
    # resp.headers["access-control-allow-credentials"] = 'True'
    # resp.headers["Access-Control-Allow-Origin"] = "*"
    # resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    if resp.status_code > HTTP_200_OK:
        logerror(msg=f'({errcode}){error}', kwargs=kwargs)
    else:
        logresponse(msg=f'({errcode}){error}: {data}', kwargs=kwargs) if log_response else logconsole(msg=f'({errcode}){error}: {data}', kwargs=kwargs)
    return data


