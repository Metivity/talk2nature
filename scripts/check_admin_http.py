"""Bounded smoke test of the locked local container; no real identity or data."""
import json
import time
import urllib.error
import urllib.request


def main():
    base = 'http://localhost:4180'
    deadline = time.monotonic() + 20
    while True:
        try:
            with urllib.request.urlopen(base+'/ready', timeout=2) as response:
                assert response.status == 200
                assert json.load(response)['mode'] == 'synthetic-metadata-only'
                break
        except (urllib.error.URLError, TimeoutError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(.25)
    with urllib.request.urlopen(base+'/auth/config', timeout=2) as response:
        assert json.load(response) == {'ready': False}
    with urllib.request.urlopen(base+'/privacy', timeout=2) as response:
        assert 'local SQLite' in response.read().decode()
        assert response.headers['Cache-Control'] == 'no-store'
    try:
        urllib.request.urlopen(base+'/api/observations', timeout=2)
        raise AssertionError('Unauthenticated private access was allowed.')
    except urllib.error.HTTPError as error:
        assert error.code == 401
    print('Service ready; sign-in unconfigured; private access denied; privacy response checked.')


if __name__ == '__main__':
    main()
