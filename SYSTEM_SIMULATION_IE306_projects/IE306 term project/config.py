"""
Shared project parameters — all values taken directly from the project specification
(term_project.pdf), except BASE_SEED which is a team choice.
"""

# ---------------------------------------------------------------------------
# Simulation time window  (§3.2 / Table 13)
# ---------------------------------------------------------------------------
SIM_START  = 6 * 3600    # 06:00 as seconds since midnight (clock offset reference)
SIM_END    = 22 * 3600   # 22:00
WARMUP     = 3600        # 1-hour warm-up: 06:00–07:00
TOTAL_TIME = SIM_END - SIM_START  # 57 600 s

N_REPS    = 20             # replications per scenario
T_CRIT_95 = 2.093024054   # t_{0.025, 19}  (95 % CI, df = 19)
BASE_SEED = 42             # team choice; identical across S1–S6 for CRN

TIME_EPS  = 1e-9           # numerical guard for period-boundary comparisons

# ---------------------------------------------------------------------------
# Time-of-day periods  (Table 3)  — seconds since 06:00
# ---------------------------------------------------------------------------
# Four-entry ordered list used by the simulation for headway and demand lookup.
# The 'low' entry covers only 19:00–22:00; the early-morning window (06:00–07:00)
# returns 'low' via the default branch of get_period().
PERIODS = [
    ('am_peak', 3600,  10800),   # 07:00–09:00
    ('midday',  10800, 39600),   # 09:00–17:00
    ('pm_peak', 39600, 46800),   # 17:00–19:00
    ('low',     46800, 57600),   # 19:00–22:00
]

# Both disjoint sub-windows that jointly form the 'low' period.
# Used by input_analysis.py to compute inter-arrival times without crossing the gap.
LOW_WINDOWS = [(0, 3600), (46800, 57600)]   # 06:00–07:00  and  19:00–22:00

PERIOD_CHANGE_POINTS = [3600, 10800, 39600, 46800]   # boundaries where headways/rates shift

# ---------------------------------------------------------------------------
# Terminal parameters  (Table 1)
# ---------------------------------------------------------------------------
TERMINAL_PARAMS = {
    'A1': {'berths': 3, 'wait_cap': 1500, 'turnstiles': 8, 'dwell_min': 6},
    'A2': {'berths': 2, 'wait_cap':  600, 'turnstiles': 4, 'dwell_min': 5},
    'E1': {'berths': 3, 'wait_cap': 1200, 'turnstiles': 6, 'dwell_min': 6},
    'E2': {'berths': 2, 'wait_cap':  800, 'turnstiles': 4, 'dwell_min': 5},
}

# ---------------------------------------------------------------------------
# Ferry line parameters  (Table 2)  — headways and travel time in minutes
# ---------------------------------------------------------------------------
FERRY_LINE_PARAMS = {
    'L1': {'origin': 'A1', 'dest': 'E1', 'cap': 400, 'peak_hw': 15, 'offpeak_hw': 30, 'travel': 20},
    'L2': {'origin': 'A1', 'dest': 'E2', 'cap': 200, 'peak_hw': 20, 'offpeak_hw': 40, 'travel': 25},
    'L3': {'origin': 'A2', 'dest': 'E1', 'cap': 200, 'peak_hw': 20, 'offpeak_hw': 40, 'travel': 15},
    'L4': {'origin': 'A2', 'dest': 'E2', 'cap': 200, 'peak_hw': 30, 'offpeak_hw': 60, 'travel': 20},
    'L5': {'origin': 'E1', 'dest': 'E2', 'cap': 200, 'peak_hw': 15, 'offpeak_hw': 15, 'travel': 10},
}

# All directed line names — fixed list used to pre-allocate weather RNG streams so that
# stream indices are stable whether or not the shuttle (L5) is active (CRN requirement).
ALL_LINE_NAMES = [
    'L1', 'L1_rev',
    'L2', 'L2_rev',
    'L3', 'L3_rev',
    'L4', 'L4_rev',
    'L5', 'L5_rev',
]

# ---------------------------------------------------------------------------
# Service parameters  (§1.4 / Table 13)
# ---------------------------------------------------------------------------
TURNSTILE_MEAN_S = 3.0   # Exp(mean = 3 s) per passenger
BOARDING_MEAN_S  = 1.0   # Exp(mean = 1 s) per passenger

# ---------------------------------------------------------------------------
# Demand parameters  (Table 5 — A2 and E2 given directly;
#                     A1 and E1 rates are estimated from CSV data)
# ---------------------------------------------------------------------------
A2_BASE_RATE_MIN = 1000.0 / 60.0   # pax/min  (dominant-direction peak)
E2_BASE_RATE_MIN =  500.0 / 60.0   # pax/min

A2_SPLITS = {'E1': 0.55, 'E2': 0.45}
E2_SPLITS = {'A1': 0.60, 'A2': 0.40}

# Direction multipliers by time period  (Table 6)
DIR_MULT = {
    'Asia->Europe': {'am_peak': 1.0, 'midday': 0.4, 'pm_peak': 0.3, 'low': 0.15},
    'Europe->Asia': {'am_peak': 0.3, 'midday': 0.4, 'pm_peak': 1.0, 'low': 0.15},
}

# ---------------------------------------------------------------------------
# Route switching  (§1.6 / Table 8)
# ---------------------------------------------------------------------------
ROUTE_SWITCH_PROB = 0.60   # probability q of taking the indirect route when left behind

# Indirect routes via L5: origin -> {final_dest -> transfer_terminal}
# Only four OD pairs have an indirect alternative (Table 8).
INDIRECT_ROUTES = {
    'A1': {'E2': 'E1'},
    'A2': {'E2': 'E1'},
    'E2': {'A1': 'E1', 'A2': 'E1'},
}

# ---------------------------------------------------------------------------
# Weather disruption  (§1.7 / Table 13)
# ---------------------------------------------------------------------------
LODOS_P_CANCEL = 0.20   # per-sailing independent cancellation probability under Lodos

# ---------------------------------------------------------------------------
# Data files  (Table 4)
# ---------------------------------------------------------------------------
CSV_A1 = 'arrivals_kadikoy.csv'
CSV_E1 = 'arrivals_eminonu.csv'

# Human-readable destination name → terminal code  (Table 4 example rows)
DEST_MAP = {'Eminonu': 'E1', 'Besiktas': 'E2', 'Kadikoy': 'A1', 'Uskudar': 'A2'}

# ---------------------------------------------------------------------------
# KPI names  (Table 11) — exact strings required by the auto-grader
# ---------------------------------------------------------------------------
KPI_NAMES = [
    'avg_journey_time',
    'avg_jt_eminonu', 'avg_jt_besiktas', 'avg_jt_kadikoy', 'avg_jt_uskudar',
    'loss_rate', 'left_behind_rate', 'throughput',
    'load_factor_L1', 'load_factor_L2', 'load_factor_L3', 'load_factor_L4',
    'avg_wait_kadikoy', 'avg_wait_uskudar', 'avg_wait_eminonu', 'avg_wait_besiktas',
    'berth_util_kadikoy', 'berth_util_eminonu',
    'missed_conn_rate', 'total_pax_served',
]
