from cone.app.model import BaseNode
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.zodb import testing
from cone.zodb import zodb_entry_for
from cone.zodb import ZODBEntry
from cone.zodb import ZODBEntryNode
from cone.zodb.interfaces import IZODBEntry
from cone.zodb.interfaces import IZODBEntryNode
from cone.zodb.testing import ZODBDummyNode
from node.ext.zodb import OOBTNodeAttributes
from node.interfaces import IOrder
from node.interfaces import IOrdered
from node.interfaces import IUUIDAware
from node.tests import NodeTestCase
from node.utils import LocationIterator
import transaction
import uuid


class TestEntry(NodeTestCase):
    layer = testing.zodb_layer

    def test_entry(self):
        self.layer.new_request()

        # Create node containing ZODBEntry
        root = BaseNode(name='root')
        root['myentry'] = ZODBEntry()
        entry = root['myentry']
        self.assertTrue(isinstance(entry, ZODBEntry))

        # ZODB entry node of entry is looked up by db_name from db root
        self.assertTrue(isinstance(entry.storage, ZODBEntryNode))
        self.assertEqual(entry.storage.name, 'myentry')

        # storage, entry and parents
        self.assertTrue(entry.storage._v_parent is entry)
        self.assertTrue(entry.storage.entry is entry)

        self.assertTrue(entry.storage._v_parent.parent is root)
        self.assertTrue(entry.storage.__parent__ is root)
        self.assertTrue(entry.storage.parent is root)

        # ``metadata`` and ``properties`` are returned from entry
        self.assertTrue(isinstance(entry.storage.metadata, Metadata))
        self.assertTrue(isinstance(entry.storage.properties, Properties))

        self.assertTrue(entry.storage.metadata is entry.metadata)
        self.assertTrue(entry.storage.properties is entry.properties)

        # ``attrs`` are returned from storage
        self.assertTrue(isinstance(entry.storage.attrs, OOBTNodeAttributes))
        self.assertTrue(entry.attrs is entry.storage.attrs)
        self.assertTrue(entry.attrs.parent is entry.storage)

        # Create children
        foo = ZODBDummyNode()
        entry['foo'] = foo
        bar = ZODBDummyNode()
        bar.attrs['title'] = 'bar'
        entry['bar'] = bar

        # ``__iter__``
        self.assertEqual([k for k in entry], ['foo', 'bar'])

        # ``__getitem__``
        self.assertTrue(entry['foo'] is foo)

        # ``keys``
        self.assertEqual(foo.attrs.keys(), ['title', 'uuid'])

        # ``__parent__``
        self.assertTrue(foo.parent is entry)
        self.assertTrue(foo.parent.parent is root)

        # IZODBEntry and IZODBEntryNode
        self.assertTrue(IZODBEntry.providedBy(entry))
        self.assertTrue(IZODBEntryNode.providedBy(entry.storage))

        # ZODBDummyNode is UUIDAware
        self.assertTrue(IUUIDAware.providedBy(foo))
        self.assertTrue(isinstance(foo.uuid, uuid.UUID))

        # Entry and entry node result in the same tree
        self.checkOutput("""
        <class 'cone.zodb.entry.ZODBEntry'>: myentry
          <class 'cone.zodb.testing.ZODBDummyNode'>: foo
          <class 'cone.zodb.testing.ZODBDummyNode'>: bar
        """, entry.treerepr())

        self.checkOutput("""
        <class 'cone.zodb.entry.ZODBEntryNode'>: myentry
          <class 'cone.zodb.testing.ZODBDummyNode'>: foo
          <class 'cone.zodb.testing.ZODBDummyNode'>: bar
        """, entry.storage.treerepr())

        # IOrdered and IOrder
        self.assertTrue(IOrdered.providedBy(entry))
        self.assertTrue(IOrder.providedBy(entry))

        # first_key
        self.assertEqual(entry.first_key, 'foo')

        # last_key
        self.assertEqual(entry.last_key, 'bar')

        # next_key
        self.assertEqual(entry.next_key('foo'), 'bar')

        # prev_key
        self.assertEqual(entry.prev_key('bar'), 'foo')

        # swap
        entry.swap(entry['foo'], entry['bar'])
        self.assertEqual(entry.keys(), ['bar', 'foo'])

        # insertbefore
        foo = entry.detach('foo')
        entry.insertbefore(foo, entry['bar'])
        self.assertEqual(entry.keys(), ['foo', 'bar'])

        # insertafter
        foo = entry.detach('foo')
        entry.insertafter(foo, entry['bar'])
        self.assertEqual(entry.keys(), ['bar', 'foo'])

        # insertfirst
        foo = entry.detach('foo')
        entry.insertfirst(foo)
        self.assertEqual(entry.keys(), ['foo', 'bar'])

        # insertlast
        foo = entry.detach('foo')
        entry.insertlast(foo)
        self.assertEqual(entry.keys(), ['bar', 'foo'])

        # movebefore
        entry.movebefore('foo', 'bar')
        self.assertEqual(entry.keys(), ['foo', 'bar'])

        # moveafter
        entry.moveafter('foo', 'bar')
        self.assertEqual(entry.keys(), ['bar', 'foo'])

        # movefirst
        entry.movefirst('foo')
        self.assertEqual(entry.keys(), ['foo', 'bar'])

        # movelast
        entry.movelast('foo')
        self.assertEqual(entry.keys(), ['bar', 'foo'])

        # ``__delitem__``
        del entry['foo']
        self.checkOutput("""
        <class 'cone.zodb.entry.ZODBEntry'>: myentry
          <class 'cone.zodb.testing.ZODBDummyNode'>: bar
        """, entry.treerepr())

        # ``__call__`` delegates to storage, which is the ZODB entry node
        entry()

        # ``zodb_entry_for``
        self.assertTrue(zodb_entry_for(entry) is entry)
        self.assertTrue(zodb_entry_for(entry.storage) is entry)
        self.assertTrue(zodb_entry_for(bar) is entry)
        self.assertTrue(zodb_entry_for(root) is None)

        # LocationIterator
        self.assertEqual([_ for _ in LocationIterator(bar)], [bar, entry, root])
        self.assertEqual([_ for _ in LocationIterator(entry)], [entry, root])

        # DB name
        class CustomZODBEntry(ZODBEntry):
            @property
            def db_name(self):
                return 'custom_entry_storage'

            @property
            def name(self):
                return 'entry_storage'

        root['custom_entry_storage'] = CustomZODBEntry(name='custom_entry')
        entry = root['custom_entry_storage']
        self.assertEqual(entry.name, 'entry_storage')

        child = ZODBDummyNode()
        entry['child'] = child
        child = entry['child']
        self.assertEqual(child.path, ['root', 'entry_storage', 'child'])
        self.assertEqual(entry.db_name, 'custom_entry_storage')

        transaction.commit()
