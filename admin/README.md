# Private owner workbench

Local synthetic-metadata prototype, separate from the GitHub Pages website. It exercises Google-token verification, an owner-only server session, review gates and withdrawal. No audio, actual training or contributor access.

## Run locally

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r admin/requirements.lock
python3 -m admin.catalog
.venv/bin/python -m uvicorn admin.app:create_app --factory --host 127.0.0.1 --port 4180 --no-access-log
```

Open `http://localhost:4180` (use exactly localhost, matching the default origin). Without a client ID, the page explains setup is incomplete and private routes remain locked. Environment settings are documented in `admin/.env.example`; that file is not loaded automatically. `T2N_DATABASE` defaults to ignored `data/private/admin.sqlite3`. Do not place the database, copies or local secrets inside `dist/`, `content/` or tracked files. Local filesystem owners can read the unencrypted SQLite file; this is not a multi-user workstation security boundary.

## PostgreSQL and hosting preparation

`T2N_DATABASE_URL` selects the tested PostgreSQL adapter; without it, local development uses SQLite. `T2N_HOSTED=1` or Cloud Run's `K_SERVICE` requires HTTPS, a configured Google client, pinned owner subject and PostgreSQL. See [the concrete deployment proposal and release gates](../docs/HOSTING.md). Cloud hosting and live Google Sign-In are still unverified.

Run `.venv/bin/python scripts/test_postgres.py` to create a disposable local PostgreSQL cluster and exercise the full workbench suite with a restricted runtime role. This requires existing PostgreSQL binaries and does not connect to any existing database. `admin.database init` explicitly initializes the private schema; runtime never runs migrations. The SQLite recovery command below does not back up PostgreSQL.

## Local recovery rehearsal

```sh
python3 -m admin.recovery --name first-rehearsal
```

This reads the current local database, uses SQLite's backup API for a consistent snapshot, removes authentication sessions and login challenges from the copy, and restores into a separate file. The pinned owner identity is preserved. It verifies integrity, foreign keys, table counts and a fingerprint of all restored schema/records. The original database is neither replaced nor activated. An existing output directory is refused.

Outputs are `snapshot.sqlite3`, `restored.sqlite3` and `report.json` inside ignored `data/private/recovery/<name>/`. The directory is owner-only (0700); files are 0600. They remain **unencrypted local copies**, not off-device backups or a hosted recovery service. No automatic schedule or retention policy is enabled. The CLI only publishes its output in this ignored private subtree. Use this with the trusted local prototype database, not arbitrary downloaded SQLite files.

The snapshot excludes live authentication state so restored copies require a fresh login. This does not solve post-snapshot withdrawal: an older copy can contain data withdrawn later. Never switch the app to a restored file without reconciling later withdrawals, deleted records and revoked releases. The current tool deliberately provides no activate/overwrite command. Hosted restoration, encryption, retention, withdrawal reconciliation and operational access remain release gates.

On September 30 the actual 82-record evidence catalog was copied and restored with matching content; the active database was untouched. Isolated tests additionally cover pinned identity, session scrubbing, withdrawn observations and revoked releases, corrupt references, private file modes and overwrite refusal. No real participant data or live Google login was used.

## Connect real Google Sign-In

1. Sign into Google Cloud as `raviv@metivity.com`. Account verification was completed on September 30.
2. Select the dedicated **Talk2Nature** project, ID `talk2nature`, created under the metivity.com organization on September 30. Do not create another project, use an unrelated company project or attach billing just to obtain an identity client.
3. Configure Google Auth Platform branding and a Web application OAuth client. Use only basic sign-in identity; no Drive/Gmail scopes. For local development add the exact authorized JavaScript origin `http://localhost:4180` (and Google-required localhost origin if the console requires it). Set the owner as the test user if using an external testing consent configuration. A hosted client requires its exact future HTTPS origin; do not invent one.
4. Set the public web client ID in `T2N_GOOGLE_CLIENT_ID`; no OAuth client secret is used by this ID-token flow. Run the app with its matching `T2N_ORIGIN`.
5. Complete the Google button flow. The server requires the exact owner email, verified status, correct token audience/issuer/signature/expiry, browser nonce and Workspace domain for initial binding. It stores the stable Google subject privately. Inspect/bind that verified subject through local configuration before a hosted rollout. If Google is not authoritative for the email, explicitly resolve identity; do not remove the check.
6. Verify owner success, another account denied, logout and session expiry. Google client setup and live login have **not** yet been verified.

The app loads Google's hosted Identity Services library according to the [official setup guide](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid). The configured client ID is public; ID tokens and session cookies are private. Authentication does not require public access to any private dataset.

## Verify

```sh
.venv/bin/python -m unittest discover -s admin/tests -v
python3 -m unittest discover -s tests -v
python3 web/build.py
python3 scripts/check_site.py
```

Admin tests generate a temporary RSA signing key and replace Google's certificate retrieval only. They exercise real signature/audience/issuer/expiry verification plus nonce replay, exact owner binding, CSRF, session expiry/logout, private routes, input restrictions, optimistic review versions, training opt-out, atomic release and withdrawal, retained review attestations and release-content integrity. No network provider test is implied.

Only synthetic metadata is admitted; real-data submissions return 409. A private release is a metadata-rehearsal JSON export, not a valid audio manifest or a trained model. It is intentionally distinct from the source-recording manifests in `talk2nature/manifest.py`.

The study planner saves passive protocols, behavior definitions, version-pinned evidence, and open/closed study sessions. New UI observations are linked to those sessions; the server checks species, animal, codebook and session start time. The catalog import is idempotent and preserves cited historical versions. See `docs/FIELD_NOTES.md` for the schema, legacy-record behavior and remaining capture/hosting gates. Withdrawing an observation does not delete the study protocol or session alias; these separate records currently have no deletion UI and must remain synthetic.

See `docs/PHASE_TWO_PLAN.md` and `docs/PRIVATE_ARCHITECTURE.md` for product priorities, scientific limits and unfinished hosted requirements. Do not deploy this SQLite adapter on ephemeral serverless storage. No deployment workflow for the private backend is supplied yet.
