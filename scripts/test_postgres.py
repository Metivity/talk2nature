"""Test both database adapters in an isolated local PostgreSQL cluster.

Requires existing initdb/pg_ctl binaries and the admin virtual environment.
Creates only disposable synthetic data; never connects to an existing cluster.
"""
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def main():
    import psycopg
    initdb, pg_ctl = shutil.which('initdb'), shutil.which('pg_ctl')
    if not initdb or not pg_ctl:
        raise SystemExit('Install PostgreSQL tools separately; this script does not download or reuse a server.')
    work = Path(tempfile.mkdtemp(prefix='t2n-pg-test-'))
    started = False
    stopped = True
    try:
        password = secrets.token_urlsafe(32)
        password_file = work / 'initial-password'
        fd = os.open(password_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'w') as output:
            output.write(password + '\n')
        cluster = work / 'cluster'
        subprocess.run([initdb, '-D', str(cluster), '--no-locale', '--encoding=UTF8',
                        '--auth=scram-sha-256', '--username=t2n_test', f'--pwfile={password_file}'],
                       check=True, capture_output=True, text=True)
        password_file.unlink()
        with socket.socket() as available:
            available.bind(('127.0.0.1', 0))
            port = available.getsockname()[1]
        # TCP loopback only. Disable Unix sockets to avoid path-length/platform differences.
        subprocess.run([pg_ctl, '-D', str(cluster), '-l', str(work/'server.log'), '-w',
                        '-o', f"-h 127.0.0.1 -p {port} -k ''", 'start'],
                       check=True, capture_output=True, text=True)
        started = True
        prefix = f'postgresql://t2n_test:{quote(password, safe="")}@127.0.0.1:{port}/'
        with psycopg.connect(prefix+'postgres?sslmode=disable', autocommit=True) as db:
            db.execute('CREATE DATABASE t2n_test_workbench')
            db.execute(psycopg.sql.SQL('CREATE ROLE t2n_app WITH LOGIN PASSWORD {}').format(psycopg.sql.Literal(password)))
        environment = dict(os.environ)
        environment['T2N_TEST_DATABASE_URL'] = prefix+'t2n_test_workbench?sslmode=disable'
        environment['T2N_TEST_APP_DATABASE_URL'] = prefix.replace('t2n_test:', 't2n_app:')+'t2n_test_workbench?sslmode=disable'
        print('Running against a fresh, password-protected, loopback-only PostgreSQL test cluster.', flush=True)
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'admin/tests', '-v'],
                                cwd=ROOT, env=environment)
        return result.returncode
    finally:
        if started:
            stopped = subprocess.run([pg_ctl, '-D', str(work/'cluster'), '-w', '-m', 'fast', 'stop'],
                                     capture_output=True).returncode == 0
        if stopped:
            shutil.rmtree(work)
        else:
            print(f'Test server did not stop. Its files were preserved at {work}.', file=sys.stderr)


if __name__ == '__main__':
    raise SystemExit(main())
