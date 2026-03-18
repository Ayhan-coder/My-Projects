/*
 * CMPE322 Project 2 - Parallel Hash Implementation
 * Implementation of parallel and sequential hashing algorithms
 */

#include "hash_parallelization_v3.h"
#include <string.h>

// Thread argument structure
struct thread_args {
    int thread_id;
    int start_idx;
    int end_idx;
};

// Helper function to get time in nanoseconds
static int64_t get_time_ns(struct timespec *ts) {
    return (int64_t)ts->tv_sec * 1000000000LL + (int64_t)ts->tv_nsec;
}

// Array allocation function
int array_allocation() {
    // Allocate hash array (array of pointers to entry_struct)
    hash_array = (struct entry_struct **)malloc(n * sizeof(struct entry_struct *));
    if (hash_array == NULL) {
        return -1;
    }
    
    // Initialize all hash array entries to NULL
    for (int i = 0; i < n; i++) {
        hash_array[i] = NULL;
    }
    
    // Allocate entry list (array of entry_struct)
    entry_list = (struct entry_struct *)malloc(m * sizeof(struct entry_struct));
    if (entry_list == NULL) {
        free(hash_array);
        return -1;
    }
    
    // Initialize entry list values
    for (int i = 0; i < m; i++) {
        entry_list[i].value = i;
        entry_list[i].timestamp = 0;
    }
    
    // Allocate lock list (array of mutex locks)
    lock_list = (pthread_mutex_t *)malloc(n * sizeof(pthread_mutex_t));
    if (lock_list == NULL) {
        free(hash_array);
        free(entry_list);
        return -1;
    }
    
    // Initialize all locks
    for (int i = 0; i < n; i++) {
        if (pthread_mutex_init(&lock_list[i], NULL) != 0) {
            // Clean up already initialized locks
            for (int j = 0; j < i; j++) {
                pthread_mutex_destroy(&lock_list[j]);
            }
            free(hash_array);
            free(entry_list);
            free(lock_list);
            return -1;
        }
    }
    
    return 0;
}

// Array deallocation function
int array_deallocation() {
    // Destroy all locks
    for (int i = 0; i < n; i++) {
        pthread_mutex_destroy(&lock_list[i]);
    }
    
    // Free all allocated arrays
    free(hash_array);
    free(entry_list);
    free(lock_list);
    
    return 0;
}

// Sequential h_1 implementation
int sequential_h_1() {
    struct timespec ts;
    
    // Process all entries
    for (int idx = 0; idx < m; idx++) {
        int i = entry_list[idx].value;
        int c = 0;
        
        // Find an empty slot
        while (1) {
            int pos = (i + c) % n;
            
            if (hash_array[pos] == NULL) {
                // Empty slot found, place the entry
                hash_array[pos] = &entry_list[idx];
                
                // Get timestamp
                clock_gettime(CLOCK_MONOTONIC, &ts);
                entry_list[idx].timestamp = get_time_ns(&ts);
                break;
            } else {
                // Collision, increment c
                c++;
            }
        }
    }
    
    return 0;
}

// Thread function for parallel_h_1
void *parallel_h_1_thread(void *arg) {
    struct thread_args *args = (struct thread_args *)arg;
    struct timespec ts;
    
    // Process entries assigned to this thread
    for (int idx = args->start_idx; idx < args->end_idx; idx++) {
        int i = entry_list[idx].value;
        int c = 0;
        
        // Find an empty slot
        while (1) {
            int pos = (i + c) % n;
            
            // Try to acquire lock
            if (pthread_mutex_trylock(&lock_list[pos]) == 0) {
                // Lock acquired, check if slot is empty
                if (hash_array[pos] == NULL) {
                    // Empty slot found, place the entry
                    hash_array[pos] = &entry_list[idx];
                    
                    // Get timestamp
                    clock_gettime(CLOCK_MONOTONIC, &ts);
                    entry_list[idx].timestamp = get_time_ns(&ts);
                    
                    pthread_mutex_unlock(&lock_list[pos]);
                    break;
                } else {
                    // Slot is occupied, release lock and try next
                    pthread_mutex_unlock(&lock_list[pos]);
                    c++;
                }
            }
            // If lock acquisition failed or slot was occupied, continue loop
            // This effectively retries with the current or incremented c value
        }
    }
    
    return NULL;
}

// Parallel h_1 implementation
int parallel_h_1() {
    pthread_t *threads = malloc(t * sizeof(pthread_t));
    struct thread_args *args = malloc(t * sizeof(struct thread_args));
    int entries_per_thread = m / t;
    
    // Create threads
    for (int i = 0; i < t; i++) {
        args[i].thread_id = i;
        args[i].start_idx = i * entries_per_thread;
        // Last thread gets any remaining entries
        if (i == t - 1) {
            args[i].end_idx = m;
        } else {
            args[i].end_idx = (i + 1) * entries_per_thread;
        }
        
        if (pthread_create(&threads[i], NULL, parallel_h_1_thread, &args[i]) != 0) {
            free(threads);
            free(args);
            return -1;
        }
    }
    
    // Wait for all threads to complete
    for (int i = 0; i < t; i++) {
        pthread_join(threads[i], NULL);
    }
    
    free(threads);
    free(args);
    return 0;
}

// Thread function for parallel_h_2
void *parallel_h_2_thread(void *arg) {
    struct thread_args *args = (struct thread_args *)arg;
    struct timespec ts;
    int num_windows = n / k;
    
    // Process entries assigned to this thread
    for (int idx = args->start_idx; idx < args->end_idx; idx++) {
        int i = entry_list[idx].value;
        int c = 0;
        
        // Find an empty slot
        while (1) {
            int rand_val = get_random_val();
            int acquired_locks[num_windows];
            int lock_count = 0;
            int all_locks_acquired = 1;
            
            // Try to acquire all locks for this collision count
            for (int cnt = 0; cnt < num_windows; cnt++) {
                int window_idx = (rand_val + cnt) % num_windows;
                int pos = ((i + c) % k) + window_idx * k;
                
                if (pthread_mutex_trylock(&lock_list[pos]) == 0) {
                    acquired_locks[lock_count++] = pos;
                } else {
                    // Failed to acquire lock, release all and retry
                    all_locks_acquired = 0;
                    for (int j = 0; j < lock_count; j++) {
                        pthread_mutex_unlock(&lock_list[acquired_locks[j]]);
                    }
                    break;
                }
            }
            
            if (!all_locks_acquired) {
                // Failed to acquire all locks, retry (go to S4)
                continue;
            }
            
            // All locks acquired, check for empty slot
            int found_slot = 0;
            int found_pos = -1;
            
            for (int cnt = 0; cnt < num_windows; cnt++) {
                int window_idx = (rand_val + cnt) % num_windows;
                int pos = ((i + c) % k) + window_idx * k;
                
                if (hash_array[pos] == NULL) {
                    found_slot = 1;
                    found_pos = pos;
                    break;
                }
            }
            
            if (found_slot) {
                // Empty slot found, place the entry
                hash_array[found_pos] = &entry_list[idx];
                
                // Get timestamp
                clock_gettime(CLOCK_MONOTONIC, &ts);
                entry_list[idx].timestamp = get_time_ns(&ts);
                
                // Release all locks
                for (int j = 0; j < lock_count; j++) {
                    pthread_mutex_unlock(&lock_list[acquired_locks[j]]);
                }
                break;
            } else {
                // No empty slot found, release all locks and increment c
                for (int j = 0; j < lock_count; j++) {
                    pthread_mutex_unlock(&lock_list[acquired_locks[j]]);
                }
                c++;
            }
        }
    }
    
    return NULL;
}

// Parallel h_2 implementation
int parallel_h_2() {
    pthread_t *threads = malloc(t * sizeof(pthread_t));
    struct thread_args *args = malloc(t * sizeof(struct thread_args));
    int entries_per_thread = m / t;
    
    // Create threads
    for (int i = 0; i < t; i++) {
        args[i].thread_id = i;
        args[i].start_idx = i * entries_per_thread;
        // Last thread gets any remaining entries
        if (i == t - 1) {
            args[i].end_idx = m;
        } else {
            args[i].end_idx = (i + 1) * entries_per_thread;
        }
        
        if (pthread_create(&threads[i], NULL, parallel_h_2_thread, &args[i]) != 0) {
            free(threads);
            free(args);
            return -1;
        }
    }
    
    // Wait for all threads to complete
    for (int i = 0; i < t; i++) {
        pthread_join(threads[i], NULL);
    }
    
    free(threads);
    free(args);
    return 0;
}

// Speedup comparison for h_1
int speedup_comparison_h_1() {
    struct timespec start, end;
    int64_t sequential_time, parallel_time;
    
    // Measure sequential h_1 time
    clock_gettime(CLOCK_MONOTONIC, &start);
    sequential_h_1();
    clock_gettime(CLOCK_MONOTONIC, &end);
    sequential_time = get_time_ns(&end) - get_time_ns(&start);
    
    // Reset hash array for parallel run
    for (int i = 0; i < n; i++) {
        hash_array[i] = NULL;
    }
    for (int i = 0; i < m; i++) {
        entry_list[i].timestamp = 0;
    }
    
    // Measure parallel h_1 time
    clock_gettime(CLOCK_MONOTONIC, &start);
    parallel_h_1();
    clock_gettime(CLOCK_MONOTONIC, &end);
    parallel_time = get_time_ns(&end) - get_time_ns(&start);
    
    // Calculate speedup
    h_1_speedup = (double)sequential_time / (double)parallel_time;
    
    return 0;
}
