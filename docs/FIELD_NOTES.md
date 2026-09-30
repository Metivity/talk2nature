# Field Notes: next product milestone

September 30, 2026. The [product page](https://metivity.github.io/talk2nature/field-notes/) is public. The operational app is a local, owner-only synthetic rehearsal. No public signup, participant collection or animal translation is available.

## Recommendation

Build a responsive web app first. Its immediate value is a useful observation history and a guided, reviewable study workflow. A participant should be able to choose an invited study, understand its protocol, start a short session, describe observable behavior, review a permitted clip and see feedback on contribution quality. Build native capture only when actual device tests show a need for it. Android listening stations and paired TV displays remain later options in `PHASE_TWO_PLAN.md`.

The first research question remains whether sound adds information about independently observed behavior on held-out animals and sessions. Natural-call interpretation and a voluntarily learned interface are separate studies. The current app supports passive study planning; it has no intervention, playback or fabricated animal-speech feature.

## Implemented database records

| Information | Current storage and behavior |
| --- | --- |
| Research sources, original notes, code/model/dataset records | 82 public catalog records imported into private SQLite. Content fingerprints retain historical versions; repeat imports are idempotent. |
| Study protocol and codebook | A saved synthetic study contains the question, species, observation instructions, stop rule and defined behavior labels. Protocol content is immutable; revisions require a new study. Activation is a separate, version-checked action. |
| Evidence used by a study | References point to exact catalog fingerprints, so later catalog changes or retirement do not silently rewrite the study's evidence. |
| Observation sessions | Linked to an active study and an invented animal alias. Open/closed state and optimistic versions are persisted. These are separate from authentication sessions. |
| Observations | Linked to an open study session, matching species/animal/session and the study codebook. Unknown context remains possible but cannot pass acceptance. Timestamps must not precede session start. |
| Permissions, reviews, releases and withdrawal | Existing separate permissions and review gates remain. Exports carry study/protocol/evidence references. Withdrawal removes observation payload and its session link, revoking dependent releases. |
| Future recordings | Not implemented. Private object storage should hold audio/video bytes; the database should track object keys, hashes, duration, device, rights, consent, access and deletion status. |

The public catalog's editable source remains versioned JSON in Git; the database holds imported snapshots for private research use. Private studies, sessions and observations are database-owned and are never exported by the static website builder. This is not yet a single production content-management system. The 808-row external annotation sample remains quarantined in ignored local files; importing its dataset description does not admit those rows to the participant database.

The older standalone observation API remains compatible with earlier synthetic records. New UI submissions require a study session. Standalone records are visibly labeled; they do not receive a study-protocol claim. A metadata release can contain different study references and is not a scientifically approved combined dataset.

## Reproduce the private workflow

```sh
python3 -m admin.catalog
.venv/bin/python -m uvicorn admin.app:create_app --factory --host 127.0.0.1 --port 4180 --no-access-log
.venv/bin/python -m unittest discover -s admin/tests -v
```

The catalog command reads only the reviewed public JSON files, not external sample files, credentials or private funding material. Its default destination is ignored `data/private/admin.sqlite3`. Reimporting the same catalog reports zero creations, changes and retirements. Removed records are retired, while cited versions remain readable behind owner authentication.

Google setup is still unfinished. The browser rehearsal used a temporary isolated database and an injected synthetic test session; it is not a verified Google login. That session was revoked and its cookie removed after verification. There is no production demo-auth option.

## Public interactive demo

The public `/field-notes/demo/` walkthrough uses two invented scene descriptions. Visitors label visible behavior, separately choose private review and training permission, practice four review checks, create a simulated release and withdraw it. Unknown or unsupported labels cannot pass acceptance; training opt-out blocks release; withdrawal clears the observation and revokes a dependent release.

The demo is a static browser simulation, separate from the private API and database. It has no upload, microphone access, sign-in, persistent browser storage, network submission or model prediction. Reload resets its choices. The observer/reviewer role switch teaches the workflow and is not an authorization mechanism. Its rules are tested with `node --test tests/demo.test.mjs`, which also runs before Pages deployment. This does not change the private server's synthetic-only gate or verify Google Sign-In.

## Next release gates

1. **Make the private app usable by its owner:** finish the pending Google agreement/client setup, verify real sign-in and wrong-account rejection, choose a durable private host/region and an explicit spending limit, and test hosted recovery and deletion. The local `admin.recovery` rehearsal now verifies a separate restored copy and removes live auth state; it does not cover encrypted/off-device backups or reconciliation of withdrawals after the snapshot. Do not deploy SQLite on ephemeral compute storage.
2. **Define one feasible study:** audit the parrot dataset's label independence and audio linkage; agree on a species, codebook, review process and scientific collaborator. Determine whether the first pilot uses existing licensed data or invited new observations.
3. **Add invited contribution and short foreground capture:** participant authorization, separately versioned consent, local preview/discard, upload quotas, human-speech/privacy review, private media storage and withdrawal. Test actual iOS/Android devices, interruptions and denied permissions before deployment.
4. **Evaluate a frozen release:** grouped splits, simple baselines, calibrated uncertainty and confound checks. Only then consider a user-facing suggestion about a bounded observed context. Controlled animal-facing experiments require their own protocol and welfare review.

Free preparation can continue locally. No paid resource, Google agreement acceptance, new account access, recording intake or external AI transfer is implied by this milestone.
