"""Generate benchmark chart from the final CSV data."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv

# Read throughput data
tp = {}
with open('throughput_results.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        server = row['server'].strip()
        clients = int(row['clients'].strip())
        rps = float(row['rps'].strip())
        tp.setdefault(server, {'clients': [], 'rps': []})
        tp[server]['clients'].append(clients)
        tp[server]['rps'].append(rps)

# Read memory data
mem = {}
with open('memory_results.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        server = row['server'].strip()
        clients = int(row['clients'].strip())
        rss = float(row['peak_rss_mb'].strip())
        mem.setdefault(server, {'clients': [], 'rss': []})
        mem[server]['clients'].append(clients)
        mem[server]['rss'].append(rss)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

# Throughput chart
for server, data in tp.items():
    marker = 'o' if server == 'epollserv' else 's'
    color = '#2563eb' if server == 'epollserv' else '#dc2626'
    ax1.plot(data['clients'], data['rps'], marker=marker, color=color,
             linewidth=2.2, markersize=9, label=server)
ax1.set_title('Throughput vs. Concurrency', fontsize=14, fontweight='bold')
ax1.set_xlabel('Concurrent Connections', fontsize=12)
ax1.set_ylabel('Requests per Second (RPS)', fontsize=12)
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 11000)

# Memory chart
for server, data in mem.items():
    marker = 'o' if server == 'epollserv' else 's'
    color = '#2563eb' if server == 'epollserv' else '#dc2626'
    ax2.plot(data['clients'], data['rss'], marker=marker, color=color,
             linewidth=2.2, markersize=9, label=server)
ax2.set_title('Memory Footprint (RSS) vs. Concurrency', fontsize=14, fontweight='bold')
ax2.set_xlabel('Concurrent Connections', fontsize=12)
ax2.set_ylabel('Peak RSS (MB)', fontsize=12)
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, 11000)

plt.tight_layout()
plt.savefig('benchmark_chart.png', dpi=150, bbox_inches='tight')
print("Chart saved to benchmark_chart.png")
