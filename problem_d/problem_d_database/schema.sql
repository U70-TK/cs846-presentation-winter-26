-- Problem D demo schema (SQLite)

CREATE TABLE IF NOT EXISTS organizations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  region TEXT NOT NULL,
  seats INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  name TEXT NOT NULL,
  environment TEXT NOT NULL,
  status TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS invoices (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  amount INTEGER NOT NULL,
  status TEXT NOT NULL,
  issued_at TEXT NOT NULL,
  FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS usage_summary (
  id TEXT PRIMARY KEY,
  ingestion_gb REAL NOT NULL,
  model_calls INTEGER NOT NULL,
  team_seats INTEGER NOT NULL,
  last_sync TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS organization_memberships (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'auditor', 'member', 'viewer')),
  created_at TEXT NOT NULL,
  FOREIGN KEY (organization_id) REFERENCES organizations(id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  UNIQUE (organization_id, user_id)
);

CREATE TABLE IF NOT EXISTS project_memberships (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  UNIQUE (project_id, user_id)
);

CREATE TABLE IF NOT EXISTS role_audit_permissions (
  role TEXT PRIMARY KEY CHECK (role IN ('owner', 'admin', 'auditor', 'member', 'viewer')),
  scope TEXT NOT NULL CHECK (scope IN ('organization', 'project_assigned', 'self')),
  can_view_sensitive INTEGER NOT NULL CHECK (can_view_sensitive IN (0, 1))
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id TEXT PRIMARY KEY,
  organization_id TEXT NOT NULL,
  project_id TEXT,
  actor_user_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
  metadata TEXT NOT NULL,
  is_sensitive INTEGER NOT NULL CHECK (is_sensitive IN (0, 1)),
  occurred_at TEXT NOT NULL,
  FOREIGN KEY (organization_id) REFERENCES organizations(id),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (actor_user_id) REFERENCES users(id)
);
