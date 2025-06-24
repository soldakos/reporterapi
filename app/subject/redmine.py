from redminelib import Redmine
from redminelib.resultsets import ResourceSet

# def init():
#     global username, password, urlroot, urlissues
#     username = Settings.objects.get(name='RedmineUsr').value
#     password = Settings.objects.get(name='RedminePwd').value
#     urlroot = Settings.objects.get(name='RedmineRootUrl').value
#     urlissues = Settings.objects.get(name='RedmineIssuesUrl').value
from app.models import RedmineCreate
from app.toolkit import get_date_now_format


def get_user(username, password, urlroot, id) -> dict:
    redmine = Redmine(url=urlroot, username=username, password=password)
    if id == -1:
        result = dict(redmine.user.get('current'))
    else:
        result = dict(redmine.user.get(resource_id=id))
    return dict(id=result.get("id"), firstname=result.get("firstname"), login=result.get("login"), lastname=result.get("lastname"), )


def prepare_text(text):
    def get_separator(res):
        return '\n' if res else ''

    res = ''
    for line in [x for x in text.replace('\t', ' ').replace('  ', ' ').splitlines() if x]:
        res = res + get_separator(res) + line.replace('\t', ' ').replace('  ', ' ')
    return res


# def execute_create_redmine_issue(username, password, urlroot, urlissues, project_id, subject, description, svn_url, assigned_to_id, parent_issue_id, what_todo):
def execute_create_redmine_issue(params: RedmineCreate):
    issue = {}
    try:
        redmine = Redmine(url=params.urlroot, username=params.username, password=params.password)
        svn_url = f'svn://{params.svn_url[params.svn_url.find("@") + 1:]}'
        issue = redmine.issue.create(project_id=params.project_id,
                                     subject=params.subject,
                                     tracker_id=4,
                                     description=params.description,
                                     status_id=7,
                                     priority_id=2,
                                     assigned_to_id=params.assigned_to_id,
                                     watcher_user_ids=[],
                                     parent_issue_id=params.parent_issue_id,
                                     start_date=get_date_now_format('short'),
                                     due_date=None,
                                     estimated_hours=0,
                                     done_ratio=0,
                                     custom_fields=[
                                         {'id': 8, 'name': 'Расположение патча SVN', 'value': svn_url},
                                         {'id': 9, 'name': 'Что проверить', 'value': params.what_todo},
                                         {'id': 12, 'name': 'Ссылка на протокол', 'value': ''},
                                         {'id': 13, 'name': 'Ссылка на FTP', 'value': ''},
                                         {'id': 18, 'name': 'Проверяющий патч'}
                                     ],
                                     uploads=[])
        issue = dict(issue)
        issue['url'] = f'{params.urlissues}/{issue["id"]}'
    except Exception as e:
        issue["error"] = str(e)

    return issue


def get_patch_format(subject):
    return subject[:subject.find('(') if '(' in subject else subject.find(' ') if ' ' in subject else 1000].strip()


def redmine_issues(username, password, urlroot, urlissues, redmine_project_url):
    """
    Get redmine issues
    :param username: Redmine username
    :param password: Redmine password
    :param urlroot: Redmine url root
    :param urlissues: Redmine url issues
    :param redmine_project_url: Redmine project url
    :return: dict of redmine issues
    """
    error, issues = '', []
    try:
        url = f'{urlroot}{redmine_project_url}'
        print(f"url={url}, username={username}, password={password} | urlroot = {urlroot},  urlissues = {urlissues}")
        redmine: Redmine = Redmine(url=url, username=username, password=password)
        print(f"redmine = {redmine}, type {type(redmine)}")
        print(f"get_user(username, password, urlroot, -1)['id'] = {get_user(username, password, urlroot, -1)['id']}")
        filtered: ResourceSet = redmine.issue.filter(tracker_id=6, status_id=2, assigned_to_id=get_user(username, password, urlroot, -1)['id'])
        # print(f"redmine.issue.filter(tracker_id=6, status_id=2, assigned_to_id=get_user(username, password, urlroot, -1)['id']) = {filtered}, type {type(filtered)}")
        # print(f"count = {filtered.values_list()}")
        # for i, item in enumerate(redmine.issue.filter(tracker_id=6, status_id=2, assigned_to_id=get_user(username, password, urlroot, -1)['id'])):
        for i, item in enumerate(filtered):
            print('issue = ', item)
            item_ = dict(item)
            dates = item_['created_on'][:item_['created_on'].find('Z')] + ' / ' + item_['updated_on'][:item_['updated_on'].find('Z')]
            dates = dates.replace('T', ' ')
            issues.append({'url': f'{urlissues}/{item_["id"]}',
                           'subject': item_['subject'],
                           'patchnum': get_patch_format(item_['subject']),
                           'project': item_['project'],
                           'id': item_['id'],
                           'author': item_['author']['name'],
                           'description': prepare_text(item_['description']),
                           'reason': item_['custom_fields'][0]['value'],
                           'tester': get_user(username, password, urlroot, item_['custom_fields'][1]['value']),
                           'dates': dates,
                           'custom_fields': item_['custom_fields'],
                           'child': []
                           })
            # child tasks: get last task and break
            for subitem in redmine.issue.filter(parent_id=item_['id'], status_id='*', sort='id:desc'):
                # print('subitem=', dict(subitem))
                issues[i]['child'].append({'id': dict(subitem)['id'],
                                           'statusid': dict(subitem).get('status', dict())['id'],
                                           'statusname': dict(subitem).get('status', dict())['name']})
                break
    except Exception as e:
        raise
        # error = f"{e} ... traceback = {format_traceback()}"

    return {"data": issues, "issuesurl": '', "issue": [], "error": error}
