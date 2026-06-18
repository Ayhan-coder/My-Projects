# CMPE476 Project 2 - Experiment Guide

This guide provides step-by-step instructions for running the five required experiments.

## Prerequisites
- System must be running: `docker compose up --build -d`
- Wait ~30 seconds for all services to be ready
- Test connectivity: `curl http://localhost:8080/health`

## Experiment 1: Load Distribution

**Goal:** Verify that requests are distributed across all three replicas.

### On Linux/macOS or WSL2:
```bash
for i in $(seq 30); do
  curl -s -D - -o /dev/null http://localhost:8080/ \
    | grep -i x-server-id
done | sort | uniq -c
```

### On Windows PowerShell:
```powershell
$servers = @{}
1..30 | ForEach-Object {
    $response = curl -i http://localhost:8080/ 2>&1 | Select-String "X-Server-Id"
    $response
    if ($response -match "app(\d)") {
        $serverId = "app$($matches[1])"
        if ($servers.ContainsKey($serverId)) {
            $servers[$serverId]++
        } else {
            $servers[$serverId] = 1
        }
    }
}
$servers
```

**Expected Result:**
- At least 2-3 different server_ids appear
- Load is roughly balanced (each server handles ~10 requests)
- Example output:
  ```
  10 X-Server-Id: app1
  10 X-Server-Id: app2
  10 X-Server-Id: app3
  ```

---

## Experiment 2: Local vs Shared State

**Goal:** Demonstrate local_count varies per replica while global_count increases globally.

### Commands:
```bash
# Request 1
curl http://localhost:8080/ | jq

# Request 2 (repeat multiple times)
curl http://localhost:8080/ | jq

# Request 3 (to a different server)
curl http://localhost:8080/ | jq
```

**Expected Behavior:**
- Same server: `local_count` increments sequentially (1, 2, 3, ...)
- Different servers: Each server's `local_count` restarts (1, 1, 1, ...) but `global_count` always increases
- Example:
  ```json
  {"server_id":"app1","local_count":1,"global_count":1}
  {"server_id":"app2","local_count":1,"global_count":2}
  {"server_id":"app3","local_count":1,"global_count":3}
  {"server_id":"app1","local_count":2,"global_count":4}
  ```

**Explanation:**
- `local_count` is stored in RAM of each container—isolated per process
- `global_count` is in Redis—shared across all replicas
- This demonstrates the difference between local and shared state in distributed systems

---

## Experiment 3: Shared Redis Store

**Goal:** Verify that values stored by one replica can be retrieved by any replica.

### Commands:
```bash
# Write from app1 (or whichever gets it)
curl "http://localhost:8080/store?key=course&value=distributed-systems"

# Read multiple times
curl "http://localhost:8080/get?key=course"
curl "http://localhost:8080/get?key=course"
curl "http://localhost:8080/get?key=course"

# Note the server_id field and X-Server-Id header
```

**Expected Result:**
- First `/store` returns:
  ```json
  {"stored":true,"key":"course","value":"distributed-systems","server_id":"appX"}
  ```
- Subsequent `/get` calls return the same value regardless of which server responds:
  ```json
  {"key":"course","value":"distributed-systems","server_id":"app1"}
  {"key":"course","value":"distributed-systems","server_id":"app2"}
  {"key":"course","value":"distributed-systems","server_id":"app3"}
  ```

**Explanation:** The value is stored in Redis (shared), not in the replica's memory. Any replica can read it.

---

## Experiment 4: Backend Failure Tolerance

**Goal:** Verify that the service continues when one replica stops.

### Commands:
```bash
# Send baseline requests (should all succeed)
for i in $(seq 10); do
  curl -s http://localhost:8080/ | jq .server_id
done

# Stop one replica
docker compose stop app2

# Wait 2-3 seconds for NGINX to detect failure
sleep 3

# Send 20 more requests
for i in $(seq 20); do
  curl -s http://localhost:8080/ | jq .server_id
done

# Restart the replica
docker compose start app2

# Verify all three are responding again
for i in $(seq 10); do
  curl -s http://localhost:8080/ | jq .server_id
done
```

**Expected Results:**
- After stopping app2: at least 18 of 20 requests succeed (90% threshold)
- Only `app1` and `app3` appear in responses (app2 missing)
- After restart: all three replicas respond again
- Example during failure:
  ```json
  {"server_id":"app1",...}
  {"server_id":"app1",...}
  {"server_id":"app3",...}  // app2 absent
  {"server_id":"app1",...}
  ```

**Explanation:** NGINX detects when a backend is down and routes traffic to healthy replicas. This is failure tolerance.

---

## Experiment 5: Slow Requests and Concurrent Load

**Goal:** Observe how NGINX distributes slow requests across replicas.

### Commands:
```bash
# Send 6 concurrent requests with 3-second sleep
# (Do this in separate terminal windows or with background jobs)

# Terminal 1
curl http://localhost:8080/slow?seconds=3

# Terminal 2
curl http://localhost:8080/slow?seconds=3

# Terminal 3
curl http://localhost:8080/slow?seconds=3

# Terminal 4
curl http://localhost:8080/slow?seconds=3

# Terminal 5
curl http://localhost:8080/slow?seconds=3

# Terminal 6
curl http://localhost:8080/slow?seconds=3

# Record which server_id responds to each and the slept duration
```

### Or with background jobs (bash):
```bash
for i in $(seq 6); do
  curl -s http://localhost:8080/slow?seconds=3 | jq . &
done
wait
```

**Expected Result:**
- All requests complete successfully
- Responses distributed across replicas (server_id varies)
- All return `"slept": 3`
- Total time should be ~3 seconds (not 18!), showing parallel load balancing
- Example:
  ```json
  {"server_id":"app1","slept":3}
  {"server_id":"app2","slept":3}
  {"server_id":"app3","slept":3}
  {"server_id":"app1","slept":3}
  {"server_id":"app2","slept":3}
  {"server_id":"app3","slept":3}
  ```

**Explanation:** Round-robin load balancing distributes requests across replicas. Multiple slow requests can run in parallel on different replicas.

---

## Capturing Evidence for Report

When running experiments:

1. **Take screenshots** showing:
   - Terminal output of load distribution test
   - curl output with headers (`curl -i`)
   - Server responses showing different server_ids
   - Before/after stopping a replica

2. **Copy terminal output** showing:
   - All three server_ids appearing
   - Load roughly balanced
   - System surviving replica failure

3. **Document observations:**
   - How many requests per server in Exp 1
   - Pattern of local_count vs global_count in Exp 2
   - Confirmation shared storage works in Exp 3
   - Success rate during replica failure in Exp 4
   - Distribution of slow requests in Exp 5

---

## Troubleshooting

### `/health` endpoint returns 504 or connection refused
- Docker containers may not have started yet
- Wait 30-60 seconds after `docker compose up --build -d`
- Check logs: `docker compose logs`

### Requests to one or more servers never appear
- NGINX may not have discovered all backends yet
- Restart nginx: `docker compose restart nginx`
- Check NGINX logs: `docker compose logs nginx`

### X-Server-Id header missing
- Verify with: `curl -i http://localhost:8080/health | grep -i x-server-id`
- Should show: `X-Server-Id: app1` (or app2/app3)

### global_count not incrementing atomically (jumps by 2 or skips)
- Indicates `GET-then-SET` race condition (should use Redis INCR)
- Verify app.py has `r.incr('global_count')` not read-modify-write

---

## Cleanup

When done testing:
```bash
# Stop all containers
docker compose down

# Stop and remove volumes (clears Redis data)
docker compose down -v

# For a clean restart
docker compose up --build -d
```
