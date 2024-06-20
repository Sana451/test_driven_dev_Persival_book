import random
import subprocess

from fabric import task, Connection
from invoke import UnexpectedExit

REPO_URL = "https://github.com/Sana451/test_driven_dev_Persival_book.git"
connection = Connection("sana451@89.111.170.80")


@task
def deploy(conn: Connection):
    site_folder = f"/home/{conn.user}/sites/{conn.host}"
    source_folder = site_folder + "/source"
    _create_directory_structure_if_necessary(conn, site_folder)
    _get_latest_source(conn, source_folder)
    _update_settings(conn, source_folder, repr(conn.host))
    _update_virtualenv(conn, source_folder)
    _update_static_files(conn, source_folder)
    _update_database(conn, source_folder)
    _update_nginx_settings(conn, source_folder)


def _create_directory_structure_if_necessary(conn: Connection, site_folder):
    """Создать структуру каталога, если нужно."""
    for subfolder in ("database", "static", "virtualenv", "source"):
        conn.run(f"mkdir -p {site_folder}/{subfolder}")


def _get_latest_source(conn: Connection, source_folder):
    """Получить самый свежий исходный код."""
    try:
        conn.run(f"ls {source_folder}/.git", hide=True)
        conn.run(f"cd {source_folder} && git fetch")
    except UnexpectedExit:
        conn.run(f"git clone {REPO_URL} {source_folder}")
    current_commit = subprocess.run(["git", "log", "-n", "1", "--format=%H"],
                                    capture_output=True
                                    ).stdout.decode("utf-8")
    conn.run(f"cd {source_folder} && git reset --hard {current_commit}")


def _update_settings(conn: Connection, source_folder, site_name):
    """Обновить настройки."""
    settings_path = source_folder + "/superlists/settings.py"

    conn.run(f"sed -i 's/DEBUG = True/DEBUG = False/g' {settings_path}", hide=True)
    conn.run(f"""sed -r -i "s/ALLOWED_HOSTS =.+$/ALLOWED_HOSTS = [{site_name},]/g" {settings_path}""", hide=True)

    secret_key_file = source_folder + "/superlists/secret_key.py"
    try:
        conn.run(f"ls {secret_key_file}", hide=True)
    except UnexpectedExit:
        conn.run(f"touch {secret_key_file}")
    finally:
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        conn.run(f"""echo "SECRET_KEY = '{key}'" > {secret_key_file}""")

    try:
        conn.run(f"grep -r 'from .secret_key import SECRET_KEY' {settings_path}")
    except UnexpectedExit:
        conn.run(f"echo \ >> {settings_path}")
        conn.run(f"echo 'from .secret_key import SECRET_KEY' >> {settings_path}")


def _update_virtualenv(conn: Connection, source_folder):
    """Обновить виртуальную среду."""
    virtualenv_folder = source_folder + '/../virtualenv'
    try:
        conn.run(f"ls {virtualenv_folder}/bin/pip", hide=True)
    except UnexpectedExit:
        conn.run(f"python3 -m venv {virtualenv_folder}")
    finally:
        conn.run(f"{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt", hide=False)


def _update_static_files(conn: Connection, source_folder):
    """Обновить статические файлы."""
    conn.run(f"cd {source_folder} && ../virtualenv/bin/python manage.py collectstatic --noinput")


def _update_database(conn: Connection, source_folder):
    """Обновить базу данных."""
    conn.run(f"""cd {source_folder} && ../virtualenv/bin/python manage.py migrate --noinput""")


def _update_nginx_settings(conn: Connection, source_folder):
    deploy_tools_folder = f"{source_folder}/deploy_tools"
    conn.run(f"ls {deploy_tools_folder} -a")

    conn.run(f"""sed -r -i "s/SITENAME/{conn.host}/g" {deploy_tools_folder}/nginx.template.conf""")
    conn.run(f"""sed -r -i "s/USERNAME/{conn.user}/g" {deploy_tools_folder}/nginx.template.conf""")
    conn.run(f"sudo rm -rf /etc/nginx/sites-available/{conn.host}")
    conn.run(f"sudo rm -rf /etc/nginx/sites-enabled/{conn.host}")
    conn.run(f"sudo cp {deploy_tools_folder}/nginx.template.conf /etc/nginx/sites-available/{conn.host}")
    conn.run(f"sudo ln -s /etc/nginx/sites-available/{conn.host} /etc/nginx/sites-enabled/{conn.host}")

    conn.run(f"""sed -r -i "s/SITENAME/{conn.host}/g" {deploy_tools_folder}/gunicorn-systemd.template.service""")
    conn.run(f"""sed -r -i "s/USERNAME/{conn.user}/g" {deploy_tools_folder}/gunicorn-systemd.template.service""")
    conn.run(f"sudo rm -rf /etc/systemd/system/gunicorn-systemd.template.service")
    conn.run(f"""sudo cp {deploy_tools_folder}/gunicorn-systemd.template.service 
                            /etc/systemd/system/gunicorn-systemd.template.service""")


def main(conn: Connection):
    deploy(conn)


if __name__ == "__main__":
    main(conn=connection)
