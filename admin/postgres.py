"""Private PostgreSQL adapter. Runtime performs no schema creation or migration."""
from contextlib import contextmanager
from urllib.parse import urlsplit, parse_qs

from admin.store import StorageUnavailable

LOCK_ID = 816421901
SCHEMA_VERSION = 2


def validate_database_url(value, hosted=False):
    try:
        parsed = urlsplit(value)
        options = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
        valid = (parsed.scheme in {'postgres', 'postgresql'} and parsed.hostname
                 and parsed.path not in {'', '/'} and not parsed.fragment
                 and set(options) <= {'sslmode', 'sslrootcert'}
                 and all(len(values) == 1 for values in options.values()))
        _ = parsed.port
        local = parsed.hostname in {'localhost', '127.0.0.1', '::1'}
        mode = options.get('sslmode', [''])[0]
        if not valid or (mode != 'verify-full' and (hosted or not local)):
            raise ValueError
        if hosted and local:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError('Use a PostgreSQL URL with sslmode=verify-full; only local rehearsal may omit verified TLS. Connection overrides are not allowed.') from None


class Record(dict):
    def __init__(self, names, values):
        super().__init__(zip(names, values))
        self.values_tuple = tuple(values)

    def __getitem__(self, key):
        return self.values_tuple[key] if isinstance(key, int) else super().__getitem__(key)


def record_factory(cursor):
    names = [column.name for column in cursor.description] if cursor.description else []
    return lambda values: Record(names, values)


def parameters(query):
    """Translate fixed application qmark SQL, preserving quoted text/identifiers.

    Values are always sent separately to psycopg; no user input becomes SQL.
    Comments/dollar-quoted SQL aren't supported by this small common dialect.
    """
    if '--' in query or '/*' in query or '$' in query:
        raise ValueError('Unsupported SQL syntax in the common storage interface.')
    result, quote, index = [], None, 0
    while index < len(query):
        char = query[index]
        if quote:
            result.append('%%' if char == '%' else char)
            if char == quote:
                if index + 1 < len(query) and query[index + 1] == quote:
                    result.append(quote)
                    index += 1
                else:
                    quote = None
        elif char in {'"', "'"}:
            quote = char
            result.append(char)
        else:
            result.append('%s' if char == '?' else '%%' if char == '%' else char)
        index += 1
    if quote:
        raise ValueError('Unterminated SQL literal.')
    return ''.join(result)


class Connection:
    def __init__(self, raw):
        self.raw = raw

    def execute(self, query, values=()):
        return self.raw.execute(parameters(query), values)

    def executemany(self, query, rows):
        cursor = self.raw.cursor()
        cursor.executemany(parameters(query), rows)
        return cursor


class PostgresStore:
    def __init__(self, database_url, hosted=False):
        validate_database_url(database_url, hosted=hosted)
        self._database_url = database_url
        with self.connect() as db:
            version = db.execute('SELECT version FROM schema_version WHERE singleton=1').fetchone()
            if not version or version[0] != SCHEMA_VERSION:
                raise StorageUnavailable('Database schema is not initialized at the supported version.')

    @contextmanager
    def connect(self):
        import psycopg
        try:
            with psycopg.connect(self._database_url, row_factory=record_factory,
                                 connect_timeout=10, prepare_threshold=None) as raw:
                raw.execute("SET LOCAL statement_timeout='10s'")
                raw.execute("SET LOCAL lock_timeout='5s'")
                raw.execute("SET LOCAL search_path=talk2nature,pg_catalog")
                # Same serialized transition semantics as the local SQLite adapter.
                # Transaction-scoped, so it also works with a transaction pooler.
                raw.execute('SELECT pg_advisory_xact_lock(%s)', (LOCK_ID,))
                yield Connection(raw)
        except psycopg.Error:
            raise StorageUnavailable('Private database unavailable or not initialized. Consult the deployment checklist.') from None
