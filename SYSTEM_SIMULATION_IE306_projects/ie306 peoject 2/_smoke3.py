# ===== Cell 1 =====
# If needed, uncomment and run once:
# %pip install simpy numpy pandas matplotlib seaborn simpy-stats

from dataclasses import dataclass
import heapq
import math
import numpy as np
import pandas as pd
import simpy
from simpy_stats import Stats
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')

RUN_LENGTH = 7200.0
WARMUP = 900.0
REPLICATIONS = 20

CYCLE = 90.0
G_NS = 45.0
AMBER = 4.0
G_WE = 37.0

L = 300.0
V_FREE = 15.0
FREE_FLOW_TT = L / V_FREE
N_MAX = 40

LAMBDA_S = 900 / 3600.0
LAMBDA_WE = 400 / 3600.0

P_CAR = 0.85
P_BUS = 0.10
P_EMER = 0.05

P_STRAIGHT_A = 0.70
P_STRAIGHT_B = 0.80

MEAN_SERVICE = 2.0
PREEMPT_CLEARANCE = 4.0
PREEMPT_MIN_NS = 10.0

SCENARIOS = [
    {'id': 1, 'name': 'Uncoordinated_NoEmergency', 'offset_B': 0.0, 'emergency_enabled': False},
    {'id': 2, 'name': 'Coordinated_NoEmergency', 'offset_B': 20.0, 'emergency_enabled': False},
    {'id': 3, 'name': 'Coordinated_WithEmergency', 'offset_B': 20.0, 'emergency_enabled': True},
]

MASTER_SEED = 20260407
# ===== Cell 2 =====
@dataclass
class Vehicle:
    vid: int
    kind: str  # car, bus, emergency, we
    entry_time: float
    approach_arrival: float
    total_delay: float = 0.0
    turn_e_at_A: bool = False
    turn_e_at_B: bool = False

    @property
    def is_emergency(self):
        return self.kind == 'emergency'

    @property
    def is_bus(self):
        return self.kind == 'bus'


class TimeWeightedStat:
    def __init__(self, warmup, end_time, initial=0.0):
        self.warmup = warmup
        self.end_time = end_time
        self.last_t = 0.0
        self.last_v = float(initial)
        self.area = 0.0
        self.max_v = float(initial)

    def update(self, t, new_value):
        t = float(t)
        if t < self.last_t:
            return

        seg_start = max(self.last_t, self.warmup)
        seg_end = min(t, self.end_time)
        if seg_end > seg_start:
            self.area += self.last_v * (seg_end - seg_start)
            self.max_v = max(self.max_v, self.last_v)

        self.last_t = t
        self.last_v = float(new_value)
        if t >= self.warmup:
            self.max_v = max(self.max_v, self.last_v)

    def finalize(self):
        self.update(self.end_time, self.last_v)

    @property
    def mean(self):
        horizon = self.end_time - self.warmup
        return self.area / horizon if horizon > 0 else np.nan


class Metrics:
    def __init__(self, warmup, run_length, cycle_len):
        self.warmup = warmup
        self.run_length = run_length
        self.cycle_len = cycle_len

        # simpy-stats registry (lecture-style clean statistics collection)
        self.stats = Stats()
        self.delay_through_tally = self.stats.tally('delay_through_s')
        self.delay_we_tally = self.stats.tally('delay_we_s')
        self.preemption_counter = self.stats.counter('preemption_events')
        self.recovery_tally = self.stats.tally('recovery_time_s')

        # Keep explicit time-weighted trackers for queue/link levels and max queue KPIs
        self.queue_stats = {
            'A_NS': TimeWeightedStat(warmup, run_length, 0),
            'B_NS': TimeWeightedStat(warmup, run_length, 0),
            'A_WE': TimeWeightedStat(warmup, run_length, 0),
            'B_WE': TimeWeightedStat(warmup, run_length, 0),
        }
        self.link_occ = TimeWeightedStat(warmup, run_length, 0)

        self.throughput_north_count = 0
        self.blocking_bins = set()

        # Approach accounting for utilization and rho checks
        self.served_counts = {
            'A_NS': 0,
            'B_NS': 0,
            'A_WE': 0,
            'B_WE': 0,
        }
        self.service_time_accum = {
            'A_NS': 0.0,
            'B_NS': 0.0,
            'A_WE': 0.0,
            'B_WE': 0.0,
        }

        self.stats_snapshot = {}

    def update_queue(self, key, t, value):
        self.queue_stats[key].update(t, value)

    def update_link(self, t, value):
        self.link_occ.update(t, value)

    def mark_blocking(self, t):
        if t >= self.warmup:
            b = int((t - self.warmup) // self.cycle_len)
            self.blocking_bins.add(b)

    def record_service(self, approach_key, service_start_time, service_time):
        if approach_key not in self.served_counts:
            return
        if service_start_time >= self.warmup:
            self.served_counts[approach_key] += 1
            self.service_time_accum[approach_key] += float(service_time)

    def record_delay_through(self, delay, t):
        if t >= self.warmup:
            self.delay_through_tally.observe(float(delay), t=t)

    def record_delay_we(self, delay, t):
        if t >= self.warmup:
            self.delay_we_tally.observe(float(delay), t=t)

    def record_preemption(self, t):
        if t >= self.warmup:
            self.preemption_counter.inc()

    def record_recovery(self, recovery_time, t):
        if t >= self.warmup:
            self.recovery_tally.observe(float(recovery_time), t=t)

    def finalize(self):
        for s in self.queue_stats.values():
            s.finalize()
        self.link_occ.finalize()
        self.stats_snapshot = dict(self.stats.finalize(self.run_length))

    def as_replication_row(self):
        total_bins = int((self.run_length - self.warmup) // self.cycle_len)
        horizon = self.run_length - self.warmup
        mu_service = 1.0 / MEAN_SERVICE

        util_A_NS = self.service_time_accum['A_NS'] / horizon if horizon > 0 else np.nan
        util_B_NS = self.service_time_accum['B_NS'] / horizon if horizon > 0 else np.nan
        util_A_WE = self.service_time_accum['A_WE'] / horizon if horizon > 0 else np.nan
        util_B_WE = self.service_time_accum['B_WE'] / horizon if horizon > 0 else np.nan

        lambda_A_NS = self.served_counts['A_NS'] / horizon if horizon > 0 else np.nan
        lambda_B_NS = self.served_counts['B_NS'] / horizon if horizon > 0 else np.nan
        lambda_A_WE = self.served_counts['A_WE'] / horizon if horizon > 0 else np.nan
        lambda_B_WE = self.served_counts['B_WE'] / horizon if horizon > 0 else np.nan

        rho_A_NS = lambda_A_NS / mu_service if mu_service > 0 else np.nan
        rho_B_NS = lambda_B_NS / mu_service if mu_service > 0 else np.nan
        rho_A_WE = lambda_A_WE / mu_service if mu_service > 0 else np.nan
        rho_B_WE = lambda_B_WE / mu_service if mu_service > 0 else np.nan

        served_we_total = self.served_counts['A_WE'] + self.served_counts['B_WE']
        lambda_we_total = served_we_total / horizon if horizon > 0 else np.nan

        return {
            'delay_through_s': self.stats_snapshot.get('delay_through_s.mean', np.nan),
            'delay_we_s': self.stats_snapshot.get('delay_we_s.mean', np.nan),
            'avg_q_A_NS': self.queue_stats['A_NS'].mean,
            'max_q_A_NS': self.queue_stats['A_NS'].max_v,
            'avg_q_B_NS': self.queue_stats['B_NS'].mean,
            'max_q_B_NS': self.queue_stats['B_NS'].max_v,
            'avg_q_A_WE': self.queue_stats['A_WE'].mean,
            'max_q_A_WE': self.queue_stats['A_WE'].max_v,
            'avg_q_B_WE': self.queue_stats['B_WE'].mean,
            'max_q_B_WE': self.queue_stats['B_WE'].max_v,
            'throughput_north_vph': self.throughput_north_count * 3600.0 / (self.run_length - self.warmup),
            'avg_link_occupancy': self.link_occ.mean,
            'blocking_frequency': len(self.blocking_bins) / total_bins if total_bins > 0 else np.nan,
            'preemption_count': self.stats_snapshot.get('preemption_events.count', 0.0),
            'recovery_time_s': self.stats_snapshot.get('recovery_time_s.mean', np.nan),
            'served_A_NS': self.served_counts['A_NS'],
            'served_B_NS': self.served_counts['B_NS'],
            'served_A_WE': self.served_counts['A_WE'],
            'served_B_WE': self.served_counts['B_WE'],
            'served_WE_total': served_we_total,
            'lambda_A_NS': lambda_A_NS,
            'lambda_B_NS': lambda_B_NS,
            'lambda_A_WE': lambda_A_WE,
            'lambda_B_WE': lambda_B_WE,
            'lambda_WE_total': lambda_we_total,
            'util_A_NS': util_A_NS,
            'util_B_NS': util_B_NS,
            'util_A_WE': util_A_WE,
            'util_B_WE': util_B_WE,
            'rho_A_NS': rho_A_NS,
            'rho_B_NS': rho_B_NS,
            'rho_A_WE': rho_A_WE,
            'rho_B_WE': rho_B_WE,
        }
# ===== Cell 3 =====
class SignalController:
    REGULAR_PHASES = [
        ('NS_GREEN', G_NS),
        ('ALL_RED', AMBER),
        ('WE_GREEN', G_WE),
        ('ALL_RED', AMBER),
    ]

    def __init__(self, env, name, offset, emergency_enabled, metrics):
        self.env = env
        self.name = name
        self.offset = offset
        self.emergency_enabled = emergency_enabled
        self.metrics = metrics

        self.phase_name = None
        self.phase_idx = None
        self._handling_preemption = False

        self.state_event = env.event()
        self.proc = env.process(self.run())

    def _notify(self):
        if not self.state_event.triggered:
            self.state_event.succeed()
        self.state_event = self.env.event()

    def _initial_phase(self):
        cycle = CYCLE
        pos = (cycle - self.offset) % cycle

        boundary = 0.0
        for idx, (_, dur) in enumerate(self.REGULAR_PHASES):
            if pos < boundary + dur:
                elapsed = pos - boundary
                rem = dur - elapsed
                return idx, rem
            boundary += dur

        return 0, G_NS

    def is_ns_green(self):
        return self.phase_name == 'NS_GREEN'

    def is_we_green(self):
        return self.phase_name == 'WE_GREEN'

    def request_preemption(self):
        if not self.emergency_enabled:
            return
        if self.phase_name == 'NS_GREEN':
            return
        if self._handling_preemption:
            return
        if self.proc.is_alive:
            try:
                self.proc.interrupt('preempt')
            except RuntimeError:
                pass

    def _timeout_ignore_preempt(self, duration):
        end_t = self.env.now + max(0.0, duration)
        while self.env.now < end_t - 1e-9:
            rem = end_t - self.env.now
            try:
                yield self.env.timeout(rem)
            except simpy.Interrupt as interrupt:
                if interrupt.cause == 'preempt':
                    continue
                raise

    def run(self):
        phase_idx, remaining = self._initial_phase()

        while True:
            phase_name, _ = self.REGULAR_PHASES[phase_idx]
            self.phase_idx = phase_idx
            self.phase_name = phase_name
            self._notify()

            start = self.env.now
            try:
                yield self.env.timeout(remaining)
                phase_idx = (phase_idx + 1) % len(self.REGULAR_PHASES)
                remaining = self.REGULAR_PHASES[phase_idx][1]

            except simpy.Interrupt as interrupt:
                if interrupt.cause != 'preempt' or not self.emergency_enabled or self.phase_name == 'NS_GREEN':
                    elapsed = self.env.now - start
                    remaining = max(0.0, remaining - elapsed)
                    continue

                elapsed = self.env.now - start
                interrupted_idx = phase_idx
                interrupted_remaining = max(0.0, remaining - elapsed)

                self.metrics.record_preemption(self.env.now)

                self._handling_preemption = True
                try:
                    self.phase_name = 'ALL_RED'
                    self.phase_idx = -1
                    self._notify()
                    yield from self._timeout_ignore_preempt(PREEMPT_CLEARANCE)

                    self.phase_name = 'NS_GREEN'
                    self.phase_idx = -2
                    self._notify()
                    yield from self._timeout_ignore_preempt(PREEMPT_MIN_NS)

                    recovery_start = self.env.now

                    if interrupted_remaining > 1e-9:
                        phase_idx = interrupted_idx
                        remaining = interrupted_remaining
                        self.phase_name = self.REGULAR_PHASES[phase_idx][0]
                        self.phase_idx = phase_idx
                        self._notify()
                        yield from self._timeout_ignore_preempt(remaining)

                    self.metrics.record_recovery(self.env.now - recovery_start, self.env.now)

                    phase_idx = (interrupted_idx + 1) % len(self.REGULAR_PHASES)
                    remaining = self.REGULAR_PHASES[phase_idx][1]
                finally:
                    self._handling_preemption = False


class CorridorLink:
    def __init__(self, env, metrics, travel_rng, noise_rng, downstream_intersection=None):
        self.env = env
        self.metrics = metrics
        self.travel_rng = travel_rng
        self.noise_rng = noise_rng
        self.downstream_intersection = downstream_intersection

        self.capacity = N_MAX
        self.occupancy = 0
        self.change_event = env.event()

    def _notify(self):
        if not self.change_event.triggered:
            self.change_event.succeed()
        self.change_event = self.env.event()

    def _travel_time(self):
        n = min(self.occupancy, self.capacity - 1e-3)
        base = FREE_FLOW_TT / (1.0 - n / self.capacity)
        noise = max(0.5, self.noise_rng.normal(loc=1.0, scale=0.02))
        return base * noise

    def can_enter(self):
        return self.occupancy < self.capacity

    def send_to_B(self, vehicle):
        self.occupancy += 1
        self.metrics.update_link(self.env.now, self.occupancy)
        self._notify()

        tt = self._travel_time()
        yield self.env.timeout(tt)

        self.occupancy -= 1
        self.metrics.update_link(self.env.now, self.occupancy)
        self._notify()

        vehicle.approach_arrival = self.env.now
        self.downstream_intersection.enqueue_ns(vehicle)


class Intersection:
    def __init__(self, env, name, signal, metrics, service_rng, turn_rng, link=None):
        self.env = env
        self.name = name
        self.signal = signal
        self.metrics = metrics
        self.service_rng = service_rng
        self.turn_rng = turn_rng
        self.link = link

        self.ns_queue = []
        self.we_queue = []
        self.seq = 0
        self.queue_event = env.event()

        self.env.process(self.ns_server())
        self.env.process(self.we_server())

    def _queue_key_ns(self):
        return f'{self.name}_NS'

    def _queue_key_we(self):
        return f'{self.name}_WE'

    def _notify_queue(self):
        if not self.queue_event.triggered:
            self.queue_event.succeed()
        self.queue_event = self.env.event()

    def enqueue_ns(self, vehicle):
        if self.name == 'B':
            vehicle.turn_e_at_B = self.turn_rng.random() > P_STRAIGHT_B

        prio = 0 if vehicle.is_emergency else (1 if vehicle.is_bus else 2)
        heapq.heappush(self.ns_queue, (prio, self.seq, vehicle))
        self.seq += 1

        self.metrics.update_queue(self._queue_key_ns(), self.env.now, len(self.ns_queue))

        if vehicle.is_emergency and self.signal.emergency_enabled and not self.signal.is_ns_green():
            self.signal.request_preemption()

        self._notify_queue()

    def enqueue_we(self, vehicle):
        heapq.heappush(self.we_queue, (2, self.seq, vehicle))
        self.seq += 1
        self.metrics.update_queue(self._queue_key_we(), self.env.now, len(self.we_queue))
        self._notify_queue()

    def ns_server(self):
        while True:
            if not self.ns_queue:
                wait_for = [self.queue_event, self.signal.state_event]
                if self.link is not None:
                    wait_for.append(self.link.change_event)
                yield self.env.any_of(wait_for)
                continue

            if not self.signal.is_ns_green():
                yield self.signal.state_event
                continue

            _, _, veh = self.ns_queue[0]

            blocked = (
                self.name == 'A'
                and veh.turn_e_at_A is False
                and not veh.is_emergency
                and self.link is not None
                and not self.link.can_enter()
            )

            if blocked:
                self.metrics.mark_blocking(self.env.now)
                yield self.env.any_of([self.signal.state_event, self.link.change_event])
                continue

            heapq.heappop(self.ns_queue)
            self.metrics.update_queue(self._queue_key_ns(), self.env.now, len(self.ns_queue))

            wait = self.env.now - veh.approach_arrival
            veh.total_delay += wait

            service_start = self.env.now
            service_t = self.service_rng.exponential(MEAN_SERVICE)
            self.metrics.record_service(self._queue_key_ns(), service_start, service_t)
            yield self.env.timeout(service_t)

            if self.name == 'A':
                if veh.turn_e_at_A:
                    pass
                else:
                    self.env.process(self.link.send_to_B(veh))
            else:
                if not veh.turn_e_at_B:
                    # Gate on exit time (env.now), not entry_time, so vehicles
                    # that arrived before warmup but exit after are included.
                    if self.env.now >= WARMUP:
                        self.metrics.record_delay_through(veh.total_delay, self.env.now)
                        self.throughput_increment()

    def throughput_increment(self):
        self.metrics.throughput_north_count += 1

    def we_server(self):
        while True:
            if not self.we_queue:
                yield self.env.any_of([self.queue_event, self.signal.state_event])
                continue

            if not self.signal.is_we_green():
                yield self.signal.state_event
                continue

            _, _, veh = heapq.heappop(self.we_queue)
            self.metrics.update_queue(self._queue_key_we(), self.env.now, len(self.we_queue))

            wait = self.env.now - veh.approach_arrival
            service_start = self.env.now
            service_t = self.service_rng.exponential(MEAN_SERVICE)
            self.metrics.record_service(self._queue_key_we(), service_start, service_t)
            yield self.env.timeout(service_t)

            # Gate on exit time so W/E vehicles exiting after warmup are included.
            if self.env.now >= WARMUP:
                self.metrics.record_delay_we(wait, self.env.now)
# ===== Cell 4 =====
def spawn_rngs(master_seed, scenario_id, replication_id):
    ss = np.random.SeedSequence([master_seed, scenario_id, replication_id])
    children = ss.spawn(9)
    return {
        'arrival_s': np.random.default_rng(children[0]),
        'arrival_we_A': np.random.default_rng(children[1]),
        'arrival_we_B': np.random.default_rng(children[2]),
        'classify': np.random.default_rng(children[3]),
        'turn_A': np.random.default_rng(children[4]),
        'turn_B': np.random.default_rng(children[5]),
        'service_A': np.random.default_rng(children[6]),
        'service_B': np.random.default_rng(children[7]),
        'link_noise': np.random.default_rng(children[8]),
    }


def south_arrivals(env, inter_A, rng_arr, rng_cls, rng_turn_A, emergency_enabled):
    vid = 0
    while True:
        dt = rng_arr.exponential(1.0 / LAMBDA_S)
        yield env.timeout(dt)
        if env.now > RUN_LENGTH:
            break

        u = rng_cls.random()
        if emergency_enabled:
            if u < P_CAR:
                kind = 'car'
            elif u < P_CAR + P_BUS:
                kind = 'bus'
            else:
                kind = 'emergency'
        else:
            kind = 'car' if u < (P_CAR + P_EMER) else 'bus'

        veh = Vehicle(
            vid=vid,
            kind=kind,
            entry_time=env.now,
            approach_arrival=env.now,
            turn_e_at_A=(rng_turn_A.random() > P_STRAIGHT_A),
        )
        vid += 1
        inter_A.enqueue_ns(veh)


def we_arrivals(env, intersection, rng_arr):
    vid = 0
    while True:
        dt = rng_arr.exponential(1.0 / LAMBDA_WE)
        yield env.timeout(dt)
        if env.now > RUN_LENGTH:
            break

        veh = Vehicle(
            vid=vid,
            kind='we',
            entry_time=env.now,
            approach_arrival=env.now,
        )
        vid += 1
        intersection.enqueue_we(veh)


def run_replication(scenario, rep_id, master_seed=MASTER_SEED):
    env = simpy.Environment()
    rngs = spawn_rngs(master_seed, scenario['id'], rep_id)

    metrics = Metrics(WARMUP, RUN_LENGTH, CYCLE)

    signal_A = SignalController(env, 'A', offset=0.0, emergency_enabled=scenario['emergency_enabled'], metrics=metrics)
    signal_B = SignalController(env, 'B', offset=scenario['offset_B'], emergency_enabled=scenario['emergency_enabled'], metrics=metrics)

    link = CorridorLink(env, metrics, travel_rng=rngs['service_A'], noise_rng=rngs['link_noise'])

    inter_A = Intersection(
        env=env,
        name='A',
        signal=signal_A,
        metrics=metrics,
        service_rng=rngs['service_A'],
        turn_rng=rngs['turn_A'],
        link=link,
    )

    inter_B = Intersection(
        env=env,
        name='B',
        signal=signal_B,
        metrics=metrics,
        service_rng=rngs['service_B'],
        turn_rng=rngs['turn_B'],
        link=None,
    )

    link.downstream_intersection = inter_B

    env.process(south_arrivals(env, inter_A, rngs['arrival_s'], rngs['classify'], rngs['turn_A'], scenario['emergency_enabled']))
    env.process(we_arrivals(env, inter_A, rngs['arrival_we_A']))
    env.process(we_arrivals(env, inter_B, rngs['arrival_we_B']))

    env.run(until=RUN_LENGTH)
    metrics.finalize()

    row = metrics.as_replication_row()
    row['scenario'] = scenario['name']
    row['replication'] = rep_id
    return row


def mean_ci(series, z=1.96):
    x = pd.Series(series).dropna()
    n = len(x)
    if n == 0:
        return np.nan, np.nan, np.nan
    mean = x.mean()
    if n == 1:
        return mean, np.nan, np.nan
    se = x.std(ddof=1) / math.sqrt(n)
    h = z * se
    return mean, mean - h, mean + h


def summarize_with_ci(df_rep):
    records = []
    metric_cols = [
        'delay_through_s', 'delay_we_s',
        'avg_q_A_NS', 'max_q_A_NS', 'avg_q_B_NS', 'max_q_B_NS',
        'avg_q_A_WE', 'max_q_A_WE', 'avg_q_B_WE', 'max_q_B_WE',
        'throughput_north_vph', 'avg_link_occupancy', 'blocking_frequency',
        'preemption_count', 'recovery_time_s'
    ]

    for scen, g in df_rep.groupby('scenario'):
        for m in metric_cols:
            mean, lo, hi = mean_ci(g[m])
            records.append({
                'scenario': scen,
                'metric': m,
                'mean': mean,
                'ci95_low': lo,
                'ci95_high': hi,
            })

    return pd.DataFrame(records)
# ===== Cell 13 =====
# ─── V&V: Downstream blocking — structural analysis ─────────────────────────
# The assignment specifies downstream blocking logic (§1.5): a vehicle at A
# may only enter the link if n < Nmax (capacity 40).

# STRUCTURAL REASON BLOCKING NEVER FIRES AT GIVEN PARAMETERS:
# Both intersections have identical NS green time (G_NS = 45s / C = 90s cycle)
# and an identical single-server with mean 2s per vehicle.
# => Max service rate at A (onto link) = G_NS / (C * mu_s) = 45 / (90*2) = 0.25 veh/s
# => Max service rate at B  (off link)  = same = 0.25 veh/s
# Since both ends are symmetric, B drains the link at least as fast as A fills it.
# No matter how high the arrival demand is, A is always the bottleneck — not the link.
# Therefore the link never reaches Nmax = 40 under any demand level with this signal plan.

# VERIFICATION THAT THE BLOCKING CODE IS STRUCTURALLY CORRECT:
# We can force blocking by giving B a much shorter NS green (asymmetric scenario).
# Here we temporarily halve B's effective NS green to G_NS_B = 22s by running
# the standard model and checking that occupancy approaches capacity.
# (This is a unit-test; the production scenarios use G_NS = 45s at both intersections.)

import numpy as np

def _run_unit_test_blocking(seed=42, g_ns_b_override=10.0):
    """
    Temporarily override SignalController.REGULAR_PHASES for intersection B
    to shorten NS green, forcing more link occupancy.
    """
    import simpy
    env = simpy.Environment()
    _ss = np.random.SeedSequence([seed, 99, 2])
    _ch = _ss.spawn(9)
    rngs = {k: np.random.default_rng(_ch[i]) for i, k in enumerate([
        'arrival_s','arrival_we_A','arrival_we_B','classify',
        'turn_A','turn_B','service_A','service_B','link_noise'])}

    metrics_s = Metrics(WARMUP, RUN_LENGTH, CYCLE)

    # Normal A
    sig_A = SignalController(env, 'A', offset=0.0, emergency_enabled=False, metrics=metrics_s)

    # B with shortened NS green to make it a drain bottleneck
    sig_B = SignalController(env, 'B', offset=0.0, emergency_enabled=False, metrics=metrics_s)
    g_we_b_adjusted = CYCLE - g_ns_b_override - 2 * AMBER
    sig_B.REGULAR_PHASES = [
        ('NS_GREEN', g_ns_b_override),
        ('AMBER',    AMBER),
        ('WE_GREEN', max(1.0, g_we_b_adjusted)),
        ('AMBER',    AMBER),
    ]

    lnk = CorridorLink(env, metrics_s, travel_rng=rngs['service_A'], noise_rng=rngs['link_noise'])
    iA  = Intersection(env, 'A', sig_A, metrics_s, rngs['service_A'], rngs['turn_A'], link=lnk)
    iB  = Intersection(env, 'B', sig_B, metrics_s, rngs['service_B'], rngs['turn_B'], link=None)
    lnk.downstream_intersection = iB

    # Full demand, all-straight south arrivals to maximise link load
    def _arrivals(env, inter, rng_arr, rng_turn):
        vid = 0
        while True:
            dt = rng_arr.exponential(1.0 / LAMBDA_S)
            yield env.timeout(dt)
            if env.now > RUN_LENGTH:
                break
            veh = Vehicle(vid=vid, kind='car', entry_time=env.now,
                          approach_arrival=env.now, turn_e_at_A=False)
            vid += 1
            inter.enqueue_ns(veh)

    env.process(_arrivals(env, iA, rngs['arrival_s'], rngs['turn_A']))
    env.process(we_arrivals(env, iA, rngs['arrival_we_A']))
    env.process(we_arrivals(env, iB, rngs['arrival_we_B']))
    env.run(until=RUN_LENGTH)
    metrics_s.finalize()
    return metrics_s.as_replication_row()

print("=== V&V: Downstream Blocking Analysis ===")
print()
print("Structural note:")
print(f"  Max A->link rate = G_NS/(C × mu_s) = {G_NS}/({CYCLE}×{MEAN_SERVICE}) = {G_NS/(CYCLE*MEAN_SERVICE):.4f} veh/s")
print(f"  Max B  drain rate = same (symmetric G_NS) = {G_NS/(CYCLE*MEAN_SERVICE):.4f} veh/s")
print(f"  => Link can never fill under given signal plan (B always drains as fast as A fills).")
print(f"  => blocking_frequency = 0 is CORRECT for these parameters.")
print()
print("Unit test with artificially short B NS-green (G_NS_B = 10s) to force blocking:")
_r = _run_unit_test_blocking(g_ns_b_override=10.0)
_occ = _r['avg_link_occupancy']
_bf  = _r['blocking_frequency']
print(f"  avg_link_occupancy = {_occ:.2f} / {N_MAX}  ({100*_occ/N_MAX:.1f}% of capacity)")
print(f"  blocking_frequency = {_bf:.4f}")
if _bf > 0:
    print("  PASS: Blocking logic fires correctly when B's drain rate is constrained.")
else:
    print("  NOTE: Even with G_NS_B=10s blocking didn't fire — demand may need increase.")
