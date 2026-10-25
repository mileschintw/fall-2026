"""
Checks that analysis.md and my_timing.py have been filled in. These tests cannot
tell whether your answers are GOOD (a person reads those). They only catch
leftover placeholders, deleted markers, and unfinished code.

Run with:  python3 analysis_test.py
"""
import os
import re
import unittest

import my_timing

HERE = os.path.dirname(os.path.abspath(__file__))
EXPECTED_ANSWERS = 15          # A1-A4, P1-P3, T1, Q1-Q7
MIN_CHARACTERS = 30


def read_analysis():
    with open(os.path.join(HERE, 'analysis.md'), encoding='utf-8') as file:
        return file.read()


class AnalysisTests(unittest.TestCase):
    def test_every_question_has_an_answer(self):
        text = read_analysis()
        answers = re.findall(r'^ANSWER:(.*?)(?=^ANSWER:|^#|\Z)', text, re.S | re.M)
        self.assertEqual(EXPECTED_ANSWERS, len(answers),
                         'expected %d "ANSWER:" markers but found %d. Did you delete or rename one?'
                         % (EXPECTED_ANSWERS, len(answers)))
        for number, answer in enumerate(answers, start=1):
            self.assertNotIn('replace this', answer.lower(),
                             'answer %d still has the placeholder text' % number)
            self.assertGreaterEqual(len(answer.strip()), MIN_CHARACTERS,
                                    'answer %d is empty or very short' % number)

    def test_the_timing_results_have_been_pasted(self):
        text = read_analysis()
        match = re.search(r'### Your results.*?```text\n(.*?)```', text, re.S)
        self.assertIsNotNone(match, 'could not find the results block under "### Your results"')
        results = match.group(1)
        self.assertNotIn('(paste here)', results, 'paste the output of timing.py into the block')
        self.assertIn('microseconds', results, 'this does not look like the output of timing.py')


class MyTimingTests(unittest.TestCase):
    def test_the_stopwatch_function_times_a_real_insert(self):
        microseconds = my_timing.stopwatch_microseconds(10_000)
        # Shifting 10,000 values takes far longer than this; an unfinished TODO takes about 0.2
        self.assertGreater(microseconds, 20, 'did you finish the TODO in stopwatch_microseconds?')

    def test_the_timeit_function_times_a_real_insert(self):
        microseconds = my_timing.timeit_microseconds(10_000)
        self.assertGreater(microseconds, 20, 'did you finish the TODO in timeit_microseconds?')


if __name__ == '__main__':
    unittest.main()
