# Authentication

## Endpoints
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/dev-token` (development mode only)

## Login contract
Request:
```json
{
  "email": "admin@ems.local",
  "password": "admin123!"
}
```

Response:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

## JWT claims
Access tokens include:
- `sub` (user id)
- `email`
- `role`
- `roles`
- `organization_id`
- `iat`
- `exp`

## Local development seed
Migration `db/migrations/0005_auth_passwords.sql` seeds:
- User: `admin@ems.local`
- Password: `admin123!`
- Role: `client_admin`

## Notes
- UI stores the bearer token in local storage key `ems_access_token`.
- Invalid/expired tokens trigger a `401` and route users back to `/login`.
- `POST /api/v1/auth/logout` currently performs stateless client logout.
