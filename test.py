from pathlib import Path

import oracledb

oracledb.init_oracle_client()
conn = oracledb.connect(dsn="""db/1@(DESCRIPTION =
  (ADDRESS_LIST =
   (ADDRESS = (PROTOCOL = TCP)(HOST = 10.8.26.22)(PORT = 1521))
  )
 (CONNECT_DATA =
  (SERVICE_NAME = bittl)
 )
)""")
with conn.cursor() as cur:
    cur.execute('select sysdate from dual')
    print(cur.fetchall())


def patchInstall(patchdirserv):
    error = ''
    try:
        import subprocess
        # Формируем команду для запуска install.bat в нужной директории
        # /d — смена диска, /c — выполнить команду и выйти
        # # os.system(f'cmd.exe /C "cd /d {patchdirserv} && @install.bat"')
        import os
        import sys
        subprocess.run(["start", "/wait", "cmd", "/C", f"cd /d {patchdirserv} && call install.bat"],
                       shell=True,
                       check=True,
                       env=os.environ,
                       # stdout=sys.stdout, stderr=sys.stderr,
                       # start_new_session=True,
                       # capture_output=True,
                       # encoding='windows-1251'
                       # encoding='utf8',
                       )
        # p.check_returncode()
        # subprocess.run(f'cmd.exe /c "cd /d {patchdirserv} && install.bat"', shell=True, check=True)
    except Exception as e:
        print(f"patchInstall error  = {e}")


def patchInstall_(patchdirserv):
    error = ''
    try:
        import subprocess
        # Формируем команду для запуска install.bat в нужной директории
        # /d — смена диска, /c — выполнить команду и выйти
        # # os.system(f'cmd.exe /C "cd /d {patchdirserv} && @install.bat"')
        import os
        import sys
        subprocess.run(f'cmd.exe /c "cd /d {patchdirserv} && call install.bat"', shell=True, check=True,
                       env=os.environ,
                       ).check_returncode()
    except Exception as e:
        print(f"patchInstall error  = {e}")


# patchInstall(r"d:\Patch\1.3\URX.1.541\server")
patchInstall(Path(r"d:\\Patch\\1.3\\URX.1.541\\server"))
# patchInstall_(Path(r"d:\\Patch\\1.3\\URX.1.541\\server"))
