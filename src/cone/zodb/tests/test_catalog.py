from BTrees.IFBTree import IFSet
from cone.app.model import BaseNode
from cone.zodb import CatalogProxy
from cone.zodb import testing
from cone.zodb.catalog import CatalogIndexer
from cone.zodb.indexing import create_default_catalog
from cone.zodb.indexing import create_default_metadata
from cone.zodb.testing import CatalogAwareZODBEntry
from cone.zodb.testing import CatalogAwareZODBNode
from cone.zodb.testing import CatalogIncludedZODBEntry
from node.tests import NodeTestCase
from persistent import Persistent
from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.path import CatalogPathIndex
from repoze.catalog.query import Eq
import transaction


class TestCatalog(NodeTestCase):
    layer = testing.zodb_layer

    def test_catalog(self):
        # Create calatog aware ZODB entry
        self.layer.new_request()

        root = BaseNode(name='root')
        entry = root['catalog_aware'] = CatalogAwareZODBEntry()
        catalog = entry.catalog_proxies['default'].catalog

        self.assertTrue(isinstance(catalog, Catalog))
        self.assertEqual(
            sorted(catalog.keys()),
            ['app_path', 'path', 'state', 'title', 'type', 'uid']
        )
        self.assertTrue(isinstance(catalog['app_path'], CatalogPathIndex))
        self.assertTrue(isinstance(catalog['path'], CatalogPathIndex))
        self.assertTrue(isinstance(catalog['state'], CatalogFieldIndex))
        self.assertTrue(isinstance(catalog['title'], CatalogFieldIndex))
        self.assertTrue(isinstance(catalog['type'], CatalogFieldIndex))
        self.assertTrue(isinstance(catalog['uid'], CatalogFieldIndex))

        # Empty node. not added yet
        foo = CatalogAwareZODBNode()
        uid = foo.uuid
        res = entry.catalog_proxies['default'].catalog.query(Eq('uid', uid))
        self.assertEqual(res[0], 0)
        self.assertTrue(isinstance(res[1], IFSet))
        self.assertEqual(len(res[1]), 0)

        # Add nodes and query catalog
        bar = CatalogAwareZODBNode()
        bar.attrs['title'] = 'bar'

        entry['foo'] = foo
        entry['bar'] = bar

        res = entry.catalog_proxies['default'].catalog.query(Eq('uid', uid))
        self.assertEqual(res[0], 1)
        self.assertEqual(len(res[1]), 1)

        # Check path index
        res = entry.catalog_proxies['default'].catalog.query(
            Eq('path', {'query': '/catalog_aware', 'level': 0})
        )
        self.assertEqual(res[0], 2)
        self.assertEqual(len(res[1]), 2)

        res = entry.catalog_proxies['default'].catalog.query(
            Eq('app_path', {'query': 'root'})
        )
        self.assertEqual(res[0], 2)
        self.assertEqual(len(res[1]), 2)

        # Check metadata
        self.assertEqual(
            sorted(entry.catalog_proxies['default'].doc_metadata(uid).items()),
            [
                ('app_path', ['root', 'catalog_aware', 'foo']),
                ('combined_title', 'catalog_aware - foo'),
                ('path', ['catalog_aware', 'foo']),
                ('title', 'foo'),
                ('uid', uid)]
        )

        # Reindexing happens at ``__call__`` time
        foo.attrs['title'] = 'foo changed'
        foo()
        self.assertEqual(
            sorted(entry.catalog_proxies['default'].doc_metadata(str(uid)).items()),
            [
                ('app_path', ['root', 'catalog_aware', 'foo']),
                ('combined_title', 'catalog_aware - foo changed'),
                ('path', ['catalog_aware', 'foo']),
                ('title', 'foo changed'),
                ('uid', uid)
            ]
        )

        # Calling the ZODB entry delegates to refering ZODB entry node
        entry()

        # Create child for 'bar'
        child = CatalogAwareZODBNode()
        bar['child'] = child
        child.attrs['title'] = 'Child of bar'
        child()

        self.checkOutput("""
        <class 'cone.zodb.testing.CatalogAwareZODBEntry'>: catalog_aware
          <class 'cone.zodb.testing.CatalogAwareZODBNode'>: foo
          <class 'cone.zodb.testing.CatalogAwareZODBNode'>: bar
            <class 'cone.zodb.testing.CatalogAwareZODBNode'>: child
        """, entry.treerepr())

        bar_uid = bar.uuid
        res = entry.catalog_proxies['default'].catalog.query(Eq('uid', bar_uid))
        self.assertEqual(res[0], 1)
        self.assertEqual(len(res[1]), 1)

        child_uid = child.uuid
        res = entry.catalog_proxies['default'].catalog.query(Eq('uid', child_uid))
        self.assertEqual(res[0], 1)
        self.assertEqual(len(res[1]), 1)

        # Rebuild catalog
        self.assertEqual(
            entry.catalog_proxies['default'].rebuild_catalog(),
            3
        )

        res = entry.catalog_proxies['default'].catalog.query(Eq('type', 'dummytype'))
        self.assertEqual(res[0], 3)
        self.assertEqual(len(res[1]), 3)

        # Delete node. Gets unindexed recursive.
        del entry['bar']

        self.checkOutput("""
        <class 'cone.zodb.testing.CatalogAwareZODBEntry'>: catalog_aware
          <class 'cone.zodb.testing.CatalogAwareZODBNode'>: foo
        """, entry.treerepr())

        res = entry.catalog_proxies['default'].catalog.query(Eq('uid', bar_uid))
        self.assertEqual(res[0], 0)
        self.assertEqual(len(res[1]), 0)

        res = entry.catalog_proxies['default'].catalog.query(Eq('uid', child_uid))
        self.assertEqual(res[0], 0)
        self.assertEqual(len(res[1]), 0)

        res = entry.catalog_proxies['default'].catalog.query(Eq('type', 'dummytype'))
        self.assertEqual(res[0], 1)
        self.assertEqual(len(res[1]), 1)

        self.assertEqual(
            entry.catalog_proxies['default'].rebuild_catalog(),
            1
        )

        # Test moving of subtrees, if objects get indexed the right way
        source = entry['source'] = CatalogAwareZODBNode()
        source['c1'] = CatalogAwareZODBNode()
        source['c2'] = CatalogAwareZODBNode()
        entry['target'] = CatalogAwareZODBNode()
        self.checkOutput("""
        <class 'cone.zodb.testing.CatalogAwareZODBEntry'>: catalog_aware
          <class 'cone.zodb.testing.CatalogAwareZODBNode'>: foo
          <class 'cone.zodb.testing.CatalogAwareZODBNode'>: source
            <class 'cone.zodb.testing.CatalogAwareZODBNode'>: c1
            <class 'cone.zodb.testing.CatalogAwareZODBNode'>: c2
          <class 'cone.zodb.testing.CatalogAwareZODBNode'>: target
        """, entry.treerepr())

        uid = source['c1'].uuid
        self.assertEqual(
            sorted(entry.catalog_proxies['default'].doc_metadata(str(uid)).items()),
            [
                ('app_path', ['root', 'catalog_aware', 'source', 'c1']),
                ('combined_title', 'catalog_aware - foo - foo'),
                ('path', ['catalog_aware', 'source', 'c1']),
                ('title', 'foo'),
                ('uid', uid)
            ]
        )

        to_move = entry.detach('source')
        target = entry['target']
        target[to_move.name] = to_move
        uid = target['source']['c1'].uuid
        self.assertEqual(
            sorted(entry.catalog_proxies['default'].doc_metadata(str(uid)).items()),
            [
                ('app_path', ['root', 'catalog_aware', 'target', 'source', 'c1']),
                ('combined_title', 'catalog_aware - foo - foo - foo'),
                ('path', ['catalog_aware', 'target', 'source', 'c1']),
                ('title', 'foo'),
                ('uid', uid)
            ]
        )

        self.checkOutput("""
        <class 'cone.zodb.testing.CatalogAwareZODBEntry'>: catalog_aware
          <class 'cone.zodb.testing.CatalogAwareZODBNode'>: foo
          <class 'cone.zodb.testing.CatalogAwareZODBNode'>: target
            <class 'cone.zodb.testing.CatalogAwareZODBNode'>: source
              <class 'cone.zodb.testing.CatalogAwareZODBNode'>: c1
              <class 'cone.zodb.testing.CatalogAwareZODBNode'>: c2
        """, entry.treerepr())

        res = entry.catalog_proxies['default'].catalog.query(
            Eq('path', {'query': '/catalog_aware/target'})
        )
        self.assertEqual(res[0], 4)
        self.assertEqual(len(res[1]), 4)

        res = entry.catalog_proxies['default'].catalog.query(
            Eq('path', {'query': '/catalog_aware/target/source'})
        )
        self.assertEqual(res[0], 3)
        self.assertEqual(len(res[1]), 3)

        # Test CatalogIndexer
        indexer = entry.catalog_indexer
        self.assertTrue(isinstance(indexer, CatalogIndexer))

        foo = entry['foo']
        indexer.unindex_doc(foo)

        res = entry.catalog_proxies['default'].catalog.query(Eq('uid', foo.uuid))
        self.assertEqual(res[0], 0)
        self.assertEqual(len(res[1]), 0)

        indexer.index_doc(foo)
        res = entry.catalog_proxies['default'].catalog.query(Eq('uid', foo.uuid))
        self.assertEqual(res[0], 1)
        self.assertEqual(len(res[1]), 1)

        target = entry['target']
        indexer.unindex_recursiv(target)
        res = entry.catalog_proxies['default'].catalog.query(
            Eq('path', {'query': '/catalog_aware'})
        )
        self.assertEqual(res[0], 1)
        self.assertEqual(len(res[1]), 1)

        indexer.index_recursiv(target)
        res = entry.catalog_proxies['default'].catalog.query(
            Eq('path', {'query': '/catalog_aware'})
        )
        self.assertEqual(res[0], 5)
        self.assertEqual(len(res[1]), 5)

        # Test pointing CatalogProxy to existing objects providing the wrong
        # interface
        db_root = self.layer.zodb_root()
        db_root['invalid_catalog_object'] = Persistent()
        db_root['invalid_doc_map_object'] = Persistent()

        proxy = CatalogProxy(
            entry['foo'],
            entry,
            'invalid_catalog_object',
            'invalid_doc_map_object',
            create_default_catalog,
            create_default_metadata
        )

        err = self.expectError(
            ValueError,
            lambda: proxy.catalog
        )
        expected = 'ICatalog not provided by invalid_catalog_object'
        self.assertEqual(str(err), expected)

        err = self.expectError(
            ValueError,
            lambda: proxy.doc_map
        )
        expected = 'invalid_catalog_object not a DocumentMap instance'
        self.assertEqual(str(err), expected)

        entry = root['catalog_included'] = CatalogIncludedZODBEntry()
        entry.attrs['title'] = 'Calatog Included'
        uid = entry.storage.uuid
        res = entry.catalog_proxies['default'].catalog.query(Eq('uid', uid))
        self.assertEqual(res[0], 1)
        self.assertEqual(len(res[1]), 1)

        self.assertEqual([
            ('app_path', ['root', 'catalog_included']),
            ('combined_title', 'catalog_included'),
            ('path', ['catalog_included']),
            ('title', 'catalog_included'),
            ('uid', uid)
        ], list(entry.catalog_proxies['default'].doc_metadata(str(uid)).items()))

        # Re-init ZODB connection
        transaction.commit()
        self.layer.init_zodb()
