import sys

def parse_strace_c(filename):
    counts = {}
    with open(filename, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2 and parts[-1] == 'syscall': continue
            if len(parts) >= 2 and parts[-1] == 'total': continue
            if len(parts) >= 2 and parts[0].startswith('---'): continue
            if len(parts) < 4: continue
            
            # strace -c output format:
            # % time     seconds  usecs/call     calls    errors syscall
            # The syscall name is the LAST element
            # The count is the 4th element (index 3)
            
            try:
                name = parts[-1]
                count = int(parts[3])
                counts[name] = count
            except ValueError:
                continue
    return counts

empty = parse_strace_c('/tmp/empty_c.txt')
capture = parse_strace_c('/tmp/capture_c.txt')

diffs = []
for name, count in capture.items():
    empty_count = empty.get(name, 0)
    if count > empty_count:
        diffs.append(name)

print('\n'.join(sorted(diffs)))
