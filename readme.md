# Distributed Rate Limiter

Lightweight distributed rate-limiter demo using Redis cluster and a small demo service.

**Contents**
- Overview
- Requirements
- Run (Docker)
- Run (local / without Docker)
- Benchmarking with `ab`
- How Redis `INCR` solves the read-modify-write cycle

## Overview

This project demonstrates a simple distributed rate-limiter pattern using Redis (cluster) and a demo HTTP service. The rate-limiter uses atomic Redis operations so multiple instances can safely coordinate counts.

## Requirements

- Docker & Docker Compose (recommended)
- Python 3.10+ (if running locally)
- `ab` (ApacheBench) for load testing (optional)

## Run (Docker Compose) — recommended

Build and run all services (Redis cluster, apps, load balancer, etc) with the repository's `docker-compose.yml`:

```bash
docker compose up -d --build
```

This command builds images (if needed) and starts all services defined in `docker-compose.yml` including the Redis cluster, two app instances, and the `load-balancer` service which exposes the demo on port `9000` — you do not need to start the load balancer manually.

To view logs:

```bash
docker compose logs -f
```

To stop and remove the containers:

```bash
docker compose down
```

## Benchmarking with ApacheBench (`ab`)

You can test the demo endpoint with `ab` to simulate concurrent requests. Example:

```bash
ab -n 1000 -c 100 http://localhost:9000/demo-service/hello
```

- `-n 1000` means total 1000 requests.
- `-c 100` means 100 concurrent requests at a time.

Typical interpretation:
- `Requests per second` shows achieved throughput.
- `Failed requests` indicates errors under load.

Run this against the service while the rate-limiter is active to observe throttling or counter updates.

## How the Redis read-modify-write (RMW) cycle is solved using `INCR`

Problem: when multiple processes/instances try to update a shared counter, a naive pattern "read -> modify -> write" is vulnerable to race conditions (two clients read the same value, both increment locally, and each writes back the same new value, losing one increment).

Solution: use Redis atomic operations, specifically `INCR` (or `INCRBY`). `INCR` is performed atomically on the Redis server, so concurrent increments are serialized by Redis and no updates are lost.

Pattern used in this project:

1. Use `INCR` to atomically increment the counter:

```py
count = await redis.incr(key)
```

2. If you need the counter to expire after a fixed window (sliding or fixed window rate limiting), set the TTL only when the key is first created — i.e., when `INCR` returns `1`. This avoids accidentally shortening the TTL on every increment.

```py
if count == 1:
	# first increment created the key; set expiry for the rate window
	await redis.expire(key, window_seconds)
```

This pattern ensures:
- Atomic increments (no lost updates).
- TTL is applied once when the window starts, preserving the rate window semantics.

If you need multi-key or more complex semantics (like returning both count and TTL atomically, or resetting and returning count in one operation), consider using a small Lua script (EVAL) to perform multiple operations atomically on the Redis server.

## Notes

- The repository contains a small `rate_limiter_service` module which wraps the Redis client. It uses `incr` and `expire` operations as shown above.
- For real production usage you should secure Redis, tune eviction/replication, and ensure cluster topology matches your needs.

---

If you want, I can also:
- show a minimal Lua script for more advanced atomic operations,
- or add a small example `curl`/`python` script to demonstrate the rate-limiter behavior.

Enjoy — run the `ab` command above to benchmark and observe the rate-limiter behavior.
