from cone.app.model import AppNode
from cone.zodb.interfaces import IZODBEntry
from cone.zodb.interfaces import IZODBEntryNode
from node.behaviors import AsAttrAccess
from node.behaviors import Attributes
from node.behaviors import DefaultInit
from node.behaviors import Lifecycle
from node.behaviors import NodeChildValidate
from node.behaviors import Nodespaces
from node.behaviors import Nodify
from node.behaviors import Storage
from node.ext.zodb import IZODBNode
from node.ext.zodb import OOBTNode
from node.interfaces import IOrdered
from node.locking import locktree
from plumber import default
from plumber import override
from plumber import plumbing
from pyramid.threadlocal import get_current_request
from pyramid_zodbconn import get_connection
from zope.interface import implementer


def zodb_entry_for(node):
    while node:
        if IZODBEntryNode.providedBy(node):
            return node.entry
        if node.parent is None or not IZODBNode.providedBy(node):
            return None
        node = node.parent


@implementer(IZODBEntryNode)
class ZODBEntryNode(OOBTNode):

    @property
    def __parent__(self):
        # note: as parent ZODBEntryStorage instance is set, but we are
        # interested in it's parent when traversing.
        return self._v_parent.parent

    @__parent__.setter
    def __parent__(self, value):
        self._v_parent = value

    @property
    def entry(self):
        return self._v_parent

    @property
    def metadata(self):
        return self.entry.metadata

    @property
    def properties(self):
        return self.entry.properties


@implementer(IZODBEntry)
class ZODBEntryStorage(Storage):
    node_factory = default(ZODBEntryNode)

    @default
    @property
    def db_name(self):
        return self.name

    @default
    @property
    def db_root(self):
        # XXX: currently primary DB only, support named DB
        conn = get_connection(get_current_request())
        return conn.root()

    @default
    @property
    def storage(self):
        entry = self.db_root.get(self.db_name)
        if not entry:
            entry = self.node_factory(name=self.name, parent=self)
            self.db_root[self.db_name] = entry
        else:
            entry._v_parent = self
        return entry

    @override
    @locktree
    def __setitem__(self, key, val):
        self.storage[key] = val

    @override
    @locktree
    def __delitem__(self, key):
        del self.storage[key]

    @default
    @locktree
    def __call__(self):
        self.storage()


@plumbing(
    AppNode,
    AsAttrAccess,
    NodeChildValidate,
    Nodespaces,
    Attributes,
    DefaultInit,
    Nodify,
    Lifecycle,
    ZODBEntryStorage)
@implementer(IOrdered)
class ZODBEntry(object):
    pass
