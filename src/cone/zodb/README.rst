Setup environment::

    >>> import os
    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp()
    >>> import ZODB
    >>> from ZODB.FileStorage import FileStorage
    >>> from ZODB.DB import DB
    >>> storage = FileStorage(os.path.join(tempdir, 'Data.fs'))
    >>> db = DB(storage)
    >>> connection = db.open()
    >>> request = layer.new_request()
    >>> request.environ['repoze.zodbconn.connection'] = connection


Create calatog aware ZODB entry::

    >>> from cone.zodb.tests import CatalogAwareDummyNode
    >>> from cone.zodb import CatalogAwareZODBEntry
    >>> entry = root['catalog_aware'] = CatalogAwareZODBEntry()
    >>> entry.catalog
    {'app_path': <repoze.catalog.indexes.path.CatalogPathIndex object at ...>, 
    'uid': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'title': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'state': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'path': <repoze.catalog.indexes.path.CatalogPathIndex object at ...>, 
    'type': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>}
    
    >>> foo = CatalogAwareDummyNode()
    >>> bar = CatalogAwareDummyNode()
    >>> bar.attrs['title'] = 'bar'

Empty. Nodes not added yet::

    >>> uid = foo.attrs['uid']
    >>> from repoze.catalog.query import Eq
    >>> entry.catalog.query(Eq('uid', uid))
    (0, IFSet([]))

Add nodes and query catalog::

    >>> entry['foo'] = foo
    >>> entry['bar'] = bar
    >>> res = entry.catalog.query(Eq('uid', uid))
    >>> res
    (1, IFSet([...]))

Check path index::

    >>> entry.catalog.query(Eq('path', {'query': '/catalog_aware', 'level': 0}))
    (2, IFSet([..., ...]))
    
    >>> entry.catalog.query(Eq('app_path', {'query': 'root'}))
    (2, IFSet([..., ...]))

Check metadata::

    >>> [(k, v) for k, v in entry.doc_metadata(uid).items()]
    [('app_path', ['root', 'catalog_aware', 'foo']), 
    ('combined_title', 'catalog_aware - foo'), 
    ('path', ['catalog_aware', 'foo']), 
    ('state', 'state_1'), 
    ('title', 'foo')]

``zodb_entry_for``::

    >>> from cone.zodb import zodb_entry_for
    >>> zodb_entry_for(root)
    
    >>> zodb_entry_for(bar)
    <CatalogAwareZODBEntry object 'catalog_aware' at ...>

Reindexing happens at ``__call__`` time::

    >>> foo.attrs['title'] = 'foo changed'
    >>> foo()
    >>> [(k, v) for k, v in entry.doc_metadata(str(uid)).items()]
    [('app_path', ['root', 'catalog_aware', 'foo']), 
    ('combined_title', 'catalog_aware - foo changed'), 
    ('path', ['catalog_aware', 'foo']), 
    ('state', 'state_1'), 
    ('title', 'foo changed')]

Calling the ZODB entry delegates to refering ZODB entry node::

    >>> entry()

Create child for 'bar'::

    >>> child = CatalogAwareDummyNode()
    >>> bar['child'] = child
    >>> child.attrs['title'] = 'Child of bar'
    >>> child()
    >>> entry.printtree()
    <class 'cone.zodb.CatalogAwareZODBEntry'>: catalog_aware
      <class 'cone.zodb.tests.CatalogAwareDummyNode'>: foo
      <class 'cone.zodb.tests.CatalogAwareDummyNode'>: bar
        <class 'cone.zodb.tests.CatalogAwareDummyNode'>: child
    
    >>> bar_uid = bar.attrs['uid']
    >>> child_uid = child.attrs['uid']
    >>> entry.catalog.query(Eq('uid', bar_uid))
    (1, IFSet([...]))
    
    >>> entry.catalog.query(Eq('uid', child_uid))
    (1, IFSet([...]))

Rebuild catalog::

    >>> entry.rebuild_catalog()
    3
    
    >>> entry.catalog.query(Eq('type', 'dummytype'))
    (3, IFSet([..., ..., ...]))

Delete node. Gets unindexed recursive.::

    >>> del entry['bar']
    >>> entry.printtree()
    <class 'cone.zodb.CatalogAwareZODBEntry'>: catalog_aware
      <class 'cone.zodb.tests.CatalogAwareDummyNode'>: foo
    
    >>> entry.catalog.query(Eq('uid', bar_uid))
    (0, IFSet([]))
    
    >>> entry.catalog.query(Eq('uid', child_uid))
    (0, IFSet([]))
    
Test moving of subtrees, if objects get indexed the right way::

    >>> source = entry['source'] = CatalogAwareDummyNode()
    >>> source['c1'] = CatalogAwareDummyNode()
    >>> source['c2'] = CatalogAwareDummyNode()
    >>> target = entry['target'] = CatalogAwareDummyNode()
    >>> entry.printtree()
    <class 'cone.zodb.CatalogAwareZODBEntry'>: catalog_aware
      <class 'cone.zodb.tests.CatalogAwareDummyNode'>: foo
      <class 'cone.zodb.tests.CatalogAwareDummyNode'>: source
        <class 'cone.zodb.tests.CatalogAwareDummyNode'>: c1
        <class 'cone.zodb.tests.CatalogAwareDummyNode'>: c2
      <class 'cone.zodb.tests.CatalogAwareDummyNode'>: target
    
    >>> uid = source['c1'].attrs['uid']
    >>> [(k, v) for k, v in entry.doc_metadata(str(uid)).items()]
    [('app_path', ['root', 'catalog_aware', 'source', 'c1']), 
    ('combined_title', 'catalog_aware - foo - foo'), 
    ('path', ['catalog_aware', 'source', 'c1']), 
    ('state', 'state_1'), 
    ('title', 'foo')]
    
    >>> to_move = entry.detach('source')
    >>> target[to_move.name] = to_move
    >>> uid = target['source']['c1'].attrs['uid']
    >>> [(k, v) for k, v in entry.doc_metadata(str(uid)).items()]
    [('app_path', ['root', 'catalog_aware', 'target', 'source', 'c1']), 
    ('combined_title', 'catalog_aware - foo - foo - foo'), 
    ('path', ['catalog_aware', 'target', 'source', 'c1']), 
    ('state', 'state_1'), 
    ('title', 'foo')]
    
    >>> entry.printtree()
    <class 'cone.zodb.CatalogAwareZODBEntry'>: catalog_aware
      <class 'cone.zodb.tests.CatalogAwareDummyNode'>: foo
      <class 'cone.zodb.tests.CatalogAwareDummyNode'>: target
        <class 'cone.zodb.tests.CatalogAwareDummyNode'>: source
          <class 'cone.zodb.tests.CatalogAwareDummyNode'>: c1
          <class 'cone.zodb.tests.CatalogAwareDummyNode'>: c2
    
    >>> entry.catalog.query(Eq('path', {'query': '/catalog_aware/target'}))
    (4, IFSet([..., ..., ..., ...]))
    
    >>> entry.catalog.query(Eq('path',
    ...                        {'query': '/catalog_aware/target/source'}))
    (3, IFSet([..., ..., ...]))

Cleanup test environment::

    >>> import transaction
    >>> transaction.commit()
    >>> connection.close()
    >>> db.close()
    >>> import shutil
    >>> shutil.rmtree(tempdir)
