# CMPE476 - C10K Project

## Group Members

| Name | Student ID | Contribution |
|------|-----------|--------------|
| Ali Ayhan Gunder | 2021400219 | Co-implemented the servers and protocol handling, and contributed to debugging/validation and report preparation. |
| Battal Hazar | 2022400318 | Co-implemented the servers and protocol handling, and contributed to debugging/validation and report preparation. |

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

## Submission archive (tar.gz)

The required submission format is a **single** `.tar.gz` (not `.zip`) named exactly:

`textCMPE476-C10k-<group_id>-<surname1>[_<surname2>].tar.gz`

This repo includes a cross-platform packager:

```bash
python pack_submission.py --group-id <group_id> --surname1 <surname1> [--surname2 <surname2>]
```

If your instructor requires a different exact filename, you can override it:

```bash
python pack_submission.py --output-name CMPE476-C10k-surname1-surname2.tar.gz
```

It will fail if `report.pdf` is missing (build it from `report.tex` first).

If you are using WSL/Git-Bash, you can also stage + (optionally) package via:

```bash
./prepare_submission.sh <group_id> <surname1> [surname2]
```
