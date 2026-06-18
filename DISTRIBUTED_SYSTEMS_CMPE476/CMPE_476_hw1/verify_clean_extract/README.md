# CMPE476 - C10K Project

<!--
 * @author1: Ali Ayhan Gunder 2021400219 
 * @author2: Battal Hazar 2022400318
-->

## Contributions

- Ali Ayhan Gunder (2021400219): Co-implemented the servers and protocol handling, and contributed to debugging/validation and report preparation.
- Battal Hazar (2022400318): Co-implemented the servers and protocol handling, and contributed to debugging/validation and report preparation.

## Building

```bash
make          # builds threadserv and epollserv
make test     # builds and runs the CUnit test suite
make clean    # removes all generated files
```

## Running

```bash
./threadserv 9090   # thread-per-connection server on port 9090
./epollserv 9091    # epoll event-loop server on port 9091
```
