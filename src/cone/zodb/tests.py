import uuid
import doctest
import interlude
import pprint
import unittest2 as unittest
from plumber import plumber
from node.ext.zodb import OOBTNode
from cone.app.testing import security
from cone.zodb import CatalogAware
from plone.testing import layered

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE


class DummyZODBNode(OOBTNode):
    node_info_name = 'dummytype'
    def __init__(self, name=None, parent=None):
        OOBTNode.__init__(self, name=name, parent=parent)
        self.attrs['uid'] = uuid.uuid4()
        self.attrs['title'] = 'foo'
        self.state = 'state_1'


class CatalogAwareDummyNode(DummyZODBNode):
    __metaclass__ = plumber
    __plumbing__ = CatalogAware


TESTFILES = [
    'README.rst',
]

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
                ), security)
        for testfile in TESTFILES
        ])
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')                 #pragma NO COVERAGE