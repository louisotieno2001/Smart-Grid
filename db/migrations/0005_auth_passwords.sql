CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS password_hash TEXT;

INSERT INTO organizations (name, legal_name, industry, timezone)
SELECT 'Demo Organization', 'Demo Organization Ltd', 'Energy', 'UTC'
WHERE NOT EXISTS (
  SELECT 1 FROM organizations WHERE name = 'Demo Organization'
);

INSERT INTO users (email, full_name, status)
SELECT 'admin@ems.local', 'EMS Admin', 'active'
WHERE NOT EXISTS (
  SELECT 1 FROM users WHERE email = 'admin@ems.local'
);

UPDATE users
SET password_hash = crypt('admin123!', gen_salt('bf'))
WHERE email = 'admin@ems.local'
  AND (password_hash IS NULL OR password_hash = '');

INSERT INTO user_memberships (user_id, organization_id, role)
SELECT u.id, o.id, 'admin'
FROM users u
CROSS JOIN organizations o
WHERE u.email = 'admin@ems.local'
  AND o.name = 'Demo Organization'
  AND NOT EXISTS (
    SELECT 1
    FROM user_memberships m
    WHERE m.user_id = u.id
      AND m.organization_id = o.id
      AND m.role = 'admin'
  );
