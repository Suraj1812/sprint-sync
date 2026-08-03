# API Conventions

## Routing

- All API routes live under `/api/v1/`.
- Routers are grouped by domain: `auth`, `users`, `health`.
- OpenAPI documentation is available at `/api/docs`.

## Responses

- Success responses return the requested model.
- Error responses use the standard `APIResponse` envelope:

```json
{
  "success": false,
  "error_code": "authentication_error",
  "message": "Authentication failed."
}
```

## Authentication

- Include the access token in the `Authorization: Bearer <token>` header.
- Cookies are also supported via `access_token`.

## Pagination

List endpoints accept `page` and `page_size` query parameters and return `PaginatedResponse`.

## HTTP Status Codes

- `200` OK
- `201` Created
- `401` Unauthorized
- `403` Forbidden
- `404` Not Found
- `409` Conflict
- `422` Validation Error
- `429` Rate Limit
- `500` Internal Server Error
