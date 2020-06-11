from cone.app.interfaces import IWorkflowState
from cone.app.model import BaseNode
from cone.app.model import Metadata
from cone.zodb import app_path
from cone.zodb import combined_title
from cone.zodb import create_default_catalog
from cone.zodb import create_default_metadata
from cone.zodb import get_state
from cone.zodb import get_title
from cone.zodb import get_type
from cone.zodb import get_uid
from cone.zodb import str_app_path
from cone.zodb import str_zodb_path
from cone.zodb import testing
from cone.zodb import zodb_path
from cone.zodb import ZODBEntry
from cone.zodb.indexing import FLOORDATETIME
from cone.zodb.indexing import force_dt
from cone.zodb.testing import ZODBDummyNode
from datetime import datetime
from node.behaviors import UUIDAware
from node.tests import NodeTestCase
from plumber import plumbing
from zope.interface import alsoProvides
import uuid


class TestIndexing(NodeTestCase):
    layer = testing.zodb_layer

    def test_indexing(self):
        # Helper functions for catalog indexing
        root = BaseNode(name='root')
        entry = root['myentry'] = ZODBEntry()
        foo = entry['foo'] = ZODBDummyNode()
        bar = entry['bar'] = ZODBDummyNode()
        bar.attrs['title'] = 'Bar title'

        # ``path``
        self.assertEqual(foo.path, ['root', 'myentry', 'foo'])

        # ``zodb_path``
        self.assertEqual(zodb_path(entry), ['myentry'])
        self.assertEqual(zodb_path(entry.storage), ['myentry'])
        self.assertEqual(zodb_path(bar), ['myentry', 'bar'])
        self.assertEqual(zodb_path(foo), ['myentry', 'foo'])

        # ``str_zodb_path``
        self.assertEqual(str_zodb_path(bar), '/myentry/bar')
        self.assertEqual(str_zodb_path(foo), '/myentry/foo')

        # ``app_path``
        self.assertEqual(app_path(foo), ['root', 'myentry', 'foo'])

        # ``str_app_path``
        self.assertEqual(str_app_path(foo), '/root/myentry/foo')

        # ``combined_title``
        self.assertEqual(combined_title(bar), 'myentry - Bar title')

        # ``force_dt``
        self.assertEqual(force_dt('foo'), datetime(1980, 1, 1, 0, 0))
        self.assertTrue(FLOORDATETIME == force_dt('foo'))

        self.assertEqual(
            force_dt(datetime(2011, 5, 1)),
            datetime(2011, 5, 1, 0, 0)
        )

        # ``get_uid``
        @plumbing(UUIDAware)
        class UUIDNode(BaseNode):
            pass

        self.assertEqual(get_uid(BaseNode(), 'default'), 'default')
        self.assertTrue(isinstance(get_uid(UUIDNode(), 'default'), uuid.UUID))

        # ``get_type``
        self.assertEqual(get_type(object(), 'default'), 'default')
        self.assertEqual(get_type(foo, 'default'), 'dummytype')

        # ``get_state``
        self.assertEqual(get_state(object(), 'default'), 'default')

        setattr(foo, 'state', 'state_1')
        alsoProvides(foo, IWorkflowState)
        self.assertEqual(get_state(foo, 'default'), 'state_1')

        # ``get_title`` First ``node.metadata``, then ``node.attrs`` are
        # searched for title. finally default takes effect
        self.assertEqual(get_title(foo, 'default'), 'foo')
        self.assertEqual(get_title(BaseNode(), 'default'), u'no_title')

        class NoTitleNode(BaseNode):

            @property
            def metadata(self):
                return Metadata()

        self.assertEqual(get_title(NoTitleNode(), 'default'), 'default')

        # ``create_default_catalog``
        self.assertEqual(
            sorted(create_default_catalog().keys()),
            ['app_path', 'path', 'state', 'title', 'type', 'uid']
        )

        # ``create_default_metadata``
        setattr(bar, 'state', 'some_wf_state')
        alsoProvides(bar, IWorkflowState)
        self.assertEqual(create_default_metadata(bar), {
            'app_path': ['root', 'myentry', 'bar'],
            'uid': bar.uuid,
            'title': 'Bar title',
            'state': 'some_wf_state',
            'combined_title': 'myentry - Bar title',
            'path': ['myentry', 'bar']
        })
