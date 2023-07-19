from datetime import datetime
import pysvn

client = pysvn.Client()


def svnData(path):
    error, svn_patch, headrev = '', '', '',
    try:
        svn_patch = get_url_from_path(path)
        headrev = get_revision(svn_patch) if svn_patch else ''
    except Exception as e:
        error = f"{e}"
    return {"svn_patch": svn_patch, "headrev": headrev, "error": error}


def get_url_from_path(path):
    print('svn client.info2(url_or_path=path), ', client.info2(url_or_path=path))
    return client.info2(url_or_path=path)[0][1]['URL']


# def get_root_url(bittlvers_id):
#     result = svnurl(bittlvers_id)
#     if result['error']:
#         raise Exception(result['error'])
#     return result['data'][0][0]


def get_revision(url):
    rev = ''
    try:
        rev = client.info2(url_or_path=url)[0][1]['last_changed_rev'].number
    except Exception as exc:
        print(exc)
    return rev


def commit_svn(url_root, url_patch, patchnum, patchdir, usr, pwd):
    def get_login(realm, username, may_save):
        return True, usr, pwd, True

    def get_log_message():
        return True, 'Creating...'

    def svn_mkdir():
        url = url_root
        year = str(datetime.today().strftime('%Y'))
        month = year + str(datetime.today().strftime('%m'))
        for dir in [year, month, patchnum]:
            url = f'{url}/{dir}'
            try:
                client.mkdir(url_or_path=f'{url}')
            except pysvn.ClientError as exc:
                if str(exc).startswith("File already exists"):
                    print(exc)
                else:
                    raise
        return url

    url_patch_new, rev, error = '', '', ''
    try:
        client.callback_get_login = get_login
        client.callback_get_log_message = get_log_message
        url_patch_new = url_patch if url_patch else svn_mkdir()
        client.checkout(url=url_patch_new, path=patchdir, recurse=True)
        client.add(path=patchdir, recurse=True, force=True, ignore=False, add_parents=True, autoprops=False)
        checkin = client.checkin(path=patchdir, log_message='Adding...' if not url_patch else 'Changing...', recurse=True)
        rev = get_revision(url_patch_new)
    except Exception as e:
        error = str(e)

    return {"url_patch_new": url_patch_new, "rev": rev, "error": error}
