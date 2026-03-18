# CoreMark Data Collection Sheet

## System Information
- [ ] Collected CPU information
- [ ] Noted clock frequencies
- [ ] Documented compiler version

---

## Default Build Runs

| Run # | Iterations/Sec | Notes |
|-------|----------------|-------|
| 1     |                |       |
| 2     |                |       |
| 3     |                |       |
| 4     |                |       |
| 5     |                |       |

**Average:** __________

---

## -O0 Optimization

| Run # | Iterations/Sec | Notes |
|-------|----------------|-------|
| 1     |                |       |
| 2     |                |       |
| 3     |                |       |
| 4     |                |       |
| 5     |                |       |

**Average:** __________

---

## -O1 Optimization

| Run # | Iterations/Sec | Notes |
|-------|----------------|-------|
| 1     |                |       |
| 2     |                |       |
| 3     |                |       |
| 4     |                |       |
| 5     |                |       |

**Average:** __________

---

## -O2 Optimization

| Run # | Iterations/Sec | Notes |
|-------|----------------|-------|
| 1     |                |       |
| 2     |                |       |
| 3     |                |       |
| 4     |                |       |
| 5     |                |       |

**Average:** __________

---

## -O3 Optimization

| Run # | Iterations/Sec | Notes |
|-------|----------------|-------|
| 1     |                |       |
| 2     |                |       |
| 3     |                |       |
| 4     |                |       |
| 5     |                |       |

**Average:** __________

---

## -Ofast Optimization

| Run # | Iterations/Sec | Notes |
|-------|----------------|-------|
| 1     |                |       |
| 2     |                |       |
| 3     |                |       |
| 4     |                |       |
| 5     |                |       |

**Average:** __________

---

## -march=native Optimization

| Run # | Iterations/Sec | Notes |
|-------|----------------|-------|
| 1     |                |       |
| 2     |                |       |
| 3     |                |       |
| 4     |                |       |
| 5     |                |       |

**Average:** __________

---

## Quick Reference: How to Extract Iterations/Sec

Look for this line in the CoreMark output:
```
CoreMark 1.0 : XXXXX.XXXXXX / GCC... / Heap
                ^^^^^^^^^
                This is your Iterations/Sec value
```

The full line will look something like:
```
CoreMark 1.0 : 12345.678901 / GCC9.3.0 -O2 / Heap
```

Extract: **12345.678901**
