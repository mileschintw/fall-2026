"""Tests for Part 2. They use YOUR priority queue, so get Part 1 passing first.
Run them with:  python3 -m unittest helpdesk_sim_test -v
"""
import unittest

from helpdesk_sim import simulate
from helpdesk_tools import make_ticket, make_tickets, aging_escalations, waits


def tickets(*rows):
    """rows are (arrive, priority, duration); ids are 0, 1, 2, ... in the order given."""
    return [make_ticket(i, a, p, d) for i, (a, p, d) in enumerate(rows)]


class OneAgentTest(unittest.TestCase):
    def test_no_tickets(self):
        self.assertEqual(simulate([], 2), [])

    def test_equal_priorities_first_come_first_served(self):
        t = tickets((0, 2, 5), (0, 2, 3), (0, 2, 4))
        self.assertEqual(simulate(t, 1), [(0, 0, 0), (1, 5, 0), (2, 8, 0)])

    def test_the_most_urgent_waiting_ticket_goes_next(self):
        t = tickets((0, 3, 10), (1, 2, 1), (2, 1, 2))
        self.assertEqual(simulate(t, 1), [(0, 0, 0), (2, 10, 0), (1, 12, 0)])

    def test_an_agent_is_free_again_exactly_when_the_ticket_is_done(self):
        t = tickets((0, 1, 4), (4, 1, 1))
        self.assertEqual(simulate(t, 1), [(0, 0, 0), (1, 4, 0)])

    def test_an_idle_desk_waits_for_the_next_ticket(self):
        t = tickets((20, 3, 2), (21, 3, 2), (40, 1, 1))
        self.assertEqual(simulate(t, 1), [(0, 20, 0), (1, 22, 0), (2, 40, 0)])


class AgentsTest(unittest.TestCase):
    def test_free_agents_take_tickets_in_number_order(self):
        t = tickets((0, 2, 6), (0, 2, 3), (0, 2, 5), (0, 2, 1))
        self.assertEqual(simulate(t, 2), [(0, 0, 0), (1, 0, 1), (2, 3, 1), (3, 6, 0)])

    def test_one_ticket_three_agents(self):
        self.assertEqual(simulate(tickets((7, 2, 3)), 3), [(0, 7, 0)])

    def test_agent_zero_gets_the_most_urgent(self):
        t = tickets((0, 2, 4), (0, 2, 4), (1, 3, 1), (2, 1, 1))
        self.assertEqual(simulate(t, 2), [(0, 0, 0), (1, 0, 1), (3, 4, 0), (2, 4, 1)])

    def test_a_ticket_arriving_while_everyone_is_busy(self):
        t = tickets((0, 1, 5), (0, 1, 9), (1, 2, 1), (2, 1, 2))
        self.assertEqual(simulate(t, 2), [(0, 0, 0), (1, 0, 1), (3, 5, 0), (2, 7, 0)])


class EscalationTest(unittest.TestCase):
    def test_an_escalated_ticket_jumps_ahead(self):
        t = tickets((0, 1, 10), (1, 2, 1), (2, 3, 1))
        self.assertEqual(simulate(t, 1, [(5, 2, 1)]), [(0, 0, 0), (2, 10, 0), (1, 11, 0)])

    def test_an_escalation_in_the_minute_a_ticket_arrives_counts(self):
        t = tickets((0, 1, 10), (1, 2, 1), (5, 3, 1))
        self.assertEqual(simulate(t, 1, [(5, 2, 1)]), [(0, 0, 0), (2, 10, 0), (1, 11, 0)])

    def test_escalations_for_tickets_not_waiting_are_ignored(self):
        t = tickets((0, 1, 10), (1, 2, 1), (20, 3, 1))
        escalations = [(3, 0, 3), (5, 2, 1), (12, 1, 1)]   # already started, not arrived yet, already started
        self.assertEqual(simulate(t, 1, escalations), [(0, 0, 0), (1, 10, 0), (2, 20, 0)])

    def test_a_ticket_can_be_made_less_urgent(self):
        t = tickets((0, 1, 10), (1, 1, 1), (2, 2, 1))
        self.assertEqual(simulate(t, 1, [(9, 1, 3)]), [(0, 0, 0), (2, 10, 0), (1, 11, 0)])


class OneDayTest(unittest.TestCase):
    """A seeded day of 93 tickets with two agents (the scenario from scenarios.py)."""

    def check(self, escalations, expected_by_priority):
        day = make_tickets(590)
        records = simulate(day, 2, escalations)
        self.assertEqual(sorted(r[0] for r in records), [t['id'] for t in day], 'every ticket starts exactly once')
        starts = [r[1] for r in records]
        self.assertEqual(starts, sorted(starts), 'records should be in the order the tickets started')
        w = waits(day, records)
        by_priority = [sum(w[t['id']] for t in day if t['priority'] == p) for p in (1, 2, 3)]
        self.assertEqual(by_priority, expected_by_priority, 'total minutes waited by priority 1, 2 and 3')

    def test_one_day(self):
        self.check((), [37, 126, 926])

    def test_one_day_with_aging(self):
        self.check(aging_escalations(make_tickets(590)), [39, 337, 696])
