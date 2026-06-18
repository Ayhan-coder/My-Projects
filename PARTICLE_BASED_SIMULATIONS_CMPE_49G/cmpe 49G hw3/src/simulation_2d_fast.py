"""Fast 2D molecular diffusion with reflection (vectorized)."""

from __future__ import annotations

import numpy as np


class Simulation2D_Fast:
    """Fast 2D molecular diffusion with reflection - optimized version."""

    def __init__(self, sim_params: dict):
        rx_center = np.asarray(sim_params["rx_center"], dtype=np.float32)
        self.rx_center = rx_center[:2]

        self.rx_r = np.float32(sim_params["rx_r_inMicroMeters"])

        tx_pt = np.asarray(sim_params["tx_emission_pt"], dtype=np.float32)
        self.tx_pt = tx_pt[:2]

        self.D = np.float32(sim_params["D_inMicroMeterSqrPerSecond"])
        self.delta_t = np.float32(sim_params["delta_t"])
        self.tend = float(sim_params["tend"])
        self.num_molecules = int(sim_params["num_molecules"])

        self.line_x_int = np.float32(sim_params["reflecting_line_x_intercept"])
        self.line_y_int = np.float32(sim_params["reflecting_line_y_intercept"])

        self.steps = int(self.tend / float(self.delta_t)) + 1
        self.time_axis = np.linspace(0, self.tend, self.steps)

        self.sigma = np.sqrt(2 * self.D * self.delta_t).astype(np.float32)

        self.absorbed_count = np.zeros(self.steps, dtype=np.int32)
        self.reflection_count = 0

        self._seed = sim_params.get("seed", None)
        self._max_reflect_iter = int(sim_params.get("max_reflect_iter", 5))

        self._active_positions: np.ndarray | None = None

    def run(self):
        """Execute simulation (vectorized over active molecules)."""
        rng = np.random.default_rng(self._seed)

        # Keep only active molecule positions (compacted) to avoid per-step np.where.
        self._active_positions = np.tile(self.tx_pt, (self.num_molecules, 1)).astype(
            np.float32, copy=False
        )

        # Line reflection parameters: line equation ax + by + c = 0.
        # From intercepts: y = mx + b where b = y_int, m = -y_int / x_int.
        # Standard form: mx - y + b = 0 => a=m, b=-1, c=b
        y_int = float(self.line_y_int)
        x_int = float(self.line_x_int)
        m = -y_int / x_int
        a = m
        b_coeff = -1.0
        c = y_int

        denom = a * a + b_coeff * b_coeff
        two_a_over_denom = 2.0 * a / denom
        two_b_over_denom = 2.0 * b_coeff / denom

        # Determine correct side using TX location (sign of ax+by+c).
        tx_signed = a * float(self.tx_pt[0]) + b_coeff * float(self.tx_pt[1]) + c
        if tx_signed == 0:
            tx_signed = 1.0

        rx_r_sq = float(self.rx_r) ** 2
        sigma = float(self.sigma)

        absorbed_total = 0

        for step in range(1, self.steps):
            pos = self._active_positions
            if pos.size == 0:
                break

            # Brownian motion (float32 RNG for speed/memory).
            pos += rng.standard_normal(size=pos.shape, dtype=np.float32) * sigma

            # Reflection (iterate to handle multi-crossings in one time step).
            for _ in range(self._max_reflect_iter):
                numerator = a * pos[:, 0] + b_coeff * pos[:, 1] + c
                needs_reflect = (numerator * tx_signed) < 0
                if not np.any(needs_reflect):
                    break

                self.reflection_count += int(np.count_nonzero(needs_reflect))
                n = numerator[needs_reflect]
                pos[needs_reflect, 0] -= two_a_over_denom * n
                pos[needs_reflect, 1] -= two_b_over_denom * n

            # Absorption check.
            dx = pos[:, 0] - float(self.rx_center[0])
            dy = pos[:, 1] - float(self.rx_center[1])
            dist_sq = dx * dx + dy * dy
            absorbed_mask = dist_sq < rx_r_sq
            if np.any(absorbed_mask):
                absorbed_now = int(np.count_nonzero(absorbed_mask))
                absorbed_total += absorbed_now
                pos = pos[~absorbed_mask]
                self._active_positions = pos

            self.absorbed_count[step] = absorbed_total

        return self.absorbed_count, self.time_axis

    def get_results(self):
        cumulative = self.absorbed_count.astype(int, copy=True)
        instantaneous = np.diff(cumulative, prepend=0)

        return {
            "time": self.time_axis,
            "cumulative": cumulative,
            "instantaneous": instantaneous,
            "num_molecules": self.num_molecules,
            "reflection_count": int(self.reflection_count),
        }
