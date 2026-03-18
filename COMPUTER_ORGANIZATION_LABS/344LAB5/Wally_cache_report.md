**Default Parameters**

| Parameter | Value (default) |
| - | - |
| `DCACHE_NUMWAYS` | 4 |
| `DCACHE_WAYSIZEINBYTES` | 4096 bytes |
| `DCACHE_LINELENINBITS` | 512 bits |
| `CACHE_SRAMLEN` | 128 |
| `ICACHE_NUMWAYS` | 4 |
| `ICACHE_WAYSIZEINBYTES` | 4096 bytes |
| `ICACHE_LINELENINBITS` | 512 bits |

**Question 1. What is the size of the I$ cache and the D$ cache?**

Calculation:
- One way size: `4096 bytes`
- Number of ways: `4`
- Total cache size = `num_ways * way_size` = `4 * 4096 bytes = 16384 bytes = 16 KB`

Answer:
- I$ size = 16 KB
- D$ size = 16 KB

**Question 2. Data is retrieved in blocks to the cache, how many instructions are updated into the I$ at once?**

Calculation & simple description:
- I$ cache line length = `ICACHE_LINELENINBITS = 512 bits`.
- Standard RISC-V base instruction width = `32 bits` (RV32), so the number of 32-bit instructions per line is:
  - `512 bits / 32 bits = 16` instructions per cache line.

Answer:
- On a single I$ fill, 16 (32-bit) instructions are brought in at once.
- (If compressed 16-bit instructions are used, a single line can hold up to 32 half-words; the 16 number refers to full 32-bit instruction equivalents.)

**Question 3. Given that one data word is 32 bits, how many 32-bit words are brought into the D$ on a single cache fill?**

Calculation:
- D$ cache line length = `DCACHE_LINELENINBITS = 512 bits`.
- One data word = `32 bits`.
- Words per line = `512 / 32 = 16` 32-bit words.

Answer:
- 16 32-bit words are brought into the D$ per cache fill.

**Question 4. When does a cache miss and a cache hit occur?**

The explanation of cache hits and misses is detailed in **Section 5.3, "The Basics of Caches"** of Patterson & Hennessy.

**Cache Hit:**
- A cache hit occurs when the data requested by the processor appear in some block in the upper level of the memory hierarchy (p. 83).
- In a direct-mapped cache, a hit requires that the **valid bit is on** and the **tag matches** the upper portion of the requested address (pp. 398, 581, 583).
- It is analogous to finding the needed information in one of the books already on your desk.

**Cache Miss:**
- A cache miss occurs if the data requested by the processor are **not found** in the upper level (p. 84).
- The lower level in the hierarchy is then accessed to retrieve the block containing the requested data (p. 85).
- In a direct-mapped cache, a miss occurs if the index selects an entry where the valid bit is off, or if the valid bit is on but the address tag does not match the stored tag (pp. 398, 581, 583).

**References:**
- Patterson & Hennessy, *Computer Organization and Design: The Hardware/Software Interface* (Second Edition), Section 5.3, pp. 83–85, 398, 581, 583.

**Question 5. Wally RTL design follows the write-back strategy to provide cache-memory consistency. Briefly explain what this strategy is and how it differs from write-through.**

The write-back and write-through strategies for handling writes to memory are explained in **Section 5.3, "Handling Writes"** of Patterson & Hennessy (pp. 727–731).

**Write-Back Strategy:**
- In a write-back scheme, when a write occurs, the new value is written **only to the block in the cache** (p. 728).
- The modified block is written to the lower level of the hierarchy (main memory) only when it is **replaced** (pp. 701, 703, 729).
- To track if a block has been modified, a **dirty bit** is associated with the cache block (p. 728).
- This scheme is often more complex to implement than write-through but can **improve performance** (pp. 730, 731).

**Write-Through Strategy:**
- In this scheme, writes **always update both the cache and the next lower level of the memory hierarchy** (pp. 698, 699, 709).
- This ensures that the data in the cache and memory are always consistent (p. 699).

**Key Difference:**
- Write-through requires an update to the lower memory hierarchy on *every* write (p. 716).
- Write-back avoids this frequent update, delaying the memory write until the modified block is replaced (p. 729).

**References:**
- Patterson & Hennessy, *Computer Organization and Design: The Hardware/Software Interface* (Second Edition), Section 5.3, pp. 698–703, 709–710, 716, 727–731.

**(Bonus) What design choices are to be made if we would like to introduce additional L2 cache into the Wally RTL design?**

Key design choices (high level) and places in the Wally codebase to review / modify:
- Cache hierarchy interface:
  - Define L1 (I$ and D$) to L2 interface signals (requests, responses, write-back channels, validity/ack signals, and arbitration). The modules to inspect in the repository:
    - `src/cache/cache.sv` -- top-level cache module implementing set-associative behavior and interfacing to higher/lower levels.
    - `src/cache/cachefsm.sv` -- cache finite-state machine logic (handle miss/fill/evict flows).
    - `src/cache/cacheLRU.sv` -- LRU replacement logic for ways.
    - `src/cache/cacheway.sv` -- per-way storage and tag handling.
    - `src/cache/subcachelineread.sv` -- sub-line read helper used when reading/writing parts of a line.
  - The LSU is the primary user of D$ and coordinates memory accesses. Check `src/lsu/lsu.sv` and related LSU helpers (`align.sv`, `atomic.sv`) to integrate L2 responses.
- Inclusion of an L2 level implies:
  - L2 capacity, associativity, and line size decisions (power-of-two sizes; choose L2 line size compatible with L1 or allow sub-line fills).
  - Replacement policy (LRU/PLRU), write policy (write-back/write-back for L1 and possibly write-back or write-through for L2), and coherence/consistency strategy if multiple masters/cores are present.
  - Miss handling and MSHRs (Miss Status Holding Registers) sizing: L2 introduces latency; L1 must be able to track outstanding misses and forward fills from L2. Cache FSMs (`cachefsm.sv`) will need to be extended to communicate with L2.
  - Bus or interconnect arbitration: how L1 and other masters access L2 and main memory (AHB/AXI interconnect design). Wally uses AHB-like parameters; review top-level interconnect logic and arbitration.
  - SRAM/bank/porting considerations: L2 SRAM structures might be larger and multi-ported or banked for parallelism. CACHE_SRAMLEN and `USE_SRAM` configuration determine memory instantiation style.
  - Inclusion of write-back buffers between levels to smooth bursts of writebacks.
- Practical code locations to change / inspect in the Wally repo:
  - `config/rv32gc/config.vh` (existing cache params) — add/extend parameters for L2 size/associativity/line size.
  - `src/cache/*` (listed above) — extend top-level cache module to talk to an L2 controller; add an L2 controller module (e.g., `l2cache.sv`) implementing larger SRAM and the logic for fills/evictions.
  - `src/lsu/lsu.sv` — ensure LSU's memory request path and responses are routed correctly through L2; update any assumptions about single-cycle or fixed latency memory interface.
  - Top-level integration (e.g., `cvw.sv` or `src/wally/...`) — instantiate the L2 and connect it to AHB/interconnect and to L1s.

Relevant files in the official repository (examples):
- Config file (cache params):
  - https://raw.githubusercontent.com/openhwgroup/cvw/master/config/rv32gc/config.vh
- Cache implementation files:
  - `src/cache/cache.sv` (https://github.com/openhwgroup/cvw/blob/main/src/cache/cache.sv)
  - `src/cache/cachefsm.sv` (https://github.com/openhwgroup/cvw/blob/main/src/cache/cachefsm.sv)
  - `src/cache/cacheLRU.sv` (https://github.com/openhwgroup/cvw/blob/main/src/cache/cacheLRU.sv)
  - `src/cache/cacheway.sv` (https://github.com/openhwgroup/cvw/blob/main/src/cache/cacheway.sv)
  - `src/cache/subcachelineread.sv` (https://github.com/openhwgroup/cvw/blob/main/src/cache/subcachelineread.sv)
- LSU files to inspect:
  - `src/lsu/lsu.sv` (https://github.com/openhwgroup/cvw/blob/main/src/lsu/lsu.sv)
  - Other helpful LSU helpers in `src/lsu/` (e.g., `align.sv`, `atomic.sv`).

Notes on implementation effort:
- Adding an L2 requires design and verification work: RTL changes for new modules, updating cache FSMs, extending configuration parameters, and adding tests to exercise fills/evictions and correctness under load.
- You will also want to add regression tests (in `tests/` or `testbench/`) to validate multi-level behavior and update `config.vh` appropriately.

---

References and links used:
- `config/rv32gc/config.vh` (default parameter values were read from): https://raw.githubusercontent.com/openhwgroup/cvw/master/config/rv32gc/config.vh
- Cache modules in Wally repository: https://github.com/openhwgroup/cvw/tree/main/src/cache
- LSU modules: https://github.com/openhwgroup/cvw/tree/main/src/lsu
- Patterson & Hennessy, Computer Organization and Design (RISC-V Edition) — chapter(s) on cache/memory hierarchy (textbook for cache definitions and write policies).
- Hennessy & Patterson, Computer Architecture: A Quantitative Approach — cache design overview.
- Wikipedia: CPU cache — for a concise conceptual summary: https://en.wikipedia.org/wiki/CPU_cache

---