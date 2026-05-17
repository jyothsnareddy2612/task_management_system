# Network Fundamentals

## TCP vs UDP

TCP is connection-oriented and reliable. HTTP, WebSocket, PostgreSQL, Redis, and MongoDB usually ride on TCP because APIs need ordered delivery and retransmission.

UDP is connectionless and faster for lossy workloads. It is common in DNS lookups, video, voice, and gaming where late packets may be less useful than fresh packets.

## DNS Basics

DNS translates names like `oauth2.googleapis.com` or an Aiven host into IP addresses. In this project, DNS is involved when the backend talks to Google OAuth, Aiven PostgreSQL, Redis, MongoDB, or any external HTTP integration.

## HTTP Request/Response Cycle

1. Client resolves DNS.
2. Client opens a TCP connection.
3. TLS is negotiated for HTTPS.
4. Client sends method, path, headers, and optional JSON body.
5. FastAPI middleware runs.
6. Dependencies resolve auth and database sessions.
7. Route calls service and repository layers.
8. Response returns JSON and status code.

## AJAX / Fetch Lifecycle

Browser JavaScript creates a request with `fetch`, serializes JSON, sends it asynchronously, waits for a response, parses JSON, updates UI state, and handles errors.

