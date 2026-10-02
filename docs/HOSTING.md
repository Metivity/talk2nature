# Private hosting release plan

October 1, 2026. Talk2Nature only; Metivity/talk2nature; raviv@metivity.com. Raviv approved this proposal and a total budget of up to US$50/month on October 1. Provisioning is in progress; this is not yet a hosted service. The public website and demo remain on GitHub Pages.

## Proposed first deployment

| Component | Proposed setting |
| --- | --- |
| API and private interface | One Cloud Run service, proposed name `talk2nature-admin`, inside the existing `talk2nature` Google project |
| Region | Frankfurt: Google `europe-west3` and a dedicated Supabase project in AWS `eu-central-1`; not provisioned |
| Capacity | Request billing; 1 CPU, 512 MiB; minimum zero and maximum one instance; concurrency eight; 30-second request timeout; no GPU or worker |
| Metadata | Dedicated Supabase Pro Micro PostgreSQL project; private `talk2nature` schema and restricted runtime role |
| Object storage | None for this release. Audio, video and contributor intake stay disabled |
| Identity | Basic Google identity; exact owner email and verified stable subject; no domain-wide authorization |
| Origin | Actual provider HTTPS origin, verified before OAuth registration; no purchased domain |
| Secrets | Database URL and pinned subject held privately; per-secret access for a dedicated service account; no broad Editor grant |
| Initial data | Reimport the current 131 public catalog records; synthetic metadata only. Do not upload the local SQLite database, old sessions or external samples |

The proposed locations are listed by [Google](https://docs.cloud.google.com/run/docs/locations) and [Supabase](https://supabase.com/docs/guides/platform/regions). Raviv’s confirmation covers these proposed locations; region selection is not a compliance determination.

Approved planning budget: **up to US$50/month** for this dedicated prototype. Supabase Pro starts at US$25/month including the first Micro project; Cloud Run, builds, registry, secrets, traffic and tax are additional. This is an estimate, not a purchased plan or guaranteed bill. Supabase Free can support synthetic evaluation but pauses after inactivity and excludes automatic backups. [Supabase pricing](https://supabase.com/pricing), [Cloud Run pricing](https://cloud.google.com/run/pricing).

Budget alerts are not a hard spending cap. Configure alerts, small resource limits, no optional paid add-ons and a reviewed shutdown response before rollout. Neither maximum instances nor the Supabase spend cap bounds every invoice component. [Google budgets](https://docs.cloud.google.com/billing/docs/how-to/budgets), [Supabase cost controls](https://supabase.com/docs/guides/platform/cost-control).

## Implemented preparation

- PostgreSQL preserves the existing serialized transactions using a transaction-scoped advisory lock. Values are separately bound; remote connections require verified TLS; connection/query waits are bounded and errors omit credentials. This is intentionally for a small owner prototype.
- The private schema denies PUBLIC privileges. Keep it out of Supabase's exposed API schemas and disable unnecessary data APIs. Browser JavaScript receives no database credentials.
- Runtime checks an existing schema version; it never creates or migrates tables. `admin/schema/grant-runtime.sql` limits the service role to required data operations. Tests verify that it cannot create/drop tables or change schema versions.
- `T2N_DATABASE_URL` selects PostgreSQL. `T2N_HOSTED=1`, or Cloud Run's `K_SERVICE`, requires HTTPS, Google client, pinned owner and remote PostgreSQL. There is no hosted SQLite fallback or demo authentication.
- `admin.serve` honors `PORT`, disables access logs and untrusted proxy headers, limits concurrency, and binds loopback locally. `/ready` checks database access. The privacy page describes the actual selected adapter.
- The Docker recipe uses a non-root user and an allowlisted context excluding private data, `.env`, funding drafts, screenshots and Git. The base image is pinned by registry digest. The image was built and tested on a standard public-repository GitHub runner in [successful run 36786952737](https://github.com/Metivity/talk2nature/actions/runs/36786952737): excluded-file sentinels, non-root execution, rejection of incomplete hosted settings and locked local-mode HTTP behavior all passed. This is not a cloud deployment or a vulnerability-scan result; provider-specific and security review remain release gates.

## Reproduce the checks

```sh
.venv/bin/python -m pip install -r admin/requirements.lock
.venv/bin/python scripts/test_postgres.py
python3 -m unittest discover -s tests -v
python3 web/build.py
python3 scripts/check_site.py
```

The PostgreSQL runner requires existing `initdb` and `pg_ctl`. It creates a password-protected loopback-only disposable cluster and a separate restricted runtime role, runs both adapters' tests, then stops its server and removes generated files. It never uses an existing database or cloud credentials. October 1 latest local check: 76 backend tests passed, including 36 PostgreSQL cases with no skips; 23 website/research tests passed. Local PostgreSQL was 14.18; the managed provider version still needs a deployment test.

## Database initialization after approval

Use a dedicated schema owner for initialization and a separate `t2n_app` login for runtime. Supply URLs through the environment or secret manager, never chat, command arguments, Git or logs. Remote URLs require `sslmode=verify-full` with the provider's verified CA configuration. Prepared statements are disabled for transaction-pooler compatibility. [Supabase connection modes](https://supabase.com/docs/guides/database/connecting-to-postgres).

With the schema-owner URL supplied privately:

```sh
.venv/bin/python -m admin.database init
```

Provision the runtime login, apply `admin/schema/grant-runtime.sql` as the schema owner, then switch to the runtime URL:

```sh
.venv/bin/python -m admin.database check
.venv/bin/python -m admin.database import-catalog
```

No Supabase organization, cloud runtime role, service account, secret, database or Cloud Run service has been provisioned. The Google User Data Policy was accepted after Raviv’s specific confirmation on October 1. OAuth branding and the local web client were created; real owner login, logout and repeat login after restart with the explicit pin succeeded, and the stable subject was saved privately. A different, verified Google account was denied by the owner allowlist. A dedicated Talk2Nature billing account was prepared; provider account setup requires owner action before linking it to the project. Private billing details stay outside Git. Supabase is at its separate Terms/Privacy acceptance step; no account or project has been created.

## Acceptance before calling the private app live

1. Google agreement, local web client, first real owner login/logout and private subject pin are complete. Repeat owner login after restart with the explicit pin and real non-owner denial are verified. Hosted-origin behavior remains outstanding. Test signatures are not a live provider test.
2. Budget and proposed Frankfurt regions are approved. Verify dedicated billing ownership and complete provider agreements and credential handoffs required by the provisioning surface.
3. Build and inspect the container; verify the actual service/OAuth origin; configure restricted credentials, runtime limits and operational alerts. Review provider IAM requirements before exposing the sign-in shell; all private records remain behind app authentication.
4. Test unauthenticated denial, owner login, CSRF, restart persistence, catalog import, release and withdrawal on the actual service using synthetic metadata.
5. Drill managed PostgreSQL recovery and deletion reconciliation. `admin.recovery` tests SQLite only. PostgreSQL restoration must invalidate sessions/challenges and reconcile withdrawals and revoked releases since the snapshot before serving traffic. Provider backups do not implement withdrawal automatically.

Real participants and recordings still need a scientific protocol, consent, contributor authorization, retention/deletion implementation and actual device testing. These are outside the hosted synthetic milestone.


## October 2 schema update

The runtime now requires schema v2. Fresh initialization includes synthetic media descriptors, alignment and model provenance; existing v1 PostgreSQL deployments must use the explicit schema-owner migration and refreshed runtime grants described in [MEDIA_LINEAGE](MEDIA_LINEAGE.md). No object storage or cloud provisioning was added. Hosted acceptance must include lineage persistence and withdrawal invalidation alongside the existing metadata release checks. Provider setup and hosted verification remain outstanding.
