-- Problem D demo seed data (SQLite)

INSERT INTO organizations (id, name, region, seats) VALUES
  ('org_001', 'Northwind AI', 'us-east-1', 18),
  ('org_002', 'Kestrel Analytics', 'eu-west-1', 8);

INSERT INTO projects (id, organization_id, name, environment, status, updated_at) VALUES
  ('proj_001', 'org_001', 'Aurora Insights', 'production', 'active', '2026-02-20T18:22:00.000Z'),
  ('proj_002', 'org_001', 'Lumen Sandbox', 'staging', 'paused', '2026-02-12T09:15:00.000Z'),
  ('proj_003', 'org_002', 'Nimbus', 'production', 'active', '2026-02-05T14:02:00.000Z');

INSERT INTO invoices (id, organization_id, amount, status, issued_at) VALUES
  ('inv_202601', 'org_001', 149, 'paid', '2026-02-01'),
  ('inv_202512', 'org_001', 149, 'paid', '2025-12-01');

INSERT INTO usage_summary (id, ingestion_gb, model_calls, team_seats, last_sync) VALUES
  ('usage_001', 182.4, 120340, 18, '2026-02-26T17:04:00.000Z');

INSERT INTO users (id, organization_id, name, email, password, created_at) VALUES
  ('user_001', 'org_001', 'Avery Chen', 'avery@northwind.ai', 'password123', '2026-01-02T08:30:00.000Z'),
  ('user_002', 'org_001', 'Morgan Lee', 'morgan@northwind.ai', 'password123', '2026-01-03T11:10:00.000Z'),
  ('user_003', 'org_001', 'Jordan Patel', 'jordan@northwind.ai', 'password123', '2026-01-08T09:45:00.000Z'),
  ('user_004', 'org_001', 'Riley Kim', 'riley@northwind.ai', 'password123', '2026-01-09T14:05:00.000Z'),
  ('user_005', 'org_002', 'Taylor Brooks', 'taylor@kestrel.ai', 'password123', '2026-01-10T10:25:00.000Z');

INSERT INTO organization_memberships (id, organization_id, user_id, role, created_at) VALUES
  ('orgm_001', 'org_001', 'user_001', 'owner', '2026-01-02T08:35:00.000Z'),
  ('orgm_002', 'org_001', 'user_002', 'admin', '2026-01-03T11:15:00.000Z'),
  ('orgm_003', 'org_001', 'user_003', 'member', '2026-01-08T09:50:00.000Z'),
  ('orgm_004', 'org_001', 'user_004', 'auditor', '2026-01-09T14:10:00.000Z'),
  ('orgm_005', 'org_002', 'user_005', 'owner', '2026-01-10T10:30:00.000Z');

INSERT INTO project_memberships (id, project_id, user_id, created_at) VALUES
  ('prjm_001', 'proj_001', 'user_003', '2026-01-08T10:00:00.000Z'),
  ('prjm_002', 'proj_002', 'user_003', '2026-01-08T10:05:00.000Z'),
  ('prjm_003', 'proj_001', 'user_002', '2026-01-03T11:20:00.000Z');

INSERT INTO role_audit_permissions (role, scope, can_view_sensitive) VALUES
  ('owner', 'organization', 1),
  ('admin', 'organization', 1),
  ('auditor', 'organization', 0),
  ('member', 'project_assigned', 0),
  ('viewer', 'self', 0);

INSERT INTO audit_logs (id, organization_id, project_id, actor_user_id, event_type, severity, metadata, is_sensitive, occurred_at) VALUES
  ('audit_001', 'org_001', 'proj_001', 'user_001', 'project.created', 'info', '{"projectId":"proj_001"}', 0, '2026-02-18T09:00:00.000Z'),
  ('audit_002', 'org_001', 'proj_001', 'user_002', 'apikey.rotated', 'warning', '{"keyId":"key_live_01"}', 1, '2026-02-19T10:15:00.000Z'),
  ('audit_003', 'org_001', 'proj_002', 'user_003', 'dataset.exported', 'critical', '{"datasetId":"ds_992"}', 1, '2026-02-20T13:40:00.000Z'),
  ('audit_004', 'org_001', 'proj_002', 'user_003', 'run.triggered', 'info', '{"workflow":"nightly-sync"}', 0, '2026-02-21T06:25:00.000Z'),
  ('audit_005', 'org_002', 'proj_003', 'user_005', 'project.updated', 'info', '{"field":"status"}', 0, '2026-02-21T12:12:00.000Z');
