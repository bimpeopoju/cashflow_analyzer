# MarketFlow Authentication Implementation Plan

## Goal

Move authentication out of the prototype `finance` app into the `users` domain
without breaking the existing frontend. Start with email/password and JWT, while
creating a provider-neutral foundation for future OAuth login.

## Decisions

- Keep Django's existing user model during this reconstruction phase.
- Treat the normalized email address as the login identifier and username.
- Use short-lived JWT access tokens and rotating refresh tokens.
- Blacklist refresh tokens after rotation and logout.
- Keep session authentication temporarily for admin and compatibility.
- Make `/api/v1/auth/*` the canonical authentication API.
- Keep `/api/auth/*` as a temporary compatibility alias.
- Store OAuth identities separately from core user records.
- Do not implement provider redirects or callback exchange until provider
  credentials and redirect URLs are agreed.

## Token Policy

| Token | Default lifetime | Purpose |
| --- | --- | --- |
| Access token | 15 minutes | Authenticate API requests |
| Refresh token | 7 days | Obtain a new access/refresh token pair |

Refresh tokens rotate whenever they are used. The previous refresh token is
blacklisted. Logout blacklists the submitted refresh token.

Token lifetimes are configurable through environment variables:

- `JWT_ACCESS_TOKEN_MINUTES`
- `JWT_REFRESH_TOKEN_DAYS`

## Password Flow

### Register

`POST /api/v1/auth/register/`

```json
{
  "fullName": "Amina Musa",
  "email": "amina@example.com",
  "password": "a-strong-password"
}
```

Responsibilities:

1. Normalize and validate the email.
2. Validate the password using Django password validators.
3. Create the user atomically.
4. Create the temporary legacy business profile until the `businesses` domain
   replaces it.
5. Return the user and JWT token pair.

### Login

`POST /api/v1/auth/login/`

```json
{
  "email": "amina@example.com",
  "password": "a-strong-password"
}
```

Responsibilities:

1. Normalize the email.
2. Authenticate the password.
3. Reject inactive users.
4. Return the user and JWT token pair.

### Refresh

`POST /api/v1/auth/refresh/`

```json
{
  "refresh": "<refresh-token>"
}
```

Returns a rotated access/refresh token pair.

### Current User

`GET /api/v1/auth/me/`

Requires a bearer access token or a temporary compatibility session.

### Logout

`POST /api/v1/auth/logout/`

```json
{
  "refresh": "<refresh-token>"
}
```

Blacklists the refresh token. Access tokens remain valid until their short
expiry; clients must remove them immediately.

## OAuth Scaffold

The scaffold records a stable relationship between a MarketFlow user and an
external provider identity.

```text
OAuthIdentity
  user
  provider
  subject
  email
  metadata
  created_at
  updated_at
```

Required uniqueness:

- A provider subject maps to only one MarketFlow user.
- A user may connect only one identity per provider in the initial design.

Initial provider registry:

- `google` - scaffolded, disabled until configured

Provider discovery endpoint:

`GET /api/v1/auth/oauth/providers/`

This endpoint exposes provider availability without starting an OAuth flow.
Future provider implementations must own:

1. Authorization URL generation with state and PKCE.
2. Callback state validation.
3. Authorization-code exchange.
4. ID token or user-info verification.
5. Account linking rules.
6. MarketFlow JWT issuance after successful provider authentication.

## Security Requirements

- Passwords are never logged or returned.
- Django password validators run during registration.
- Authentication failures return a generic credential error.
- OAuth provider subjects, not provider email addresses, are the stable
  identity keys.
- OAuth state and PKCE are mandatory before enabling a provider.
- Refresh tokens are never stored in plaintext by the backend.
- Production deployments require HTTPS and a non-default secret key.
- Rate limiting, email verification, password reset, and account recovery are
  required before production launch.

## Compatibility and Migration

- Existing finance endpoints accept bearer JWTs through authentication
  middleware while their views are reconstructed.
- Existing session-based frontend behavior remains temporarily supported.
- The frontend should persist access and refresh tokens, attach access tokens to
  API requests, rotate tokens after `401`, and clear tokens on logout.
- Authentication routes must be removed from `finance.urls` after compatibility
  tests confirm the users routes preserve the contract.

## Test Matrix

- Registration returns a token pair and creates a usable user.
- Registration rejects duplicate emails.
- Registration applies Django password validation.
- Login returns a token pair for valid credentials.
- Login rejects invalid credentials and inactive users.
- Bearer access token authenticates `/auth/me/` and finance endpoints.
- Refresh rotates tokens and blacklists the previous refresh token.
- Logout blacklists the submitted refresh token.
- Missing or invalid bearer tokens return `401`.
- OAuth provider discovery exposes only configured provider metadata.
- OAuth identity uniqueness constraints prevent conflicting account links.

## Deferred Work

- Email verification
- Forgot-password and password-reset flows
- Login and refresh rate limiting
- Security event/audit log
- Trusted-device and session management
- Multi-factor authentication
- Google OAuth authorization and callback implementation
- Additional OAuth providers

