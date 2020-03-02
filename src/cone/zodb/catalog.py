from cone.zodb.entry import zodb_entry_for
from cone.zodb.indexing import create_default_catalog
from cone.zodb.indexing import create_default_metadata
from cone.zodb.interfaces import ICatalogAware
from cone.zodb.interfaces import IZODBEntryNode
from node.behaviors import UUIDAware
from plumber import Behavior
from plumber import default
from plumber import plumb
from repoze.catalog.document import DocumentMap
from repoze.catalog.interfaces import ICatalog
from repoze.catalog.query import Eq
from zope.interface import implementer
import uuid


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
        self.catalog_factory = catalog_factory
        self.metadata_factory = metadata_factory

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
    def doc_map(self):
        entry = self.entry
        doc_map = entry.db_root.get(self.doc_map_key)
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

    def __init__(self, proxies):
        self.proxies = proxies

    def _proxy(self, func_name, node):
        for proxy in self.proxies.values():
            getattr(proxy, func_name)(node)

    def index_doc(self, node):
        self._proxy('index_doc', node)

    def index_recursiv(self, node):
        self._proxy('index_recursiv', node)

    def unindex_doc(self, node):
        self._proxy('unindex_doc', node)

    def unindex_recursiv(self, node):
        self._proxy('unindex_recursiv', node)


@implementer(ICatalogAware)
class CatalogAware(UUIDAware):
    include_entry = default(False)
    """Flag controls whether to index entry node in calatog.
    """

    @default
    @property
    def catalog_proxies(self):
        proxies = dict()
        proxies['default'] = CatalogProxy(
            self, zodb_entry_for(self), 'cone_catalog', 'cone_doc_map',
            create_default_catalog, create_default_metadata)
        return proxies

    @default
    @property
    def catalog_indexer(self):
        return CatalogIndexer(self.catalog_proxies)

    @plumb
    def __init__(_next, self, *args, **kwargs):
        _next(self, *args, **kwargs)
        if self.include_entry and IZODBEntryNode.providedBy(self):
            self.catalog_indexer.index_doc(self)

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
        if IZODBEntryNode.providedBy(self) and not self.include_entry:
            return
        self.catalog_indexer.index_doc(self)


class CatalogProvidingEntry(Behavior):
    """Helper behavior for ZODB entries to provide ``catalog_proxies`` and
    ``catalog_indexer`` directly.
    """

    @default
    @property
    def catalog_proxies(self):
        return self.storage.catalog_proxies

    @default
    @property
    def catalog_indexer(self):
        return CatalogIndexer(self.storage.catalog_proxies)
