import datetime
import os
import re
from operator import itemgetter
from pathlib import Path

from app.db.api import patches_root_properties, patches_user_subdir_file_order, patches_user_subdir_order
from app.db.core import exec_cmd
from app.db.datasources import get_conn
from app.models import FillInstallSql
from app.tools import read_file, write_file, raise_error_from_dict


def get_readme_struct():
    return {'patchreadmehead': '', 'patchreadmebody': '', 'patchreadmefoot': '', 'patchReason': '', 'project': '', 'installComment': '', }


def patchlist(bv_id):
    """
    Get patch list from directory
    :param dir: directory
    :return: dict of patches
    """
    error, data = '', []
    try:
        error, patch_root_props = get_patch_root_props(bv_id)
        if not error:
            paths = sorted(Path(patch_root_props['dir']).iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
            nums = [item.name.replace(patch_root_props['dir'], '') for item in paths]
            descs = [get_patch_description(item) for item in paths]
            data = [{'p': p, 'd': d} for p, d in (zip(nums, descs))]
    except Exception as e:
        error = str(e)
    return {"data": data, "error": error}


def patchedit(dir, patchnum, alias):
    """
    Get dict for edit patch
    :param dir: patches subsystem directory
    :param patchnum: patch num
    :param alias: tnsnames alias
    :return: dict of patch props
    """
    error, patchdir, patchdirserv, patchserveraddr, aliaspos = '', '', '', '', 1
    patchusers, readme = [], get_readme_struct()
    try:
        patchdir = Path(dir, patchnum)
        patchdirserv = Path(patchdir, 'server')
        patchusers = '\n'.join(get_user_list_in_install_order(Path(patchdirserv, 'install.bat')))
        readme = load_readme(patchdirserv)
        tnsnamesinfo = get_server_info(alias)
        patchserveraddr = tnsnamesinfo['addr']
        aliaspos = tnsnamesinfo['aliaspos']
    except Exception as e:
        error = f"{e}"

    return {"readme": readme, "patchusers": patchusers, "patchserveraddr": patchserveraddr, "aliaspos": aliaspos, "patchdir": patchdir, "patchdirserv": patchdirserv, "error": error}


def deleteFile(path):
    """
    Delete file from edit patch
    :param path: file path
    :return: dict of patch new struct
    """
    error = ''
    try:
        Path(path).unlink() if not Path(path).is_dir() else Path(path).rmdir()
    except Exception as e:
        error = str(e)

    return {"error": error}


def saveFile(path, alias, filetext):
    """
    Save file
    :param path: file path
    :param alias: tnsnames alias
    :param filetext: file text
    :return: dict of some file props
    """
    error, patchserveraddr, aliaspos = '', '', ''
    try:
        write_file(get_tns_path() if path == 'TNSNAMES' else Path(path), filetext.split('\r'), rewrite=True)
        if alias:
            tnsnamesinfo = get_server_info(alias, filetext)
            patchserveraddr = tnsnamesinfo['addr']
            aliaspos = tnsnamesinfo['aliaspos']
    except Exception as e:
        error = str(e)

    return {"patchserveraddr": patchserveraddr, "aliaspos": aliaspos, "error": error}


def patchStructure(patchdir):
    """
    Get patch structure
    :param patchdir: patch directory
    :return: dict of patch struct
    """
    error, data = '', []
    try:
        data = execute_load_structure(Path(patchdir))
    except Exception as e:
        error = str(e)

    return {"data": data, "error": error}


def openFile(path):
    """
    Open file from patch
    :param patchdir: patch directory
    :param path: file path
    :return: file text
    """
    error, filetext = '', ''
    try:
        (path_, filetext) = read_tnsnames() if path == 'TNSNAMES' else ('', read_file(Path(path)))
    except Exception as e:
        error = str(e)
    print("openFile ... ", path, {"filetext": filetext, "error": error})
    return {"filetext": filetext, "error": error}


def set_proj(project, bv_id):
    conn = get_conn()
    res = exec_cmd(conn=conn,
                   cmdtext=f"insert or ignore into reporter_patchesproj(name, bittlvers_id) values (:name, :bittlvers_id)",
                   cmdparams={'name': project, 'bittlvers_id': bv_id})
    raise_error_from_dict(res)


def patchCreate(bv_id, patchdir, patchdirserv, patchusers, scriptdirs, scriptfiles, readmehead, readmebody, readmefoot, project, clientdir):
    error = ''
    print('... partch create ... ', bv_id, patchdir, patchdirserv, patchusers, scriptdirs, scriptfiles, readmehead, readmebody, readmefoot, project, clientdir)
    try:
        print('mkdir ... ', Path(patchdirserv).mkdir(parents=True, exist_ok=True))
        sqlplusinstall = ''
        for user in patchusers.split():
            # sqlplus install lines
            sqlplusinstall = f'{sqlplusinstall}cd ' + ('../' if sqlplusinstall else '')
            sqlplusinstall = f'{sqlplusinstall}{user}\nsqlplus /nolog @install.sql\n'
            # create user subdirs and files
            for row1 in scriptdirs:
                Path(patchdirserv, user, row1).mkdir(parents=True, exist_ok=True)
                [write_file(Path(patchdirserv, user, row1, x)) for x in scriptfiles if row1 == 'script']
        # create client dir
        Path(patchdir, 'client').mkdir(exist_ok=True) if clientdir else None
        # create top files
        write_file(Path(patchdirserv, 'install.bat'), f'mkdir log\nchcp 1251\nset NLS_LANG = RUSSIAN_AMERICA.CL8MSWIN1251\n{sqlplusinstall}', rewrite=True)
        # create Readme file
        write_file(path=Path(patchdirserv, 'readme.txt'),
                   text=f"{readmehead}\n{readmebody}\n\n{readmefoot}".splitlines(keepends=True),
                   rewrite=True,
                   newline='\n')
        set_proj(project, bv_id)
    except Exception as e:
        print('... partch create error... ', str(e))
        error = str(e)

    return {"error": error}


def fillInstallSql(body: FillInstallSql):
    error = ''
    try:
        for user in get_user_list_in_install_order(Path(body.patchdirserv, 'install.bat')):
            sysdba = ' as sysdba' if user == 'sys' else ''
            text = [
                f"spool ..\{Path('log', body.patchnum)}.{user}.log\nset define off\nset serverout on\n"
                f"prompt connect {user}@{body.patchalias}{sysdba};\n"
                f"connect {user}@{body.patchalias}{sysdba};\nprompt\ntimin start\n\n"
                f"insert into {body.patchowner}.patch_history (patch_name, script_name) values ('{body.patchnum}', '{user}\install.sql');\ncommit;\n"
            ]
            # print('ISB',get_element(form, 'isbinstall'))
            if user.lower() == 'isb' and body.isbinstall:
                text.append('whenever sqlerror exit 1\nexec db.prc_is_bimeg\nwhenever sqlerror continue\n')
            # get files from dir
            install_sql_rows = []
            dirs_ = (x for x in Path(body.patchdirserv, user).iterdir() if x.is_dir())
            files_ = (x for x in [y.iterdir() for y in dirs_])
            for files in [y for y in files_]:
                for file in [x for x in files if x.is_file()]:
                    # print('parent = ',Path(file.parent).name, 'file = ',file.name)
                    # ???????????? ???????????????????? ?????????? ?????????? ?? ??????????, ?????????????? ?????????? ???????????????????? ?????????? ?? ?????????????? ??????????
                    fileorder = f"{get_file_order('dirs', file.parent.name)}{get_file_order('files', file.name)}"
                    shoerr = '\nsho err' if file.parent.name in ('pkg', 'trg', 'bdy', 'prc', 'proc', 'func', 'fnc') else ''
                    install_sql_rows.append({"row": f'\nprompt{("-" * 55)}  {Path(file.parent.name, file.name)}\n'
                                                    f'@@{Path(file.parent.name, file.name)}{shoerr}',
                                             "order": fileorder})
            [text.append(rec['row']) for rec in sorted(install_sql_rows, key=itemgetter('order'))]
            text.append('\n\nprompt\ntimin stop\nspool off\nexit;\n')
            write_file(Path(body.patchdirserv, user, 'install.sql'), text, rewrite=True)
    except Exception as e:
        # error = f"fillInstall: {e}"
        error = f"{e}"

    return {"error": error}


def patchInstall(patchdirserv):
    error = ''
    try:
        os.system(f'cmd.exe /C "cd {patchdirserv} && @install.bat"')
    except Exception as e:
        error = str(e)

    return {"error": error}



def get_file_order(source, name):
    res = {}
    if source == 'dirs':
        res = patches_user_subdir_order(name)
    elif source == 'files':
        res = patches_user_subdir_file_order(name)
    if res['error']:
        raise Exception(res['error'])
    return res['data'][0] if res['data'] else 100


def get_patch_description(patchdir):
    description = ''
    text = read_file(Path(patchdir, 'server', 'readme.txt'))
    for rec in (x for x in text.splitlines()[1:9] if x and not re.search(r"????????:|??????????????????:|????????????????:|?????????????????????? ??????????????????:", x)):
        description = f'{description} | ' if description else ''
        description = f'{description}{rec.strip().replace("  ", " ")}'
    return description


def get_user_list_in_install_order(file):
    return [x[3:].replace('../', '') for x in read_file(file).splitlines() if x[0:2] == 'cd']


def load_readme(patchdirserv):
    data = get_readme_struct()
    text = read_file(Path(patchdirserv, 'readme.txt'))
    if not text:
        return data
    data['patchreadmehead'] = text[0:text.find('  -') - 1]
    data['patchreadmebody'] = text[text.find('  -'):text.find('?????????????????????? ??????????????????:') - 2]
    data['patchreadmefoot'] = text[text.find('?????????????????????? ??????????????????:'):]
    try:
        data['patchReason'] = data['patchreadmehead'][data['patchreadmehead'].find('??????????????????: ') + len('??????????????????: '):
                                                      data['patchreadmehead'].find('????????????????:') - 2]
    except Exception as e:
        data['patchReason'] = e
    data['project'] = data['patchreadmehead'].splitlines()[1]
    textarr = data['patchreadmefoot'].splitlines()
    data['installComment'] = textarr[textarr.index('?????????????????????? ??????????????????:') + 1].strip()
    return data


def execute_load_structure(patchdir):
    def scan_dir(space, path):
        dir = (x for x in sorted([{'path': x, 'isDir': x.is_dir(), 'order': space + i + (2000 if x.name == 'log' and x.is_dir() else 1000 if x.is_dir() else 0)}
                                  for i, x in enumerate(path.iterdir()) if x.name != '.svn'],
                                 key=itemgetter('order')))
        for rec in dir:
            size = rec['path'].stat().st_size if not rec['isDir'] else 0
            time = datetime.datetime.fromtimestamp(rec['path'].stat().st_mtime).strftime('%d.%m.%Y %H:%M:%S') if not rec['isDir'] else ''
            error = rec['path'].suffix == '.log' and isinstance(re.search(r"ERROR|ORA-", read_file(rec['path'], 'windows-1251')), re.Match)
            tree.append(dict(space=space, name=rec['path'].name, path=rec['path'].as_posix(), is_dir=rec['isDir'], size=size, time=time, error=error))
            scan_dir(space + 20, rec['path']) if rec['isDir'] else None

    tree = []
    scan_dir(0, patchdir)
    # print('tree = ', tree)
    return tree


def get_tns_path():
    return Path(os.environ['TNS_ADMIN'], 'tnsnames.ora')


def read_tnsnames():
    path = get_tns_path()
    return path, read_file(path)


def get_server_info(alias, ftext=''):
    if not ftext:
        path, ftext = read_tnsnames()
    ftext = ftext.upper()
    alias = alias.upper()
    aliaspos, linealiaspos = -1,-1
    host, port, service = '','',''
    for line in ftext.replace(' ', '').splitlines():
        if linealiaspos == -1:
            linealiaspos = line.find(alias + '=', 0, len(alias + '='))
        if linealiaspos == -1:
            continue
        if host == '':
            hostind = line.find('HOST=')
            if hostind == -1:
                continue
            host = line[hostind + 5:line.find(')', hostind + 5)]
        if port == '' and host != '':
            portfind = line.find('PORT=')
            if portfind == -1:
                continue
            port = line[portfind + 5:portfind + 9]
        if service == '' and port != '':
            servicefind = line.find('SERVICE_NAME=')
            if servicefind == -1:
                servicefind = line.find('SID=')
            if servicefind == -1:
                continue
            servicefind = line.find('=', servicefind) + 1
            service = line[servicefind:line.find(')', servicefind)].lower()
            break
    if host != '':
        aliaspos = ftext.find(f"\n{alias} ")+1

    # print("get_server_info ... ", f'{host}:{port} / {service}', "   alias = ", alias, "  ... aliaspos = ", aliaspos)
    return {"addr": f'{host}:{port} / {service}', "aliaspos": aliaspos}


def get_patch_root_props(bv_id):
    result = patches_root_properties(bv_id)
    # if result['error']:
    #     raise Exception(result['error'])
    return result['error'], result['data'][0]
