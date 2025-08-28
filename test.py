import redminelib
tt = {'relations': None, 'time_entries': None, 'children': None, 'attachments': None, 'changesets': None, 'journals': None, 'watchers': None, 'allowed_statuses': None, 'id': 5239,
      'project': {'id': 12, 'name': '* СИСТЕМА АСР 1.3.5 '}, 'tracker': {'id': 4, 'name': 'Тестирование'}, 'status': {'id': 7, 'name': 'Патч передан на тестирование'},
      'priority': {'id': 2, 'name': 'Нормальный'}, 'author': {'id': 16, 'name': 'Константин Солдатов'}, 'assigned_to': {'id': 18, 'name': 'Ирина Шегай'},
      'parent': {'id': 5237}, 'subject': 'Проверить патч PRX.1.2101', 'description': '', 'start_date': '2025-07-21', 'done_ratio': 0, 'spent_hours': 0.0, 'total_spent_hours': 0.0,
      'custom_fields': [{'id': 8, 'name': 'Расположение патча SVN', 'value': 'svn://192.168.100.28/bittl135/trunk/patch/2025/202507/PRX.1.2101'},
                        {'id': 9, 'name': 'Что проверить', 'value': 'Снапшот osm.customer_account_db_division должен содержать данные из СРМ: select * from cust.customer_account\nwhere division_id = 11'},
                        {'id': 12, 'name': 'Ссылка на протокол', 'value': ''}, {'id': 13, 'name': 'Ссылка на FTP', 'value': ''}, {'id': 18, 'name': 'Проверяющий патч'}],
      'created_on': '2025-07-21T12:32:20Z', 'updated_on': '2025-07-21T12:32:20Z', 'url': 'http://192.168.100.27/issues/5239', 'manager': redminelib.managers.IssueManager, 'internal_id': 5239}

print(tt)

tt = {key: val for key, val in tt.items() if key != 'manager'}
print(tt)

print(bool(''))
