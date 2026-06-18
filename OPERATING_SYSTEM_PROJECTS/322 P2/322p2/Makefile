# Makefile for CMPE322 Project 2
# Hash Parallelization Implementation

CC = gcc
CFLAGS = -Wall -pthread -fPIC -I$(SRC_DIR)
LDFLAGS = -pthread -lrt
SRC_DIR = src
TEST_DIR = tests

# Targets
.PHONY: all clean test

all: $(SRC_DIR)/hash_parallelization.so

# Create shared object library
$(SRC_DIR)/hash_parallelization.so: $(SRC_DIR)/hash_parallelization.c $(SRC_DIR)/hash_parallelization_v3.h
	$(CC) -shared $(CFLAGS) -o $(SRC_DIR)/hash_parallelization.so $(SRC_DIR)/hash_parallelization.c $(LDFLAGS)

# Test executable (optional, for testing)
test: $(TEST_DIR)/test_hash

$(TEST_DIR)/test_hash: $(TEST_DIR)/test_hash.c $(SRC_DIR)/hash_parallelization.c $(SRC_DIR)/hash_parallelization_v3.h
	$(CC) $(CFLAGS) -o $(TEST_DIR)/test_hash $(TEST_DIR)/test_hash.c $(SRC_DIR)/hash_parallelization.c $(LDFLAGS)

# Build extreme_test executable
$(TEST_DIR)/extreme_test: $(TEST_DIR)/extreme_test.c $(SRC_DIR)/hash_parallelization.c $(SRC_DIR)/hash_parallelization_v3.h
	$(CC) $(CFLAGS) -o $(TEST_DIR)/extreme_test $(TEST_DIR)/extreme_test.c $(SRC_DIR)/hash_parallelization.c -Wl,--allow-multiple-definition $(LDFLAGS)

# Build mega_test executable (1.5 million entries)
$(TEST_DIR)/mega_test: $(TEST_DIR)/mega_test.c $(SRC_DIR)/hash_parallelization.c $(SRC_DIR)/hash_parallelization_v3.h
	$(CC) $(CFLAGS) -o $(TEST_DIR)/mega_test $(TEST_DIR)/mega_test.c $(SRC_DIR)/hash_parallelization.c -Wl,--allow-multiple-definition $(LDFLAGS)

# Build giga_test executable (10 million entries)
$(TEST_DIR)/giga_test: $(TEST_DIR)/giga_test.c $(SRC_DIR)/hash_parallelization.c $(SRC_DIR)/hash_parallelization_v3.h
	$(CC) $(CFLAGS) -o $(TEST_DIR)/giga_test $(TEST_DIR)/giga_test.c $(SRC_DIR)/hash_parallelization.c -Wl,--allow-multiple-definition $(LDFLAGS)

# Build fuzz_test executable
$(TEST_DIR)/fuzz_test: $(TEST_DIR)/fuzz_test.c $(SRC_DIR)/hash_parallelization.c $(SRC_DIR)/hash_parallelization_v3.h
	$(CC) $(CFLAGS) -o $(TEST_DIR)/fuzz_test $(TEST_DIR)/fuzz_test.c $(SRC_DIR)/hash_parallelization.c -Wl,--allow-multiple-definition $(LDFLAGS)

# Build ultra_test executable (100 million entries)
$(TEST_DIR)/ultra_test: $(TEST_DIR)/ultra_test.c $(SRC_DIR)/hash_parallelization.c $(SRC_DIR)/hash_parallelization_v3.h
	$(CC) $(CFLAGS) -o $(TEST_DIR)/ultra_test $(TEST_DIR)/ultra_test.c $(SRC_DIR)/hash_parallelization.c -Wl,--allow-multiple-definition $(LDFLAGS)

# Build h2_test executable
$(TEST_DIR)/h2_test: $(TEST_DIR)/h2_test.c $(SRC_DIR)/hash_parallelization.c $(SRC_DIR)/hash_parallelization_v3.h
	$(CC) $(CFLAGS) -o $(TEST_DIR)/h2_test $(TEST_DIR)/h2_test.c $(SRC_DIR)/hash_parallelization.c -Wl,--allow-multiple-definition $(LDFLAGS)

# Build h2_mega_test executable (1 million entries)
$(TEST_DIR)/h2_mega_test: $(TEST_DIR)/h2_mega_test.c $(SRC_DIR)/hash_parallelization.c $(SRC_DIR)/hash_parallelization_v3.h
	$(CC) $(CFLAGS) -o $(TEST_DIR)/h2_mega_test $(TEST_DIR)/h2_mega_test.c $(SRC_DIR)/hash_parallelization.c -Wl,--allow-multiple-definition $(LDFLAGS)

clean:
	rm -f $(SRC_DIR)/hash_parallelization.so $(TEST_DIR)/* $(SRC_DIR)/*.o

# Run test
run_test: $(TEST_DIR)/test_hash
	cd $(TEST_DIR) && ./test_hash

# Run extreme test
run_extreme: $(TEST_DIR)/extreme_test
	cd $(TEST_DIR) && ./extreme_test

# Run mega test
run_mega: $(TEST_DIR)/mega_test
	cd $(TEST_DIR) && ./mega_test

# Run giga test
run_giga: $(TEST_DIR)/giga_test
	cd $(TEST_DIR) && ./giga_test

# Run ultra test
run_ultra: $(TEST_DIR)/ultra_test
	cd $(TEST_DIR) && ./ultra_test

# Run fuzz test
run_fuzz: $(TEST_DIR)/fuzz_test
	cd $(TEST_DIR) && ./fuzz_test

# Run h2 test
run_h2: $(TEST_DIR)/h2_test
	cd $(TEST_DIR) && ./h2_test

# Run h2 mega test
run_h2_mega: $(TEST_DIR)/h2_mega_test
	cd $(TEST_DIR) && ./h2_mega_test
