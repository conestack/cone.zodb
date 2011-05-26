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

ZODBEntry::

    >>> import uuid
    >>> from cone.app.model import BaseNode
    >>> from cone.zodb import ZODBEntry

Create node containing ZODBEntry::

    >>> root = BaseNode(name='root')
    >>> root['myentry'] = ZODBEntry()
    >>> entry = root['myentry']
    >>> entry
    <ZODBEntry object 'myentry' at ...>

Context of entry is looked up by given key from db root::

    >>> entry.context
    <ZODBEntryNode object 'myentry' at ...>
    
``metadata`` and ``properties`` are returned from entry::

    >>> entry.context.metadata
    <cone.app.model.BaseMetadata object at ...>
    
    >>> entry.context.properties
    <cone.app.model.ProtectedProperties object at ...>

Create children::

    >>> from cone.zodb.tests import DummyZODBNode
    >>> foo = DummyZODBNode()
    >>> entry['foo'] = foo
    >>> bar = DummyZODBNode()
    >>> bar.attrs['title'] = 'bar'
    >>> entry['bar'] = bar

``__iter__``::

    >>> [k for k in entry]
    ['foo', 'bar']

``__getitem__``::

    >>> entry['foo']
    <DummyZODBNode object 'foo' at ...>

``keys``::

    >>> foo.attrs.keys()
    ['uid', 'title']

Its a good idea to always store a UID for each ZODB node. Also considered in
catalog::

    >>> foo.attrs['uid']
    UUID('...')

Entry and context same tree::

    >>> entry.printtree()
    <class 'cone.zodb.ZODBEntry'>: myentry
      <class 'cone.zodb.tests.DummyZODBNode'>: foo
      <class 'cone.zodb.tests.DummyZODBNode'>: bar
    
    >>> entry.context.printtree()
    <class 'cone.zodb.ZODBEntryNode'>: myentry
      <class 'cone.zodb.tests.DummyZODBNode'>: foo
      <class 'cone.zodb.tests.DummyZODBNode'>: bar

``__parent__``::
   
    >>> foo.__parent__
    <ZODBEntryNode object 'myentry' at ...>
    
    >>> foo.__parent__.__parent__
    <BaseNode object 'root' at ...>

``path``::

    >>> foo.path
    ['root', 'myentry', 'foo']

``zodb_path``::
    
    >>> from cone.zodb import zodb_path
    >>> zodb_path(bar)
    ['bar', 'myentry']

``combined_title``::

    >>> from cone.zodb import combined_title
    >>> combined_title(bar)
    'myentry - bar'

``force_dt``::

    >>> from cone.zodb import force_dt, FLOORDATETIME
    >>> force_dt('foo')
    datetime.datetime(1980, 1, 1, 0, 0)
    
    >>> FLOORDATETIME == force_dt('foo')
    True
    
    >>> import datetime
    >>> force_dt(datetime.datetime(2011, 5, 1))
    datetime.datetime(2011, 5, 1, 0, 0)

``get_uid``::

    >>> from cone.zodb import get_uid
    >>> get_uid(BaseNode(), 'default')
    'default'
    
    >>> get_uid(foo, 'default')
    UUID('...')

``get_type``::

    >>> from cone.zodb import get_type
    >>> get_type(object(), 'default')
    'default'
    
    >>> get_type(foo, 'default')
    'dummytype'

``get_state``::

    >>> from cone.zodb import get_state
    >>> get_state(object(), 'default')
    'default'
    
    >>> get_state(foo, 'default')
    'state_1'

``get_title``::

    >>> from cone.zodb import get_title
    >>> get_title(BaseNode(), 'default')
    'default'
    
    >>> get_title(foo, 'default')
    'foo'

Catalog for this ZODBEntry::

    >>> from repoze.catalog.query import Eq
    >>> entry.catalog
    {'path': <repoze.catalog.indexes.path.CatalogPathIndex object at ...>, 
    'state': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'type': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'uid': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'title': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>}

Empty. Nothing indexed yet::

    >>> uid = foo.attrs['uid']
    >>> entry.catalog.query(Eq('uid', uid))
    (0, IFSet([]))

Index node and query catalog::

    >>> entry.index_doc(foo)
    >>> res = entry.catalog.query(Eq('uid', uid))
    >>> res
    (1, IFSet([...]))
    
    >>> [(k, v) for k, v in entry.doc_metadata(uid).items()]
    [('combined_title', 'myentry - foo'), 
    ('path', ['foo', 'myentry']), 
    ('state', 'state_1'), 
    ('title', 'foo')]

After changing the node, reindex::

    >>> foo.attrs['title'] = 'foo changed'
    >>> entry.index_doc(foo)
    >>> [(k, v) for k, v in entry.doc_metadata(str(uid)).items()]
    [('combined_title', 'myentry - foo changed'), 
    ('path', ['foo', 'myentry']), 
    ('state', 'state_1'), 
    ('title', 'foo changed')]

Create child for 'bar'::

    >>> child = DummyZODBNode()
    >>> bar['child'] = child
    >>> child.attrs['title'] = 'Child of bar'
    >>> entry.index_doc(bar)
    >>> entry.index_doc(child)
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

Unindex node::

    >>> entry.unindex_doc(foo)
    >>> entry.catalog.query(Eq('uid', foo.attrs['uid']))
    (0, IFSet([]))

When deleting nodes with children, child nodes are unindexed recusriv as well::

    >>> del entry['bar']
    >>> entry.printtree()
    <class 'cone.zodb.ZODBEntry'>: myentry
      <class 'cone.zodb.tests.DummyZODBNode'>: foo
    
    >>> entry.catalog.query(Eq('uid', bar_uid))
    (0, IFSet([]))
    
    >>> entry.catalog.query(Eq('uid', child_uid))
    (0, IFSet([]))

Cleanup test environment::

    >>> entry()
    >>> connection.close()
    >>> db.close()
    >>> import shutil
    >>> shutil.rmtree(tempdir)
