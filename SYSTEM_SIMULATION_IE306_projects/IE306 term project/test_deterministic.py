import unittest

from ferry_simulation import Passenger, Simulation


class TestDeterministicVerify(unittest.TestCase):
    def test_single_ferry_trip(self):
        """Deterministic smoke test for a single A1 -> E1 passenger."""
        scenario = {
            'shuttle': False,
            'lodos': False,
            'hw_multiplier': 1.0,
            'base_seed': 42,
        }

        sim = Simulation('S1_test', 1, scenario, {}, {})
        passenger = Passenger(
            id=999,
            origin='A1',
            destination='E1',
            arrival_time=8000,
            route=['E1'],
            turnstile_time=0.0,
            board_time_1=0.0,
        )

        def mock_generate_dyn_arrivals(origin, destinations, is_historical):
            if origin == 'A1':
                yield sim.env.timeout(8000)
                sim.all_passengers.append(passenger)
                sim.env.process(
                    sim.passenger_process(
                        passenger,
                        sim.terminals['A1'],
                        arrival_time=passenger.arrival_time,
                    )
                )
            yield sim.env.timeout(999999)

        sim.generate_dyn_arrivals = mock_generate_dyn_arrivals

        sim.run()

        self.assertIsNotNone(passenger.board_time)
        self.assertIsNotNone(passenger.disembark_time)
        self.assertEqual(passenger.destination, 'E1')
        self.assertFalse(passenger.balked)
        self.assertGreaterEqual(passenger.board_time, passenger.arrival_time)
        self.assertGreater(passenger.disembark_time, passenger.board_time)


if __name__ == '__main__':
    unittest.main()
