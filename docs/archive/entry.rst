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
    ['title', 'uuid']

IZODBEntry and IZODBEntryNode::

    >>> from cone.zodb.interfaces import (
    ...     IZODBEntry,
    ...     IZODBEntryNode,
    ... )
    
    >>> IZODBEntry.providedBy(entry)
    True
    
    >>> IZODBEntryNode.providedBy(entry.storage)
    True

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

``__delitem__``::

    >>> del entry['foo']
    >>> entry.printtree()
    <class 'cone.zodb.entry.ZODBEntry'>: myentry
      <class 'cone.zodb.testing.ZODBDummyNode'>: bar

``__call__`` delegates to storage, which is the ZODB entry node::

    >>> entry()

``zodb_entry_for``::

    >>> from cone.zodb import zodb_entry_for
    >>> zodb_entry_for(entry['bar'])
    <ZODBEntry object 'myentry' at ...>
    
    >>> zodb_entry_for(entry.storage)
    <ZODBEntry object 'myentry' at ...>
    
    >>> zodb_entry_for(root)

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
