"""Run the help desk on 20 simulated days.  Run:  python3 scenarios.py

Each day is 8 hours (480 minutes) of random tickets from helpdesk_tools.make_tickets, about 100 a day,
with the same 20 days every time. Each row runs all 20 days with a number of agents and an aging
rule (see helpdesk_tools.aging_escalations):
    none      priorities never change
    every 60  a waiting ticket moves up one level for every 60 minutes it has waited
    every 30  the same, every 30 minutes

For each priority (by the priority a ticket ARRIVED with) it prints the average wait and, in
brackets, the longest wait on any of the 20 days, in minutes. Copy the table into ANALYSIS.md.
You do not need to edit this file.
"""
from helpdesk_sim import simulate
from helpdesk_tools import make_tickets, aging_escalations, waits

DAYS = range(590, 610)
ROWS = [(2, None), (2, 60), (2, 30), (3, None), (3, 60), (3, 30)]


def run(num_agents, every):
    by_priority = {1: [], 2: [], 3: []}
    for seed in DAYS:
        day = make_tickets(seed)
        escalations = aging_escalations(day, every) if every else ()
        w = waits(day, simulate(day, num_agents, escalations))
        for t in day:
            by_priority[t['priority']].append(w[t['id']])
    return by_priority


def main():
    print('| agents | aging | priority 1 wait | priority 2 wait | priority 3 wait |')
    print('| --- | --- | --- | --- | --- |')
    for num_agents, every in ROWS:
        result = run(num_agents, every)
        cells = ['%.1f (%d)' % (sum(w) / len(w), max(w)) for w in (result[1], result[2], result[3])]
        print('| %d | %s | %s |' % (num_agents, 'every %d' % every if every else 'none', ' | '.join(cells)))
    tickets = sum(len(make_tickets(seed)) for seed in DAYS)
    print()
    print('%d tickets over %d days.' % (tickets, len(DAYS)))


if __name__ == '__main__':
    main()
