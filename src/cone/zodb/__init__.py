import uuid
import datetime
import transaction
from plumber import plumber
from node.parts import (
    AsAttrAccess,
    NodeChildValidate,
    Nodespaces,
    Attributes,
    DefaultInit,
    Nodify,
    Lifecycle,
    OdictStorage,
)
from node.locking import locktree
from node.ext.zodb import OOBTNode
from pyramid.threadlocal import get_current_request
from repoze.catalog.catalog import Catalog
from repoze.catalog.document import DocumentMap
from repoze.catalog.query import Eq
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.path import CatalogPathIndex
from cone.app.model import AppNode


FLOORDATETIME = datetime.datetime(1980, 1, 1) # XXX tzinfo


def force_dt(value):
    if not isinstance(value, datetime.datetime):
        return FLOORDATETIME
    return value


def zodb_path(node, default=None):
    path = list()
    while True:
        path.append(node.name)
        if node.parent is None or isinstance(node, ZODBEntryNode):
            return path
        node = node.parent


def get_uid(node, default):
    return node.attrs.get('uid', default)


def get_type(node, default):
    if hasattr(node, 'node_info_name'):
        return node.node_info_name
    return default


def get_state(node, default):
    if hasattr(node, 'state'):
        return node.state
    return default


def get_title(node, default):
    return node.attrs.get('title', default)


def combined_title(node):
    titles = list()
    while True:
        titles.append(node.attrs.get('title', node.name))
        if node.parent is None or isinstance(node, ZODBEntryNode):
            break
        node = node.parent
    titles.reverse()
    return ' - '.join(titles)


def create_default_catalog(instance):
    catalog = Catalog()
    catalog['uid'] = CatalogFieldIndex(get_uid)
    catalog['type'] = CatalogFieldIndex(get_type)
    catalog['state'] = CatalogFieldIndex(get_state)
    catalog['path'] = CatalogPathIndex(zodb_path)
    catalog['title'] = CatalogFieldIndex(get_title)
    return catalog


def create_default_metadata(instance, node):
    metadata = dict()
    metadata['path'] = zodb_path(node)
    metadata['title'] = node.attrs['title']
    metadata['combined_title'] = combined_title(node)
    if hasattr(node, 'state'):
        metadata['state'] = node.state
    return metadata


class ZODBEntryNode(OOBTNode):

    @property
    def __parent__(self):
        return self._v_parent.parent

    @property
    def metadata(self):
        return self.parent.metadata

    @property
    def properties(self):
        return self.parent.properties


class ZODBEntry(object):
    __metaclass__ = plumber
    __plumbing__ = (
        AppNode,
        AsAttrAccess,
        NodeChildValidate,
        Nodespaces,
        Attributes,
        DefaultInit,
        Nodify,
        Lifecycle,
        OdictStorage,
    )

    node_factory = ZODBEntryNode
    catalog_key = 'cone_catalog'
    doc_map_key = 'cone_doc_map'
    create_catalog = create_default_catalog
    create_metadata = create_default_metadata

    @property
    def db_name(self):
        return self.name
    
    @property
    def db_root(self):
        # XXX: get rid of get_current_request usage
        conn = get_current_request().environ['repoze.zodbconn.connection']
        return conn.root()

    @property
    def context(self):
        context = self.db_root.get(self.db_name)
        if not context:
            context = self.node_factory(name=self.name)
            self.db_root[self.db_name] = context
        context.__parent__ = self
        return context

    @property
    def catalog(self):
        catalog = self.db_root.get(self.catalog_key)
        if not catalog:
            self.set_new_catalog()
            catalog = self.db_root[self.catalog_key]
        return catalog

    def _index_recursiv(self, node, entry):
        for child in node.values():
            entry.index_doc(child)
            self._index_count += 1
            self._index_recursiv(child, entry)

    def rebuild_catalog(self):
        self.set_new_catalog()
        self._index_count = 0
        self._index_recursiv(self, self)
        ret = self._index_count
        del self._index_count
        return ret

    def set_new_catalog(self):
        self.db_root[self.catalog_key] = self.create_catalog()

    @property
    def doc_map(self):
        doc_map = self.db_root.get(self.doc_map_key)
        if not doc_map:
            self.db_root[self.doc_map_key] = DocumentMap()
            doc_map = self.db_root[self.doc_map_key]
        return doc_map

    def doc_metadata(self, uid):
        if not isinstance(uid, uuid.UUID):
            uid = uuid.UUID(uid)
        doc_map = self.doc_map
        doc_id = doc_map.docid_for_address(uid)
        return doc_map.get_metadata(doc_id)

    def index_doc(self, node):
        uid = node.attrs['uid']
        doc_map = self.doc_map
        catalog = self.catalog
        indexed = catalog.query(Eq('uid', uid))
        if indexed[0]:
            docid = doc_map.docid_for_address(uid)
            catalog.unindex_doc(docid)
            doc_map.remove_address(uid)
        docid = doc_map.add(uid)
        metadata = self.create_metadata(node)
        doc_map.add_metadata(docid, metadata)
        catalog.index_doc(docid, node)

    def unindex_doc(self, node):
        uid = node.attrs['uid']
        doc_map = self.doc_map
        docid = doc_map.docid_for_address(uid)
        self.catalog.unindex_doc(docid)
        doc_map.remove_address(uid)

    def unindex_recursiv(self, node):
        self.unindex_doc(node)
        for child in node.values():
            self.unindex_recursiv(child)

    def __getitem__(self, key):
        val = self.context[key]
        return val

    def __setitem__(self, key, val):
        self.context[key] = val

    def __iter__(self):
        return self.context.__iter__()

    @locktree
    def __delitem__(self, key):
        self.unindex_recursiv(self.context[key])
        del self.context[key]

    @locktree
    def __call__(self):
        transaction.commit()