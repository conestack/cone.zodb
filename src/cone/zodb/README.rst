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

Create node containing ZODBEntry::

    >>> import uuid
    >>> from cone.app.model import BaseNode
    >>> from cone.zodb import ZODBEntry
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
    <cone.app.model.Metadata object at ...>
    
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

It's a good idea to always store a UID for each ZODB node. For catalog aware
ZODB nodes this is required::

    >>> foo.attrs['uid']
    UUID('...')

Entry and entry node result in the same tree::

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

DB name::

    >>> class CustomZODBEntry(ZODBEntry):
    ...     @property
    ...     def db_name(self):
    ...         return 'custom_entry_storage'
    ...     @property
    ...     def name(self):
    ...         return 'entry_storage'
    
    >>> root['custom_entry_storage'] = CustomZODBEntry(name='custom_entry')
    >>> entry = root['custom_entry_storage']
    >>> entry
    <CustomZODBEntry object 'custom_entry_storage' at ...>
    
    >>> entry.name
    'entry_storage'
    
    >>> child = DummyZODBNode()
    >>> entry['child'] = child
    
    >>> child = entry['child']
    >>> child.path
    ['root', 'entry_storage', 'child']
    
    >>> entry.db_name
    'custom_entry_storage'

ZODBPrincipalACL::

    >>> from plumber import plumber, default
    >>> from node.ext.zodb import ZODBNode
    >>> from cone.app.model import AppNode
    >>> from cone.app.security import DEFAULT_ACL
    >>> from cone.zodb import ZODBPrincipalACL
    
    >>> class ZODBPrincipalACLNode(ZODBNode):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = AppNode, ZODBPrincipalACL
    ...     @property
    ...     def __acl__(self):
    ...         return DEFAULT_ACL
    
    >>> node = ZODBPrincipalACLNode()
    >>> node.principal_roles
    <OOBTNodeAttributes object 'principal_roles' at ...>
    
    >>> node.principal_roles['someuser'] = ['manager']
    >>> node.__acl__
    [('Allow', 'someuser', ['edit', 'manage', 'add', 'view', 'manage_permissions', 'delete']), 
    ('Allow', 'system.Authenticated', ['view']), 
    ('Allow', 'role:viewer', ['view']), 
    ('Allow', 'role:editor', ['view', 'add', 'edit']), 
    ('Allow', 'role:admin', ['view', 'add', 'edit', 'delete', 'manage_permissions']), 
    ('Allow', 'role:owner', ['view', 'add', 'edit', 'delete', 'manage_permissions']), 
    ('Allow', 'role:manager', ['view', 'add', 'edit', 'delete', 'manage_permissions', 'manage']), 
    ('Allow', 'system.Everyone', ['login']), 
    ('Deny', 'system.Everyone', <pyramid.security.AllPermissionsList object at ...>)]

Helper functions for catalog indexing::

``path``::

    >>> foo.path
    ['root', 'myentry', 'foo']

``zodb_path``::
    
    >>> from cone.zodb import zodb_path
    >>> zodb_path(bar)
    ['myentry', 'bar']
    
    >>> zodb_path(foo)
    ['myentry', 'foo']

``str_zodb_path``::
    
    >>> from cone.zodb import str_zodb_path
    >>> str_zodb_path(bar)
    '/myentry/bar'
    
    >>> str_zodb_path(foo)
    '/myentry/foo'

``app_path``::

    >>> from cone.zodb import app_path
    >>> app_path(foo)
    ['root', 'myentry', 'foo']

``str_app_path``::

    >>> from cone.zodb import str_app_path
    >>> str_app_path(foo)
    '/root/myentry/foo'

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
