import re
from pathlib import Path

from starlette.requests import Request
from starlette.responses import Response

from app.db import api
from app.responses import global_resp
from app.toolkit import write_file, get_element


def get(req: Request, resp: Response, key, **kwargs):
    result, error = {}, ''
    try:
        if key == "tnsPaths":
            result = api.tnsnames()
        elif key == "services":
            result = api.services()
        elif key == "projects":
            def get_readme(path):
                return [
                    {"file": x.name, "path": x, "ext": x.suffix.lower()} for x in list(Path(path).rglob("*"))
                    if re.search(r"(_|!|^)readme", x.stem, re.IGNORECASE) and
                       not re.search(r"~|\\.svn\\|\\.pytest_cache\\|\\venv\\|\\components\\", str(x), re.IGNORECASE)
                ] if path else ''

            result['data'] = [{"name": x["name"], "path": x["path"], "description": x["description"], "docspath": x["docspath"], "readme": get_readme(x["path"])}
                              for x in api.projects()["data"]]
    except Exception as e:
        error = str(e)
    error = error or get_element(result, 'error', '')

    return global_resp(resp=resp, data={"data": get_element(result, 'data', []), "error": error})


def post(req: Request, resp: Response, key, body):
    result, error = {}, ''
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
            result = re.sub(body['replaceFrom'].replace('+', '\+') + '+', body['replaceTo'], result)
        elif key == "tnsSave":
            # print('paths = ', body['tnsPaths'], '..... text = ',body['tnsText'][:300])
            [write_file(path=x['path'], text=body['tnsText'], rewrite=True) for x in body['tnsPaths']]

    except Exception as e:
        error = str(e)
    error = error or get_element(result, 'error', '')

    return global_resp(resp=resp, data={"data": result, "error": error})
