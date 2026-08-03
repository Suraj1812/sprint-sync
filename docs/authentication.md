# Authentication

## Overview

SprintSync uses stateless JWT access tokens and refresh tokens stored in Redis.

- **Access token** — short-lived (15 minutes by default), contains `sub` (user id) and `role`.
- **Refresh token** — long-lived (7 days by default), contains a token family used to detect reuse.

## Flow

### Register

`POST /api/v1/auth/register`

Creates a user, hashes the password with Argon2id, and returns an access/refresh token pair.

### Login

`POST /api/v1/auth/login`

Validates credentials and issues a new token pair.

### Refresh

`POST /api/v1/auth/refresh`

Exchanges a valid refresh token for a new access/refresh pair. The old refresh token is revoked.

### Logout

`POST /api/v1/auth/logout`

Revokes the provided refresh token.

## RBAC

Roles are stored in the `roles` table. Built-in roles are:

- `user`
- `manager`
- `admin`

Permissions are stored as a JSON list and can be extended without schema changes.
