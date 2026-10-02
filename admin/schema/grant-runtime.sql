-- Run as the schema owner after creating the dedicated t2n_app role.
-- The role's password is configured through the provider/secret manager, never this file.
GRANT USAGE ON SCHEMA talk2nature TO t2n_app;
REVOKE CREATE ON SCHEMA talk2nature FROM t2n_app;
GRANT SELECT ON talk2nature.schema_version TO t2n_app;
GRANT SELECT,INSERT,UPDATE,DELETE ON
  talk2nature.owner, talk2nature.challenges, talk2nature.sessions,
  talk2nature.observations, talk2nature.releases, talk2nature.audit,
  talk2nature.evidence_versions, talk2nature.evidence_catalog,
  talk2nature.studies, talk2nature.study_evidence,
  talk2nature.study_sessions, talk2nature.observation_links,
  talk2nature.research_media, talk2nature.media_sync, talk2nature.model_runs,
  talk2nature.model_inputs, talk2nature.model_results TO t2n_app;
GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA talk2nature TO t2n_app;
