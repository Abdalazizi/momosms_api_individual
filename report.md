# API Security & DSA Report (MoMo SMS Transactions)

## Introduction to API security
This sample project demonstrates a simple API protected by Basic Authentication. Basic Auth is simple but weak: credentials (username:password) are only base64-encoded, not encrypted, and are sent with every request. Without HTTPS, they are exposed.

**Stronger alternatives**:
- JWT (JSON Web Tokens): stateless, carries claims, but requires secure storage and expiration handling.
- OAuth2: industry standard for delegated authorization, supports access/refresh tokens and scopes.
- Mutual TLS / API keys combined with TLS.

## DSA Results (see dsa/dsa_compare.py for code)
