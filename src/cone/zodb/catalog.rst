Create calatog aware ZODB entry::

    >>> from cone.app.model import BaseNode
    >>> from cone.zodb.testing import (
    ...     CatalogAwareZODBNode,
    ...     CatalogAwareZODBEntry,
    ... )
    
    >>> root = BaseNode(name='root')
    >>> entry = root['catalog_aware'] = CatalogAwareZODBEntry()
    >>> entry.catalog_proxies['default'].catalog
    {'app_path': <repoze.catalog.indexes.path.CatalogPathIndex object at ...>, 
    'uid': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'title': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'state': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'path': <repoze.catalog.indexes.path.CatalogPathIndex object at ...>, 
    'type': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>}
    
    >>> foo = CatalogAwareZODBNode()
    >>> bar = CatalogAwareZODBNode()
    >>> bar.attrs['title'] = 'bar'

Empty. Nodes not added yet::

    >>> uid = foo.uuid
    >>> from repoze.catalog.query import Eq
    >>> entry.catalog_proxies['default'].catalog.query(Eq('uid', uid))
    (0, IFSet([]))

Add nodes and query catalog::

    >>> entry['foo'] = foo
    >>> entry['bar'] = bar
    >>> res = entry.catalog_proxies['default'].catalog.query(Eq('uid', uid))
    >>> res
    (1, IFSet([...]))

Check path index::

    >>> entry.catalog_proxies['default'].catalog.query(
    ...     Eq('path', {'query': '/catalog_aware', 'level': 0}))
    (2, IFSet([..., ...]))
    
    >>> entry.catalog_proxies['default'].catalog.query(
    ...     Eq('app_path', {'query': 'root'}))
    (2, IFSet([..., ...]))

Check metadata::

    >>> [(k, v) for k, v in \
    ...     entry.catalog_proxies['default'].doc_metadata(uid).items()]
    [('app_path', ['root', 'catalog_aware', 'foo']), 
    ('combined_title', 'catalog_aware - foo'), 
    ('path', ['catalog_aware', 'foo']), 
    ('title', 'foo'), 
    ('uid', UUID('...'))]

Reindexing happens at ``__call__`` time::

    >>> foo.attrs['title'] = 'foo changed'
    >>> foo()
    >>> [(k, v) for k, v in \
    ...     entry.catalog_proxies['default'].doc_metadata(str(uid)).items()]
    [('app_path', ['root', 'catalog_aware', 'foo']), 
    ('combined_title', 'catalog_aware - foo changed'), 
    ('path', ['catalog_aware', 'foo']), 
    ('title', 'foo changed'), 
    ('uid', UUID('...'))]

Calling the ZODB entry delegates to refering ZODB entry node::

    >>> entry()

Create child for 'bar'::

    >>> child = CatalogAwareZODBNode()
    >>> bar['child'] = child
    >>> child.attrs['title'] = 'Child of bar'
    >>> child()
    >>> entry.printtree()
    <class 'cone.zodb.testing.CatalogAwareZODBEntry'>: catalog_aware
      <class 'cone.zodb.testing.CatalogAwareZODBNode'>: foo
      <class 'cone.zodb.testing.CatalogAwareZODBNode'>: bar
        <class 'cone.zodb.testing.CatalogAwareZODBNode'>: child
    
    >>> bar_uid = bar.uuid
    >>> entry.catalog_proxies['default'].catalog.query(Eq('uid', bar_uid))
    (1, IFSet([...]))
    
    >>> child_uid = child.uuid
    >>> entry.catalog_proxies['default'].catalog.query(Eq('uid', child_uid))
    (1, IFSet([...]))

Rebuild catalog::

    >>> entry.catalog_proxies['default'].rebuild_catalog()
    3
    
    >>> entry.catalog_proxies['default'].catalog.query(Eq('type', 'dummytype'))
    (3, IFSet([..., ..., ...]))

Delete node. Gets unindexed recursive.::
    
    >>> del entry['bar']
    
    >>> entry.printtree()
    <class 'cone.zodb.testing.CatalogAwareZODBEntry'>: catalog_aware
      <class 'cone.zodb.testing.CatalogAwareZODBNode'>: foo
    
    >>> entry.catalog_proxies['default'].catalog.query(Eq('uid', bar_uid))
    (0, IFSet([]))
    
    >>> entry.catalog_proxies['default'].catalog.query(Eq('uid', child_uid))
    (0, IFSet([]))
    
    >>> entry.catalog_proxies['default'].catalog.query(Eq('type', 'dummytype'))
    (1, IFSet([...]))
    
    >>> entry.catalog_proxies['default'].rebuild_catalog()
    1
    
Test moving of subtrees, if objects get indexed the right way::

    >>> source = entry['source'] = CatalogAwareZODBNode()
    >>> source['c1'] = CatalogAwareZODBNode()
    >>> source['c2'] = CatalogAwareZODBNode()
    >>> target = entry['target'] = CatalogAwareZODBNode()
    >>> entry.printtree()
    <class 'cone.zodb.testing.CatalogAwareZODBEntry'>: catalog_aware
      <class 'cone.zodb.testing.CatalogAwareZODBNode'>: foo
      <class 'cone.zodb.testing.CatalogAwareZODBNode'>: source
        <class 'cone.zodb.testing.CatalogAwareZODBNode'>: c1
        <class 'cone.zodb.testing.CatalogAwareZODBNode'>: c2
      <class 'cone.zodb.testing.CatalogAwareZODBNode'>: target
    
    >>> uid = source['c1'].uuid
    >>> [(k, v) for k, v in \
    ...     entry.catalog_proxies['default'].doc_metadata(str(uid)).items()]
    [('app_path', ['root', 'catalog_aware', 'source', 'c1']), 
    ('combined_title', 'catalog_aware - foo - foo'), 
    ('path', ['catalog_aware', 'source', 'c1']), 
    ('title', 'foo'), 
    ('uid', UUID('...'))]
    
    >>> to_move = entry.detach('source')
    >>> target[to_move.name] = to_move
    >>> uid = target['source']['c1'].uuid
    >>> [(k, v) for k, v in \
    ...     entry.catalog_proxies['default'].doc_metadata(str(uid)).items()]
    [('app_path', ['root', 'catalog_aware', 'target', 'source', 'c1']), 
    ('combined_title', 'catalog_aware - foo - foo - foo'), 
    ('path', ['catalog_aware', 'target', 'source', 'c1']), 
    ('title', 'foo'), 
    ('uid', UUID('...'))]
    
    >>> entry.printtree()
    <class 'cone.zodb.testing.CatalogAwareZODBEntry'>: catalog_aware
      <class 'cone.zodb.testing.CatalogAwareZODBNode'>: foo
      <class 'cone.zodb.testing.CatalogAwareZODBNode'>: target
        <class 'cone.zodb.testing.CatalogAwareZODBNode'>: source
          <class 'cone.zodb.testing.CatalogAwareZODBNode'>: c1
          <class 'cone.zodb.testing.CatalogAwareZODBNode'>: c2
    
    >>> entry.catalog_proxies['default'].catalog.query(
    ...     Eq('path', {'query': '/catalog_aware/target'}))
    (4, IFSet([..., ..., ..., ...]))
    
    >>> entry.catalog_proxies['default'].catalog.query(
    ...     Eq('path', {'query': '/catalog_aware/target/source'}))
    (3, IFSet([..., ..., ...]))

Test CatalogIndexer::

    >>> indexer = entry.catalog_indexer
    >>> indexer
    <cone.zodb.catalog.CatalogIndexer object at ...>
    
    >>> foo = entry['foo']
    >>> indexer.unindex_doc(foo)
    
    >>> entry.catalog_proxies['default'].catalog.query(Eq('uid', foo.uuid))
    (0, IFSet([]))
    
    >>> indexer.index_doc(foo)
    >>> entry.catalog_proxies['default'].catalog.query(Eq('uid', foo.uuid))
    (1, IFSet([...]))
    
    >>> target = entry['target']
    >>> indexer.unindex_recursiv(target)
    >>> entry.catalog_proxies['default'].catalog.query(
    ...     Eq('path', {'query': '/catalog_aware'}))
    (1, IFSet([...]))
    
    >>> indexer.index_recursiv(target)
    >>> entry.catalog_proxies['default'].catalog.query(
    ...     Eq('path', {'query': '/catalog_aware'}))
    (5, IFSet([..., ..., ..., ..., ...]))

Test pointing CatalogProxy to existing objects providing the wrong interface::

    >>> from persistent import Persistent
    >>> from cone.zodb import CatalogProxy
    >>> from cone.zodb.indexing import (
    ...     create_default_catalog,
    ...     create_default_metadata,
    ... )
    >>> db_root = layer.zodb_root()
    >>> db_root['invalid_catalog_object'] = Persistent()
    >>> db_root['invalid_doc_map_object'] = Persistent()
    
    >>> proxy = CatalogProxy(
    ...     entry['foo'], entry, 'invalid_catalog_object',
    ...     'invalid_doc_map_object', create_default_catalog,
    ...     create_default_metadata)
    
    >>> proxy.catalog
    Traceback (most recent call last):
      ...
    ValueError: ICatalog not provided by invalid_catalog_object
    
    >>> proxy.doc_map
    Traceback (most recent call last):
      ...
    ValueError: invalid_catalog_object not a DocumentMap instance

Re-init ZODB connection::

    >>> import transaction
    >>> transaction.commit()
    >>> layer.init_zodb()
