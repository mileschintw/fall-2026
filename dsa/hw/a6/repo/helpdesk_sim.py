"""Part 2: a help desk simulation.

Tickets (dicts, see helpdesk_tools.py) arrive at a help desk with a few agents. Waiting tickets
sit in YOUR priority queue from priority_queue.py, keyed by ticket id, and a free agent always
takes the most urgent one. See the README for the exact rules, minute by minute.
"""
from priority_queue import (create_pq, pq_insert, pq_remove_min, pq_contains,
                            pq_change_priority, pq_is_empty)


def simulate(tickets, num_agents, escalations=()):
    """Run the help desk and return a list of records, one per ticket, in the order the
    tickets were started: (ticket_id, start_minute, agent_number).

    tickets      a list of ticket dicts, in order of id
    num_agents   how many agents; they are numbered 0, 1, ..., num_agents - 1
    escalations  a list of (minute, ticket_id, new_priority) tuples
    """
    raise NotImplementedError('TODO: simulate')
