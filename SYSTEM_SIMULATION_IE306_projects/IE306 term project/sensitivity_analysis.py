"""Run report-only sensitivity experiments around S4 storm conditions.

The required auto-graded outputs remain `results.csv` and `summary.csv`. This script writes
separate sensitivity files so those required outputs are not polluted with non-scenario rows.
"""

import os

import numpy as np
import pandas as pd

from config import BASE_SEED, CSV_A1, CSV_E1, N_REPS, T_CRIT_95
from ferry_simulation import Simulation, analyze_arrivals


SENSITIVITY_KPIS = [
    'avg_journey_time',
    'loss_rate',
    'left_behind_rate',
    'throughput',
]


def main():
    kadikoy_rates = analyze_arrivals(CSV_A1)
    eminonu_rates = analyze_arrivals(CSV_E1)

    scenarios = {
        'cancel_0.10': {
            'shuttle': False,
            'lodos': True,
            'hw_multiplier': 1.0,
            'base_seed': BASE_SEED,
            'cancel_prob': 0.10,
        },
        'cancel_0.20_base': {
            'shuttle': False,
            'lodos': True,
            'hw_multiplier': 1.0,
            'base_seed': BASE_SEED,
            'cancel_prob': 0.20,
        },
        'cancel_0.30': {
            'shuttle': False,
            'lodos': True,
            'hw_multiplier': 1.0,
            'base_seed': BASE_SEED,
            'cancel_prob': 0.30,
        },
        'capacity_0.75': {
            'shuttle': False,
            'lodos': True,
            'hw_multiplier': 1.0,
            'base_seed': BASE_SEED,
            'cancel_prob': 0.20,
            'wait_cap_multiplier': 0.75,
        },
        'capacity_1.25': {
            'shuttle': False,
            'lodos': True,
            'hw_multiplier': 1.0,
            'base_seed': BASE_SEED,
            'cancel_prob': 0.20,
            'wait_cap_multiplier': 1.25,
        },
    }

    rows = []
    for scenario_name, scenario_config in scenarios.items():
        print(f'Running sensitivity {scenario_name}...')
        for rep in range(1, N_REPS + 1):
            sim = Simulation(scenario_name, rep, scenario_config, kadikoy_rates, eminonu_rates)
            kpis = sim.run()
            for kpi in SENSITIVITY_KPIS:
                rows.append({
                    'scenario': scenario_name,
                    'replication': rep,
                    'kpi': kpi,
                    'value': kpis[kpi],
                })

    os.makedirs('sensitivity', exist_ok=True)
    results = pd.DataFrame(rows)
    results.to_csv('sensitivity/sensitivity_results.csv', index=False)

    summary = results.groupby(['scenario', 'kpi'])['value'].agg(
        mean='mean',
        std=lambda x: float(np.std(x, ddof=1)),
        n='count',
    ).reset_index()
    summary['ci_half_width'] = T_CRIT_95 * summary['std'] / np.sqrt(summary['n'])
    summary['ci_lower'] = summary['mean'] - summary['ci_half_width']
    summary['ci_upper'] = summary['mean'] + summary['ci_half_width']
    summary = summary[['scenario', 'kpi', 'mean', 'ci_lower', 'ci_upper', 'std']]
    summary.to_csv('sensitivity/sensitivity_summary.csv', index=False)
    print('Done! Sensitivity outputs saved under sensitivity/.')


if __name__ == '__main__':
    main()
