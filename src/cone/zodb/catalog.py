from plumber import (
    plumber,
    plumb,
    default,
    Part,
)
from zope.interface import implements
from node.parts import UUIDAware
from node.utils import instance_property
from repoze.catalog.interfaces import ICatalog
from repoze.catalog.document import DocumentMap
from cone.zodb.interfaces import ICatalogAware
from cone.zodb.entry import (
    zodb_entry_for,
    ZODBEntryNode,
    ZODBEntry,
)


class CatalogProxy(object):
    
    def __init__(self, dbcontext, indexing_root, catalog_key,
                 doc_map_key, catalog_factory, metadata_factory):
        """
        dbcontext
            IZODBNode instance.
        indexing_root
            Indexing root. defaults to self.dbcontext.
        catalog_key
            DB key of catalog.
        doc_map_key
            DB key of doc_map.
        catalog_factory
            Factory callback for creating catalog instance.
        metadata_factory
            Factory callback for creating node metadata.
        """
        self.dbcontext = dbcontext
        self.indexing_root = indexing_root
        self.catalog_key = catalog_key
        self.doc_map_key = doc_map_key
        self.catalog_factory = create_default_catalog
        self.catalog_docmap_factory = create_default_docmap
    
    @property
    def entry(self):
        return zodb_entry_for(self.dbcontext)
    
    @property
    def catalog(self):
        entry = self.entry
        catalog = entry.db_root.get(self.catalog_key)
        if catalog and not ICatalog.providedBy(catalog):
            raise ValueError(u'ICatalog not provided by %s' % self.catalog_key)
        if not catalog:
            self.reset_catalog()
            catalog = entry.db_root[self.catalog_key]
        return catalog
    
    @property
    def doc_map(self, name):
        entry = self.entry
        doc_map = enty.db_root.get(self.doc_map_key)
        if doc_map and not isinstance(doc_map, DocumentMap):
            raise ValueError(
                u'%s not a DocumentMap instance' % self.catalog_key)
        if not doc_map:
            entry.db_root[self.doc_map_key] = DocumentMap()
            doc_map = entry.db_root[self.doc_map_key]
        return doc_map
    
    def rebuild_catalog(self):
        self.reset_catalog()
        self._index_count = 0
        for child in self.indexing_root.values():
            self.index_recursiv(child)
        ret = self._index_count
        del self._index_count
        return ret

    def reset_catalog(self):
        self.entry.db_root[self.catalog_key] = self.catalog_factory()

    def doc_metadata(self, uid):
        if not isinstance(uid, uuid.UUID):
            uid = uuid.UUID(uid)
        doc_map = self.doc_map
        doc_id = doc_map.docid_for_address(uid)
        return doc_map.get_metadata(doc_id)

    def index_doc(self, node):
        uid = node.uuid
        doc_map = self.doc_map
        catalog = self.catalog
        indexed = catalog.query(Eq('uid', uid))
        if indexed[0]:
            docid = doc_map.docid_for_address(uid)
            catalog.unindex_doc(docid)
            doc_map.remove_address(uid)
        docid = doc_map.add(uid)
        metadata = self.metadata_factory(node)
        doc_map.add_metadata(docid, metadata)
        catalog.index_doc(docid, node)
    
    def index_recursiv(self, node):
        if ICatalogAware.providedBy(node):
            self.index_doc(node)
            if hasattr(self, '_index_count'):
                self._index_count += 1
        for child in node.values():
            self.index_recursiv(child)

    def unindex_doc(self, node):
        uid = node.uuid
        doc_map = self.doc_map
        docid = doc_map.docid_for_address(uid)
        self.catalog.unindex_doc(docid)
        doc_map.remove_address(uid)

    def unindex_recursiv(self, node):
        if ICatalogAware.providedBy(node):
            self.unindex_doc(node)
        for child in node.values():
            self.unindex_recursiv(child)


class CatalogIndexer(object):
    
    def __init__(self, *proxies):
        self.proxies = proxies
    
    def index_doc(self, node):
        for proxy in self.proxies:
            proxy.index_doc(node)
    
    def index_recursiv(self, node):
        for proxy in self.proxies:
            proxy.index_recursiv(node)
    
    def unindex_doc(self, node):
        for proxy in self.proxies:
            proxy.unindex_doc(node)
    
    def unindex_recursiv(self, node):
        for proxy in self.proxies:
            proxy.unindex_recursiv(node)


class CatalogAware(UUIDAware):
    implements(ICatalogAware)
    
    @default
    @property
    def catalog_proxies(self):
        return [CatalogProxy(
            self,
            zodb_entry_for(self),
            'cone_catalog',
            'cone_doc_map',
            create_default_catalog,
            create_default_metadata),
        ]
    
    @default
    @property
    def catalog_indexer(self):
        return CatalogIndexer(self.catalog_proxies)
    
    @plumb
    def __setitem__(_next, self, key, value):
        _next(self, key, value)
        self.catalog_indexer.index_recursiv(self[key])
    
    @plumb
    def __delitem__(_next, self, key):
        self.catalog_indexer.unindex_recursiv(self[key])
        _next(self, key)
    
    @plumb
    def __call__(_next, self):
        _next(self)
        if not IZODBEntryNode.providedBy(self):
            self.catalog_indexer.index_doc(self)


class CatalogAwareZODBEntryNode(ZODBEntryNode):
    __metaclass__ = plumber
    __plumbing__ = CatalogAware


class CatalogAwareZODBEntry(ZODBEntry):
    node_factory = CatalogAwareZODBEntryNode