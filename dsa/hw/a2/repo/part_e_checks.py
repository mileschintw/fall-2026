"""
Checks that your Part E tests (student_tests.py) are real tests. The autograder
runs these; you can run them too:  python3 -m unittest part_e_checks

They do NOT judge whether your test is clever -- a person does that. They only
catch the cases where a test is missing, still has its placeholder name, fails,
or never touches your code.
"""
import ast
import inspect
import textwrap
import unittest

import student_tests

PLACEHOLDER = 'test_replace_this_name'


def check_student_class(testcase, cls, name_part):
    names = [n for n in dir(cls) if n.startswith('test_')]
    testcase.assertTrue(names, '%s has no tests yet. Write one.' % cls.__name__)
    testcase.assertNotIn(PLACEHOLDER, names,
                         'Rename %s in %s so its name says what the test checks.'
                         % (PLACEHOLDER, cls.__name__))

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(cls)
    result = unittest.TestResult()
    suite.run(result)
    problems = result.failures + result.errors
    testcase.assertEqual([], [str(t) for t, _ in problems],
                         'These tests in %s do not pass yet.' % cls.__name__)

    uses_your_code = False
    has_a_check = False
    for n in names:
        source = textwrap.dedent(inspect.getsource(getattr(cls, n)))
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Name) and name_part in node.id:
                uses_your_code = True
            if isinstance(node, ast.Attribute) and node.attr.startswith('assert'):
                has_a_check = True
    testcase.assertTrue(uses_your_code,
                        'No test in %s calls any %s function.' % (cls.__name__, name_part))
    testcase.assertTrue(has_a_check,
                        'No test in %s checks anything (use self.assertEqual and friends).'
                        % cls.__name__)


class PartEChecks(unittest.TestCase):
    def test_my_array_list_test(self):
        check_student_class(self, student_tests.MyArrayListTests, 'array_list')

    def test_my_linked_list_test(self):
        check_student_class(self, student_tests.MyLinkedListTests, 'linked_list')


if __name__ == '__main__':
    unittest.main()
