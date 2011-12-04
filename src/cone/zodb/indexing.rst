Helper functions for catalog indexing::

    >>> from cone.app.model import BaseNode
    >>> from cone.zodb import ZODBEntry
    >>> from cone.zodb.testing import ZODBDummyNode
    >>> root = BaseNode(name='root')
    >>> entry = root['myentry'] = ZODBEntry()
    >>> foo = entry['foo'] = ZODBDummyNode()
    >>> bar = entry['bar'] = ZODBDummyNode()
    >>> bar.attrs['title'] = 'Bar title'

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
    'myentry - Bar title'

``force_dt``::

    >>> from cone.zodb.indexing import force_dt, FLOORDATETIME
    >>> force_dt('foo')
    datetime.datetime(1980, 1, 1, 0, 0)
    
    >>> FLOORDATETIME == force_dt('foo')
    True
    
    >>> import datetime
    >>> force_dt(datetime.datetime(2011, 5, 1))
    datetime.datetime(2011, 5, 1, 0, 0)

``get_uid``::

    >>> from plumber import plumber
    >>> from node.parts import UUIDAware
    >>> class UUIDNode(BaseNode):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = UUIDAware
    
    >>> from cone.zodb import get_uid
    >>> get_uid(BaseNode(), 'default')
    'default'
    
    >>> get_uid(UUIDNode(), 'default')
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
    
    >>> from cone.app.interfaces import IWorkflowState
    >>> from zope.interface import alsoProvides
    >>> setattr(foo, 'state', 'state_1')
    >>> alsoProvides(foo, IWorkflowState)
    >>> get_state(foo, 'default')
    'state_1'

``get_title``::

    >>> from cone.zodb import get_title
    >>> get_title(BaseNode(), 'default')
    'default'
    
    >>> get_title(foo, 'default')
    'foo'

``create_default_catalog``::

    >>> from cone.zodb import create_default_catalog
    >>> create_default_catalog()
    {'app_path': <repoze.catalog.indexes.path.CatalogPathIndex object at ...>, 
    'uid': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'title': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'state': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>, 
    'path': <repoze.catalog.indexes.path.CatalogPathIndex object at ...>, 
    'type': <repoze.catalog.indexes.field.CatalogFieldIndex object at ...>}

``create_default_metadata``::

    >>> from zope.interface import alsoProvides
    >>> from cone.app.interfaces import IWorkflowState
    >>> from cone.zodb import create_default_metadata
    >>> setattr(bar, 'state', 'some_wf_state')
    >>> alsoProvides(bar, IWorkflowState)
    >>> create_default_metadata(bar)
    {'path': ['myentry', 'bar'], 
    'state': 'some_wf_state', 
    'title': 'Bar title', 
    'combined_title': 'myentry - Bar title', 
    'app_path': ['root', 'myentry', 'bar']}
