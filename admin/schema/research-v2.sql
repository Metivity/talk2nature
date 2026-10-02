-- Portable SQLite/PostgreSQL research lineage extension. Metadata only.
CREATE TABLE research_media (
 id TEXT PRIMARY KEY, observation_id TEXT NOT NULL REFERENCES observations(id),
 study_session_id TEXT NOT NULL REFERENCES study_sessions(id),
 modality TEXT NOT NULL CHECK(modality IN ('audio','video')),
 payload TEXT NOT NULL, fingerprint TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('active','withdrawn')), created BIGINT NOT NULL,
 UNIQUE(id,fingerprint)
);
CREATE INDEX media_observation ON research_media(observation_id);
CREATE TABLE media_sync (
 id TEXT PRIMARY KEY, audio_id TEXT NOT NULL REFERENCES research_media(id),
 video_id TEXT NOT NULL REFERENCES research_media(id), payload TEXT NOT NULL,
 fingerprint TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('active','withdrawn')),
 created BIGINT NOT NULL, CHECK(audio_id != video_id)
);
CREATE TABLE model_runs (
 id TEXT PRIMARY KEY, release_id TEXT NOT NULL REFERENCES releases(id),
 payload TEXT NOT NULL, fingerprint TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('registered','invalidated')), created BIGINT NOT NULL
);
CREATE TABLE model_inputs (
 run_id TEXT NOT NULL REFERENCES model_runs(id), media_id TEXT NOT NULL REFERENCES research_media(id),
 media_fingerprint TEXT NOT NULL, PRIMARY KEY(run_id,media_id),
 FOREIGN KEY(media_id,media_fingerprint) REFERENCES research_media(id,fingerprint)
);
CREATE TABLE model_results (
 id TEXT PRIMARY KEY, run_id TEXT NOT NULL, media_id TEXT NOT NULL,
 payload TEXT NOT NULL, fingerprint TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('active','withdrawn')), created BIGINT NOT NULL,
 FOREIGN KEY(run_id,media_id) REFERENCES model_inputs(run_id,media_id)
);
