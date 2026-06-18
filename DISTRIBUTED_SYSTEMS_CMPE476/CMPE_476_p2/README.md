# CMPE476 Project 2 - Replicated Web Service with Reverse Proxy and Shared State

## Team Members
- Student 1: [Name] - [Student ID]
- Student 2: [Name] - [Student ID]

## Backend Language and Framework
- **Language:** Python 3.11
- **Framework:** Flask + Gunicorn
- **Dependencies:** redis-py (Redis client)
- **Key-Value Store:** Redis (official alpine image)
- **Reverse Proxy:** NGINX (official alpine image)

## System Architecture

```
        [ Client / curl ]
               |
            Port 8080
               |
            +--v--+
            |NGINX|
            +--+--+
               |
         +-----+-----+
         |     |     |
       [app1][app2][app3]
         |     |     |
         +-----+-----+
               |
            [Redis]
```

- **NGINX:** Load balancer and reverse proxy (round-robin distribution)
- **app1, app2, app3:** Three identical replicas with unique SERVER_ID
- **Redis:** Shared state storage for global_count and /store data

## How to Run

### Start the system:
```bash
docker compose up --build -d
```

The system will be ready to serve requests at `http://localhost:8080` within ~60 seconds.

### Stop the system:
```bash
docker compose down
```

### Stop and clean up data (include -v to delete volumes):
```bash
docker compose down -v
```

## Third-party Code

- **NGINX:** Official nginx:alpine image (unmodified)
- **Redis:** Official redis:alpine image (unmodified)
- **Flask framework:** Used as-is per Python standard library license
- All other implementation is original
