import datetime
import os
import re
from operator import itemgetter
from pathlib import Path

from starlette.requests import Request
from starlette.responses import Response

from app.responses import global_resp


def exec(req: Request, resp: Response, key, body):
    error, result = '', ''
    try:
        if key == "exception":
            # prepare param list
            parlist = []
            for line in body['generateExceptionIn'].lower().replace(',', '').replace('\t', ' ').replace('  ', ' ').split('\n'):
                line = line.strip()
                if line == '' or line[0:1] in ('(', ')'):
                    continue
                while True:
                    if line.find(' ', 0, 1) == -1: break
                    line = line[1:]
                if line.find('(') != -1:
                    line = line[0:line.find('(')]
                elif line.find(' ') != -1:
                    line = line[0:line.find(' ')]
                parlist.append(line.replace(' ', ''))
            # prepare result
            params, endofproc = '', ''
            for row in parlist:
                params = params + (body['generateExceptionParamsDivider'] if params else '\'') + row + '=\'||' + row
            if body['generateExceptionLogType'] == 'EventLog':
                endofproc = '    set_event_log(v_event, v_params, null);' \
                            '\nexception\n    when others then\n        rollback;' \
                            '\n        set_event_log(v_event, v_params, dbms_utility.format_error_stack || dbms_utility.format_error_backtrace);' \
                            '\n        raise;\nend;'

            result = '    v_event varchar2(255) := lower($$plsql_unit)||\'.\';\n    v_params varchar2(32767) := ' + params + ';\nbegin\n\n\n' + endofproc
        elif key == "package":
            packagenameend = body['packageName'][body['packageName'].find('.') + 1:] if '.' in body['packageName'] else body['packageName']
            result = f"create or replace package {body['packageName']} is\n\n" \
                     f"    {body['packageComment']}\n\n" \
                     f"    /**/\n" \
                     f"    procedure prc(in_param number);\n\n" \
                     f"end {packagenameend};\n" \
                     f"/\n" \
                     f"create or replace package body {body['packageName']} is\n\n" \
                     f"    /**/\n" \
                     f"    procedure prc(in_param number) is\n" \
                     f"        v_event varchar2(255) := lower($$plsql_unit)||\'.prc\';\n" \
                     f"        v_params varchar2(32767) := \'in_param=\'||in_param;\n" \
                     f"    begin\n\n" \
                     f"        set_event_log(v_event, v_params, null);\n" \
                     f"    exception\n" \
                     f"        when others then\n" \
                     f"            rollback;\n" \
                     f"            set_event_log(v_event, v_params, dbms_utility.format_error_stack || dbms_utility.format_error_backtrace);\n" \
                     f"            raise;\n" \
                     f"    end;\n\n" \
                     f"end {packagenameend};\n" \
                     f"/\n"
        elif key == "replace":
            result = re.sub("(\r\n|\n\n|\t|\r)+", "\n", body['replaceIn'])
            result = re.sub(body['replaceFrom'] + '+', body['replaceTo'], result)

    except Exception as e:
        error = str(e)

    return global_resp(resp=resp,
                       data={"data": result, "error": error},
                       kwargs={"errcode": 500 if error else 0, "error": error})
