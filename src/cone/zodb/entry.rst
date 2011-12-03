Setup test::

    >>> request = layer.new_request()

Create node containing ZODBEntry::

    >>> from cone.app.model import BaseNode
    >>> from cone.zodb import ZODBEntry
    >>> root = BaseNode(name='root')
    >>> root['myentry'] = ZODBEntry()
    >>> entry = root['myentry']
    >>> entry
    <ZODBEntry object 'myentry' at ...>

ZODB entry node of entry is looked up by db_name from db root::

    >>> entry.storage
    <ZODBEntryNode object 'myentry' at ...>
    
``metadata`` and ``properties`` are returned from entry::

    >>> entry.storage.metadata
    <cone.app.model.Metadata object at ...>
    
    >>> entry.storage.properties
    <cone.app.model.Properties object at ...>

Create children::

    >>> from cone.zodb.testing import ZODBDummyNode
    >>> foo = ZODBDummyNode()
    >>> entry['foo'] = foo
    >>> bar = ZODBDummyNode()
    >>> bar.attrs['title'] = 'bar'
    >>> entry['bar'] = bar

``__iter__``::

    >>> [k for k in entry]
    ['foo', 'bar']

``__getitem__``::

    >>> entry['foo']
    <ZODBDummyNode object 'foo' at ...>

``keys``::

    >>> foo.attrs.keys()
    ['title']

ZODBDummyNode is UUIDAware::

    >>> from node.interfaces import IUUIDAware
    >>> IUUIDAware.providedBy(foo)
    True
    
    >>> foo.uuid
    UUID('...')

Entry and entry node result in the same tree::

    >>> entry.printtree()
    <class 'cone.zodb.entry.ZODBEntry'>: myentry
      <class 'cone.zodb.testing.ZODBDummyNode'>: foo
      <class 'cone.zodb.testing.ZODBDummyNode'>: bar
    
    >>> entry.storage.printtree()
    <class 'cone.zodb.entry.ZODBEntryNode'>: myentry
      <class 'cone.zodb.testing.ZODBDummyNode'>: foo
      <class 'cone.zodb.testing.ZODBDummyNode'>: bar

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
    
    >>> child = ZODBDummyNode()
    >>> entry['child'] = child
    
    >>> child = entry['child']
    >>> child.path
    ['root', 'entry_storage', 'child']
    
    >>> entry.db_name
    'custom_entry_storage'
    
Cleanup test environment::

    >>> import transaction
    >>> transaction.commit()