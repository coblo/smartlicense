# -*- coding: utf-8 -*-
import os
import sys
from fabric.api import task, local
sys.path.append(os.path.dirname(__file__))
from smartlicense.settings import SCRACTH_DB, BASE_DIR


DIR_MIGRATIONS = os.path.join(BASE_DIR, 'smartlicense', 'migrations')


@task
def reset():
    """Reset local development environment"""

    print('Update requirements')
    local('pip install -U -r requirements.txt')

    if os.path.exists(SCRACTH_DB):
        print('Remove development db:', SCRACTH_DB)
        os.remove(SCRACTH_DB)

    if os.path.exists(DIR_MIGRATIONS):
        print('Delete migration files')
        for f in os.listdir(DIR_MIGRATIONS):
            if f == '.gitignore':
                continue
            file_path = os.path.join(DIR_MIGRATIONS, f)
            try:
                if os.path.isfile(file_path):
                    print('Deleting:', file_path)
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    print('Initialize fresh Django database')
    local('python manage.py makemigrations smartlicense')
    local('python manage.py migrate --noinput --run-syncdb')
    local('python manage.py create_demo_user')
    local('python manage.py loaddata fixtures')
    local('python manage.py import_node_addrs')
    local('python manage.py import_demo_content')


@task
def dump():
    out_dir = os.path.join(BASE_DIR, 'smartlicense', 'fixtures')
    out_file = os.path.join(out_dir, 'fixtures.yaml')

    os.makedirs(out_dir, exist_ok=True)
    local(
        'python manage.py dumpdata --format yaml --output {} '
        'smartlicense.RightsModule '
        'smartlicense.ActivationMode '
        'smartlicense.Template'.format(out_file)
    )

@task
def load():
    local('python manage.py loaddata fixtures')
