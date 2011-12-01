import uuid
import datetime
from plumber import (
    plumber,
    default,
    plumb,
    Part,
)
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
from node.utils import instance_property
from node.ext.zodb import (
    IZODBNode,
    OOBTNode,
    OOBTNodeAttributes,
)
from zope.interface import (
    Interface,
    implements,
)
from pyramid.threadlocal import get_current_request
from repoze.catalog.catalog import Catalog
from repoze.catalog.document import DocumentMap
from repoze.catalog.query import Eq
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.path import CatalogPathIndex
from cone.app.model import (
    AppNode,
    AppRoot,
)
from cone.app.security import (
    DEFAULT_ACL,
    PrincipalACL,
)


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
            path.reverse()
            return path
        node = node.parent


def str_zodb_path(node, default=None):
    path = zodb_path(node, default)
    if path:
        return '/%s' % '/'.join(path)


def app_path(node, default=None):
    path = list()
    while True:
        path.append(node.name)
        if node.parent is None or isinstance(node.parent, AppRoot):
            path.reverse()
            return path
        node = node.parent


def str_app_path(node, default=None):
    path = app_path(node, default)
    if path:
        return '/%s' % '/'.join(path)


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
    catalog['path'] = CatalogPathIndex(str_zodb_path)
    catalog['app_path'] = CatalogPathIndex(str_app_path)
    catalog['title'] = CatalogFieldIndex(get_title)
    return catalog


def create_default_metadata(instance, node):
    metadata = dict()
    metadata['path'] = zodb_path(node)
    metadata['app_path'] = app_path(node)
    metadata['title'] = node.attrs['title']
    metadata['combined_title'] = combined_title(node)
    if hasattr(node, 'state'):
        metadata['state'] = node.state
    return metadata


def zodb_entry_for(node):
    while node:
        if IZODBEntryNode.providedBy(node):
            return node._v_parent
        if node.parent is None or not IZODBNode.providedBy(node):
            return None
        node = node.parent


class IZODBEntryNode(IZODBNode):
    """Marker interface for first level ZODB nodes.
    """


class ZODBEntryNode(OOBTNode):
    implements(IZODBEntryNode)

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

    def __getitem__(self, key):
        return self.context[key]

    @locktree
    def __setitem__(self, key, val):
        self.context[key] = val

    @locktree
    def __delitem__(self, key):
        del self.context[key]
    
    def __iter__(self):
        return self.context.__iter__()

    @locktree
    def __call__(self):
        self.context()


class ZODBPrincipalACL(PrincipalACL):
    """Principal ACL for ZODB nodes.
    """
    
    @default
    @instance_property
    def principal_roles(self):
        return OOBTNodeAttributes('principal_roles')


class ZODBEntryPrincipalACL(PrincipalACL):
    
    @default
    @instance_property
    def principal_roles(self):
        return self.context.principal_roles


class ICatalogAware(Interface):
    """Marker interface if ZODB node is catalog aware.
    """


class CatalogAware(Part):
    """Plumbing part for nodes indexed in a catalog.
    """
    implements(ICatalogAware)
    
    @plumb
    def __setitem__(_next, self, key, value):
        _next(self, key, value)
        zodb_entry_for(self).index_recursiv(self[key])
    
    @plumb
    def __delitem__(_next, self, key):
        zodb_entry_for(self).unindex_recursiv(self[key])
        _next(self, key)
    
    @plumb
    def __call__(_next, self):
        _next(self)
        if not IZODBEntryNode.providedBy(self):
            zodb_entry_for(self).index_doc(self)


class CatalogAwareZODBEntryNode(ZODBEntryNode):
    __metaclass__ = plumber
    __plumbing__ = CatalogAware


class CatalogAwareZODBEntry(ZODBEntry):
    node_factory = CatalogAwareZODBEntryNode
    catalog_key = 'cone_catalog'
    doc_map_key = 'cone_doc_map'
    create_catalog = create_default_catalog
    create_metadata = create_default_metadata
    
    @property
    def catalog(self):
        catalog = self.db_root.get(self.catalog_key)
        if not catalog:
            self.reset_catalog()
            catalog = self.db_root[self.catalog_key]
        return catalog

    def rebuild_catalog(self):
        self.reset_catalog()
        self._index_count = 0
        for child in self.values():
            self.index_recursiv(child)
        ret = self._index_count
        del self._index_count
        return ret

    def reset_catalog(self):
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
    
    def index_recursiv(self, node):
        if ICatalogAware.providedBy(node):
            self.index_doc(node)
            if hasattr(self, '_index_count'):
                self._index_count += 1
        for child in node.values():
            self.index_recursiv(child)

    def unindex_doc(self, node):
        uid = node.attrs['uid']
        doc_map = self.doc_map
        docid = doc_map.docid_for_address(uid)
        self.catalog.unindex_doc(docid)
        doc_map.remove_address(uid)

    def unindex_recursiv(self, node):
        if ICatalogAware.providedBy(node):
            self.unindex_doc(node)
        for child in node.values():
            self.unindex_recursiv(child)