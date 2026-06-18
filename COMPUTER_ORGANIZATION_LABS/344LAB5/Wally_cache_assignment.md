# Wally Processor Cache Assignment

## Default Parameters

The following table lists the default cache configuration parameters for the Wally rv32gc architecture, as defined in `config/rv32gc/config.vh`.

| Parameter | Value | Description |
| :--- | :--- | :--- |
| `DCACHE_NUMWAYS` | 4 | Associativity of the D$ cache |
| `DCACHE_WAYSIZEINBYTES` | 4096 | Capacity of one way in the D$ cache (bytes) |
| `DCACHE_LINELENINBITS` | 512 | Cache line size for the D$ cache (bits) |
| `CACHE_SRAMLEN` | 128 | Number of rows in the SRAMs |
| `ICACHE_NUMWAYS` | 4 | Associativity of the I$ cache |
| `ICACHE_WAYSIZEINBYTES` | 4096 | Capacity of one way in the I$ cache (bytes) |
| `ICACHE_LINELENINBITS` | 512 | Cache line size for the I$ cache (bits) |

## Question 1
**What is the size of the I$ cache and the D$ cache?**

**Calculation:**
The total size of a cache is calculated as:
`Total Size = Number of Ways × Size per Way`

For I$:
* `ICACHE_NUMWAYS` = 4
* `ICACHE_WAYSIZEINBYTES` = 4096 bytes
* Size = 4 × 4096 = 16,384 bytes = 16 KB

For D$:
* `DCACHE_NUMWAYS` = 4
* `DCACHE_WAYSIZEINBYTES` = 4096 bytes
* Size = 4 × 4096 = 16,384 bytes = 16 KB

**Answer:** Both the I$ cache and the D$ cache are 16 KB in size.

## Question 2
**Data is retrieved in blocks to the cache, how many instructions are updated into the I$ at once?**

**Calculation:**
The I$ updates one cache line at a time.
* Cache Line Length (`ICACHE_LINELENINBITS`) = 512 bits
* Standard RISC-V Instruction Size = 32 bits
* Instructions per Line = 512 / 32 = 16

**Answer:** 16 instructions (32-bit each) are updated into the I$ at once during a cache fill.

## Question 3
**Given that one data word is 32 bits, how many 32-bit words are brought into the D$ on a single cache fill?**

**Calculation:**
The D$ updates one cache line at a time.
* Cache Line Length (`DCACHE_LINELENINBITS`) = 512 bits
* Word Size = 32 bits
* Words per Line = 512 / 32 = 16

**Answer:** 16 words (32-bit each) are brought into the D$ on a single cache fill.

## Question 4
**When does a cache miss and a cache hit occur?**

**Cache Hit:** Occurs when the processor requests data from a memory address, and that data is already present in the cache. Specifically, the address tag matches a valid entry in the cache set.

**Cache Miss:** Occurs when the requested data is not found in the cache. This happens if the address tag does not match any valid entry in the set (compulsory, capacity, or conflict miss), or if the valid bit is not set.

*References:*
* Patterson, D. A., & Hennessy, J. L. *Computer Organization and Design: The Hardware/Software Interface*. Chapter on Memory Hierarchy.
* Hennessy, J. L., & Patterson, D. A. *Computer Architecture: A Quantitative Approach*.

## Question 5
**Wally RTL design follows the write-back strategy to provide cache-memory consistency. Briefly explain what this strategy is and how it differs from write-through.**

**Write-Back Strategy:** In a write-back cache, when data is modified (written) by the processor, it is updated only in the cache initially. The cache line is marked as "dirty" to indicate it differs from main memory. The modified data is written back to main memory only when the cache line is evicted (replaced) to make room for new data.

**Difference from Write-Through:**
* **Write-Through:** Updates both the cache and the main memory simultaneously on every write operation. This ensures memory is always consistent with the cache but requires more memory bandwidth.
* **Write-Back:** Updates memory lazily (only on eviction), reducing memory traffic but requiring a "dirty bit" and more complex control logic to handle evictions.

*References:*
* Patterson, D. A., & Hennessy, J. L. *Computer Organization and Design*. Section on Cache Write Policies.

## (Bonus)
**What design choices are to be made if we would like to introduce additional L2 cache into the Wally RTL design?**

Introducing an L2 cache involves several architectural and implementation choices:

* **Hierarchy Interface:** Define the interface between L1 (I$/D$) and L2. The L1 cache controller (`src/cache/cache.sv`, `src/cache/cachefsm.sv`) needs to be modified to send miss requests to L2 instead of the main memory bus.
* **L2 Configuration:** Determine L2 parameters (Size, Associativity, Line Size). These would be added to `config.vh`. L2 is typically larger and unified (stores both instructions and data).
* **Inclusion Policy:** Decide between Inclusive (L2 contains all L1 data), Exclusive (L2 contains only victim blocks from L1), or NINE (Non-Inclusive Non-Exclusive).
* **Coherence:** If multiple cores are used, a coherence protocol (like MESI) is needed.
* **Memory Interface:** The L2 controller will interface with the system bus (AHB/AXI). The LSU (`src/lsu/lsu.sv`) might need adjustments if latency assumptions change, though it primarily interacts with L1.

**Relevant Code Units:**
* `config/rv32gc/config.vh`: Add L2 parameters.
* `src/cache/cache.sv`: Modify to interface with L2.
* `src/cache/cachefsm.sv`: Update state machine for L2 interaction.
* `src/lsu/lsu.sv`: Verify memory request handling.
