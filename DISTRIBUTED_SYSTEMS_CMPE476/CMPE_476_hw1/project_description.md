# CMPE476 — C10K Project

**The C10K Problem in Practice: Building and Benchmarking a Concurrent TCP Server in C**

| Field          | Value                                      |
|----------------|--------------------------------------------|
| Language       | C (ISO C11, POSIX.1-2008 / Linux)          |
| Platform       | Linux (any modern distribution with epoll(7)) |
| Group size     | 2 students per group (individual submissions also allowed) |
| **You must implement the code yourself, not using LLM.** | |
| Deadline       | May 8, 2026 @ 23:59                        |

## 1. Overview

In Chapter 2 of the course we discussed the C10K problem: the challenge of designing a single server that can sustain ten thousand (and eventually millions of) simultaneous client connections. We contrasted the simple thread-per-connection model — which does not scale past a few thousand clients because every thread consumes roughly a megabyte of stack and forces the kernel to context-switch among thousands of runnable threads — with the event-loop model used by production systems such as Nginx, Redis, HAProxy, and Node.js, which multiplexes many connections on a single thread using non-blocking I/O and a readiness notification mechanism (epoll on Linux, kqueue on BSD, IOCP on Windows).

In this project you will build both architectures yourselves, from the ground up, in C. You will then run them side by side under load and write a short report comparing their memory footprint, throughput, and latency. The goal is not merely to produce working code: it is to turn the abstract numbers we drew on the slides (1 MB per thread, thousands vs. millions of connections) into measurements you have produced on your own laptop, so the trade-offs become something you have felt rather than something you have read.

## 2. Learning Objectives

After completing this project you should be able to:

- write a correct, POSIX-compliant TCP server in C using the socket, bind, listen, accept system calls;
- implement, and reason about the synchronisation requirements of, a thread-per-connection server using pthreads;
- implement a single-threaded event-loop server using epoll(7) and non-blocking I/O, including correct handling of partial reads and EAGAIN;
- design a line-based wire protocol with well-defined error semantics (unknown command, over-length line, graceful close);
- measure the memory and throughput of a concurrent server under controlled load and interpret the results in terms of the architectural trade-offs covered in lecture.

## 3. Background

You do not need to invent the wire protocol or the test harness — both are supplied. Your work is concentrated on the two server architectures and on the benchmark report. The five pure functions that sit beneath both servers (request parsing, response formatting, non-blocking I/O, and a line-oriented receive buffer) are defined by a header file you must not modify, so that, as the instructor, my test harness can link directly against your object files and score you deterministically.

> **Note**: Think of the project as three loosely coupled deliverables: (A) a thread-per-connection server, (B) an epoll-based event-loop server, and (C) a short benchmark report. The shared protocol layer is graded by automated unit tests; the two servers are graded by functional tests that connect real clients to the server and check responses; the report is graded by reading.

## 4. Deliverables

You must submit the following, packaged as described in Section 11:

### Part A — threadserv (30 points)

A thread-per-connection TCP server. A new POSIX thread (`pthread_create`) is spawned for each accepted client. Each worker thread reads lines from its socket, processes them through the shared protocol functions, writes the response back, and terminates when the client closes the connection or sends QUIT. The main thread loops on `accept()`. Global state (connection counts) must be protected by a mutex.

### Part B — epollserv (40 points)

A single-threaded event-loop TCP server using epoll(7) in edge-triggered mode. All sockets (including the listening socket) must be non-blocking. The server must correctly drain each ready socket until `read()` returns `EAGAIN`, accumulate partial lines in a per-connection buffer, and process each complete line through the shared protocol functions. **No pthreads, no fork, no busy-waiting.**

### Part C — Benchmark report (20 points)

A 2–3 page PDF report (`report.pdf`) in which you run both servers against a concurrent client generator, measure memory usage and throughput at 1,000, 5,000, and 10,000 simultaneous connections, present the results in a table and a chart, and interpret them in light of the C10K discussion from Chapter 2. A reference client generator (`client_flood.c`) is supplied; you may use it or write your own.

### Automated unit tests (10 points)

The five API functions defined in `server_api.h` (see Section 6) are exercised by a CUnit test harness you are provided. Passing this harness is worth 10 points directly and is also a precondition for full credit on Parts A and B, since both servers call these functions.

## 5. Wire Protocol

Both servers speak the same text-based protocol. One request per line, one response per line, all lines terminated by `'\n'`. The server tolerates an optional `'\r'` before the `'\n'` (so telnet and netcat both work). The command word is case-sensitive and uppercase; there is no leading whitespace before the command.

| Request              | Response              | Meaning |
|----------------------|-----------------------|---------|
| `PING`               | `PONG`                | Liveness check. |
| `ECHO <text>`        | `<text>`              | Echo everything after the single separating space. |
| `ECHO`               | (empty line)          | ECHO with no payload returns an empty response line. |
| `TIME`               | `<unix_seconds>`      | Current wall-clock time in seconds since the UNIX epoch. |
| `STATS`              | `<active_connections>`| Current number of established client connections. |
| `QUIT`               | `BYE`                 | Server sends BYE then closes the socket. |
| anything else        | `ERR unknown_command` | Unknown command; connection stays open. |
| line > 1024 bytes (no `'\n'`) | `ERR line_too_long` | Server emits the error line, then closes the socket. |

**Note**: The maximum accepted line length (excluding the terminating newline) is 1024 bytes. Responses are at most 1088 bytes. These constants are defined as `MAX_LINE_LEN` and `MAX_RESPONSE_LEN` in `server_api.h` — use them, do not hard-code the numbers.

## 6. API You Must Implement (`server_api.h`)

**DO NOT MODIFY THIS FILE.**

### Protocol Functions (shared)

- `int parse_request(const char *line, request_t *out);`
- `int format_response(const request_t *req, const server_state_t *st, char *out, size_t outlen);`

### Socket Helper

- `int set_nonblocking(int fd);`

### Buffer Helpers (for epoll server)

- `void buffer_init(conn_buf_t *b);`
- `int buffer_append(conn_buf_t *b, const char *data, size_t n);`
- `int buffer_take_line(conn_buf_t *b, char *out, size_t outmax);`

Full details and exact semantics are in `server_api.h` (provided).

## 7. threadserv.c — Part A Requirements

- Ignore `SIGPIPE`.
- Create listening socket, `SO_REUSEADDR`, bind to `INADDR_ANY:port`, listen.
- Loop: `accept()` → `pthread_create(worker)` → `pthread_detach`.
- Worker: read lines (handle `\r\n`), `parse_request`, `format_response`, write response + `\n`.
- Update `active_connections` under mutex on connect/disconnect.
- Close on QUIT, EOF, or `line_too_long`.
- Default port 9090.

## 8. epollserv.c — Part B Requirements

- Ignore `SIGPIPE`.
- Listening socket + all client sockets = non-blocking.
- `epoll_create1(0)`, register listener with `EPOLLIN | EPOLLET`.
- Event loop:
  - On listener readable: `accept()` until `EAGAIN`, set non-blocking, register with `EPOLLIN | EPOLLET`, attach per-connection `conn_buf_t`.
  - On client readable: drain `recv()` until `EAGAIN`, `buffer_append`, then `buffer_take_line` in loop → parse/format/send.
- Close on QUIT / peer close / `line_too_long`.
- Default port 9091.
- **Single thread only.**

## 9. Building & Testing

```bash
make              # builds threadserv + epollserv
make test         # runs CUnit tests (needs libcunit)
./threadserv 9090
./epollserv 9091
./client_flood 127.0.0.1 9090 5000 20
```

## 10. Submission (Section 11 — summarized)

Package everything into a single archive (e.g. `cmpe476-c10k-<yourname>.tar.gz`) containing:
- All `.c` and `.h` source files
- `Makefile`
- `report.pdf` (2–3 pages)
- (Optional) `README.md` with any extra notes

**You must implement the code yourself — no LLM-generated submissions.**

---

*This Markdown version was generated from the official project PDF for easier reading and reference.*
