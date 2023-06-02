import datetime
import os
import re
from operator import itemgetter
from pathlib import Path
from shutil import copy

from app.db.api import patches_root_properties, patches_user_subdir_file_order, patches_user_subdir_order, projects
from app.db.core import exec_cmd
from app.db.datasources import get_conn
from app.models import FillInstallSql
from app.toolkit import read_file, write_file, raise_error_from_dict, get_server_info, choose_files


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


def copyToFolder(path, project, bv_id):
    error, data = '', []
    if path:
        try:
            data = projects(global_name=project, bv_id=bv_id)["data"]
            project_path = '' if not data else data[0]['path']
            result = choose_files(path=project_path, filters=["*exe; *txt", "*.*"])
            [copy(x, path) for x in result]
        except Exception as e:
            error = str(e)

    return {"error": error}


def set_proj(project, bv_id):
    conn = get_conn()
    res = exec_cmd(conn=conn,
                   cmdtext=f"insert or ignore into reporter_projects(name, global_name, bittlvers_id) values (:name, :global_name, :bittlvers_id)",
                   cmdparams={'name': project, 'global_name': project, 'bittlvers_id': bv_id})
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
                text.append('whenever sqlerror exit 1\npost db.prc_is_bimeg\nwhenever sqlerror continue\n')
            # get files from dir
            install_sql_rows = []
            dirs_ = (x for x in Path(body.patchdirserv, user).iterdir() if x.is_dir())
            files_ = (x for x in [y.iterdir() for y in dirs_])
            for files in [y for y in files_]:
                for file in [x for x in files if x.is_file()]:
                    # print('parent = ',Path(file.parent).name, 'file = ',file.name)
                    # склеим порядковый номер папки и файла, получив общий порядковый номер в разрезе юзера
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
        # os.system(f'cmd.exe /C "cd /d {patchdirserv} && @install.bat"')
        import subprocess
        subprocess.run(["start", "/wait", "cmd", "/C", f"cd /d {patchdirserv} && install.bat"], shell=True)
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
    for rec in (x for x in text.splitlines()[1:9] if x and not re.search(r"Патч:|Основание:|Описание:|Особенности установки:", x)):
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
    data['patchreadmebody'] = text[text.find('  -'):text.find('Особенности установки:') - 2]
    data['patchreadmefoot'] = text[text.find('Особенности установки:'):]
    try:
        data['patchReason'] = data['patchreadmehead'][data['patchreadmehead'].find('Основание: ') + len('Основание: '):
                                                      data['patchreadmehead'].find('Описание:') - 2]
    except Exception as e:
        data['patchReason'] = e
    data['project'] = data['patchreadmehead'].splitlines()[1]
    textarr = data['patchreadmefoot'].splitlines()
    data['installComment'] = textarr[textarr.index('Особенности установки:') + 1].strip()
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


def get_patch_root_props(bv_id):
    result = patches_root_properties(bv_id)
    # if result['error']:
    #     raise Exception(result['error'])
    return result['error'], result['data'][0]
