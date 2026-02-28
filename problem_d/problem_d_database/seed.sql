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

INSERT INTO audit_log (id, event, created_at) VALUES
  ('audit_001', 'System initialized', '2026-02-01T08:00:00.000Z');
