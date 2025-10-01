# MoMo SMS Transactions API Documentation

## Authentication
This API uses HTTP Basic Authentication for simplicity (not recommended for production).
Use the `Authorization` header: `Authorization: Basic <base64(username:password)>`.
Example user: `admin:password123`

## Endpoints

### GET /transactions
List all transactions.
**Request:** GET /transactions with Basic Auth.
**Response:** 200 OK
```json
[ {'id':1, 'type':'PAYMENT', 'amount':1000, ...}, ... ]
```

### GET /transactions/{id}
Get a single transaction by id.
**Response:** 200 OK or 404 Not Found

### POST /transactions
Add a new transaction. Body JSON (without id).
**Response:** 201 Created (returns created object with assigned id)

Example request body:
```json
{ "type":"PAYMENT", "amount":5000, "sender":"+2507xxxxxxx", "receiver":"+2507yyyyyyy", "timestamp":"2025-09-01T10:00:00", "note":"..." }
```

### PUT /transactions/{id}
Replace an existing transaction. Full object in body including fields (id will be overwritten).
**Response:** 200 OK or 404 Not Found

### DELETE /transactions/{id}
Delete a transaction by id.
**Response:** 200 OK with deleted object or 404 Not Found

## Error Codes
- 400 Bad Request: invalid JSON or malformed request
- 401 Unauthorized: missing or invalid Basic Auth credentials
- 404 Not Found: resource not found

## Security Note
Basic Auth sends base64-encoded credentials; it's not encrypted. Always use HTTPS and consider JWT or OAuth2 for stronger auth and better token management.
