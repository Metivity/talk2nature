from dataclasses import replace
import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from admin.app import create_app
from admin.auth import Settings
from admin.postgres import parameters, validate_database_url
from admin.store import StorageUnavailable


class HostingTests(unittest.TestCase):
    def test_hosted_startup_requires_durable_storage_and_verified_identity_configuration(self):
        complete = Settings(origin='https://private.example', client_id='test.apps.googleusercontent.com',
                            owner_sub='synthetic-pinned-owner', hosted=True,
                            database_url='postgresql://user:password@db.example/study?sslmode=verify-full')
        self.assertNotIn('password', repr(complete))
        for changes in ({'database_url':''}, {'client_id':''}, {'owner_sub':''}, {'origin':'http://localhost:4180'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace(complete, **changes)
        with patch.dict(os.environ, {'K_SERVICE':'talk2nature-admin','T2N_HOSTED':'0'}, clear=True):
            with self.assertRaises(ValueError):
                Settings.from_env()

    def test_remote_database_requires_verified_tls_and_no_destination_override(self):
        for value in ('postgresql://db.example/study',
                      'postgresql://db.example/study?sslmode=require',
                      'postgresql://localhost/study?host=remote.example',
                      'postgresql://db.example/study?sslmode=verify-full&sslmode=disable',
                      'postgresql://db.example/study?sslmode=verify-full&hostaddr=127.0.0.1',
                      'postgresql://db.example/study?sslmode=verify-full#fragment'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_database_url(value)
        validate_database_url('postgresql://localhost/t2n_test_demo?sslmode=disable')
        with self.assertRaises(ValueError):
            validate_database_url('postgresql://localhost/t2n_test_demo?sslmode=disable', hosted=True)

    def test_storage_outage_returns_a_redacted_503(self):
        with tempfile.TemporaryDirectory() as directory:
            app = create_app(Settings(database=Path(directory)/'local.sqlite3'))
            with TestClient(app,base_url='http://localhost:4180') as client:
                self.assertEqual(client.get('/ready').status_code,200)
                with patch.object(app.state.store, 'connect', side_effect=StorageUnavailable('secret-connection-details')):
                    response = client.get('/ready')
                    self.assertEqual(response.status_code,503)
                    self.assertNotIn('secret',response.text)
                    self.assertEqual(response.headers['cache-control'],'no-store')

    def test_common_parameters_keep_literal_question_marks_and_percentages(self):
        self.assertEqual(parameters("SELECT 'is it?', '100%', 'it''s?' WHERE key=?"),
                         "SELECT 'is it?', '100%%', 'it''s?' WHERE key=%s")
        self.assertEqual(parameters('SELECT "question?" FROM things WHERE id=?'),
                         'SELECT "question?" FROM things WHERE id=%s')
        for query in ("SELECT '?' -- comment", 'SELECT $$unsafe$$', "SELECT 'broken"):
            with self.assertRaises(ValueError): parameters(query)
