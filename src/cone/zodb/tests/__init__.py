import sys
import unittest


def test_suite():
    from cone.zodb.tests import test_common
    from cone.zodb.tests import test_entry
    from cone.zodb.tests import test_indexing
    from cone.zodb.tests import test_catalog

    suite = unittest.TestSuite()

    suite.addTest(unittest.findTestCases(test_common))
    suite.addTest(unittest.findTestCases(test_entry))
    suite.addTest(unittest.findTestCases(test_indexing))
    suite.addTest(unittest.findTestCases(test_catalog))

    return suite


def run_tests():
    from zope.testrunner.runner import Runner

    runner = Runner(found_suites=[test_suite()])
    runner.run()
    sys.exit(int(runner.failed))


if __name__ == '__main__':
    run_tests()
