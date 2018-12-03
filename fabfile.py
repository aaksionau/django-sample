from fabric.api import task, env, run, cd, local, settings, abort
from fabric.operations import prompt, put
from fabric.context_managers import prefix
from fabric.contrib.console import confirm

PROJECT_NAME = "echb"

APP_DIR = f"{PROJECT_NAME}_project/echb/"
APP_STATIC_DIR = f"{PROJECT_NAME}_static/"
APP_APACHE_DIR = f"{PROJECT_NAME}_project/apache2/"

PYTHON_VERSION = "3.6"

env.use_ssh_config = True
env.hosts = ["webfaction"]
env.remote_app_dir = f'/home/paloni/webapps/{APP_DIR}'
env.remote_app_static_dir = f'/home/paloni/webapps/{APP_STATIC_DIR}'
env.remote_apache_dir = f'/home/paloni/webapps/{APP_APACHE_DIR}'

command = "python manage.py {} --settings=echb.settings.local"


@task
def runserver():
    local(command.format('runserver'))


@task
def makemigrations():
    local(command.format('makemigrations'))


@task
def migrate():
    local(command.format('migrate'))


@task
def deploy():
    test_results = test()
    commit()
    push()
    if test_results:
        deploy_to_server()


def test():
    with settings(warn_only=True):
        result = local(
            f"python manage.py test --settings={PROJECT_NAME}.settings.test")
        if result.failed and not confirm("Tests failed. Continue?"):
            abort("Aborted at user request.")
            return False
        else:
            return True


def push():
    local("git push origin master")


def commit():
    message = prompt("Enter a git commit message: ")
    local('git add . && git commit -am "{}"'.format(message))


def deploy_to_server():
    with cd(f'{env.remote_app_dir}'):
        run('git pull origin master')

    run(f'cd {env.remote_app_dir}/{PROJECT_NAME}/; python{PYTHON_VERSION} manage.py collectstatic --settings={PROJECT_NAME}.settings.production --noinput')

    run(f'cd {env.remote_app_dir}/{PROJECT_NAME}/{PROJECT_NAME}/; touch wsgi.py;')
