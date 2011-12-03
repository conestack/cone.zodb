import uuid
import doctest
import interlude
import pprint
import unittest2 as unittest
from cone.zodb.testing import ZODBLayer
from plone.testing import layered


optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE


TESTFILES = [
    'common.rst',
    'entry.rst',
    'indexing.rst',
    'catalog.rst',
]


layer = ZODBLayer()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                testfile,
                globs={'interact': interlude.interact,
                       'pprint': pprint.pprint,
                       'pp': pprint.pprint,
                       },
                optionflags=optionflags,
                ), layer)
        for testfile in TESTFILES
        ])
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')                 #pragma NO COVERAGE