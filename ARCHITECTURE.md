# Architecture

## Request Lifecycle

FastAPI accepts an ASGI request, middleware attaches a correlation ID, metrics capture timing, access logs emit structured JSON, dependencies open an async SQLAlchemy session, route handlers validate Pydantic schemas, services run business rules, repositories execute DB queries, and errors are mapped into stable API responses.

## Why The Layers Exist

Routes exist to translate HTTP into application calls. Services exist to keep business rules, permissions, transactions, and event publishing out of transport code. Repositories exist so SQLAlchemy query details do not leak into the domain workflow. Schemas exist to keep public API contracts explicit and typed.

Before this separation, route handlers often mixed validation, SQL, permissions, and serialization. That is fast for demos, but hard to test, scale, observe, and refactor.

## Failure Scenarios

Database failures are surfaced through centralized error handling and health checks. Redis failures degrade realtime delivery while the primary task write path can still commit. Third-party failures are bounded with timeouts and retries. Auth failures return stable 401/403 responses. Validation failures are handled by FastAPI/Pydantic before business logic runs.

## Scalability Concerns

Async I/O lets one process handle many concurrent waiting requests, but CPU-heavy work should move to workers. Redis pub/sub enables multiple API replicas to receive task events. WebSockets require connection fanout planning and load balancer support. SSE is cheaper for one-way streams and works well through many proxies, but it is not bidirectional.

## Security Concerns

Passwords are bcrypt-hashed, access routes use OAuth2 bearer JWTs, roles enforce admin/worker permissions, and request schemas reject malformed input. Production should add secret rotation, refresh-token revocation, HTTPS-only cookies or secure storage, rate limiting, tenant isolation, audit retention, and least-privilege DB users.

## Async Considerations

All DB access uses async SQLAlchemy sessions. Transactions are committed in services after business rules pass. Integration calls use `httpx.AsyncClient`; retries are kept outside database transactions to avoid duplicating writes. Blocking SDKs should be wrapped in workers or replaced with async clients.

## Observability Implications

Every request gets a request ID. Logs are structured so they can be indexed by request, endpoint, user, latency, and status. Metrics expose request count and latency for Prometheus. The tracing module is intentionally a small boundary so OpenTelemetry can be added without rewriting services.

## Tradeoffs

This scaffold is more verbose than a CRUD tutorial, but the cost buys testability, replaceable infrastructure, safer permissions, and clearer production operations. Redis pub/sub is simple and useful early; later systems may need Kafka, NATS, or durable outbox processing for stronger delivery guarantees.

