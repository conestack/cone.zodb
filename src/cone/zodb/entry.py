from cone.app.model import AppNode
from cone.zodb.interfaces import IZODBEntry
from cone.zodb.interfaces import IZODBEntryNode
from node.behaviors import DefaultInit
from node.behaviors import Lifecycle
from node.behaviors import MappingConstraints
from node.behaviors import MappingNode
from node.behaviors import MappingStorage
from node.behaviors import Order
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
        if IZODBEntry.providedBy(node):
            return node
        if IZODBEntryNode.providedBy(node):
            return node.entry
        if not IZODBNode.providedBy(node) or node.parent is None:
            return None
        node = node.parent


@implementer(IZODBEntryNode)
class ZODBEntryNode(OOBTNode):

    @property
    def __parent__(self):
        # ZODBEntryStorage instance is set as parent, but we are
        # interested in it's parent when traversing.
        return self._v_parent.parent

    @property
    def entry(self):
        return self._v_parent

    @property
    def metadata(self):
        return self.entry.metadata

    @property
    def properties(self):
        return self.entry.properties

    def __getitem__(self, name):
        v = super(ZODBEntryNode, self).__getitem__(name)
        # _v_parent is not set if ZODBEntryNode is not read via ZODBEntryStorage
        # but from ZODB root directly.
        v._v_parent = getattr(self, '_v_parent', None)
        return v


@implementer(IZODBEntry)
class ZODBEntryStorage(MappingStorage):
    node_factory = default(ZODBEntryNode)

    @default
    @property
    def db_name(self):
        return self.name

    @default
    @property
    def db_root(self):
        # XXX: currently primary DB only, support named DB
        #      currently requires a current request. make connection lookup
        #      function searching on request first, but provides fallback.
        conn = get_connection(get_current_request())
        return conn.root()

    @default
    @property
    def storage(self):
        storage = self.db_root.get(self.db_name)
        if not storage:
            storage = self.node_factory(name=self.name, parent=self)
            self.db_root[self.db_name] = storage
        else:
            storage._v_parent = self
        return storage

    @override
    @property
    def attrs(self):
        return self.storage.attrs

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
    MappingConstraints,
    DefaultInit,
    Order,
    MappingNode,
    Lifecycle,
    ZODBEntryStorage)
@implementer(IOrdered)
class ZODBEntry(object):

    # override methods of ``Order`` which expect odict like storage on self.
    # we already have ``IOrder`` providing node as storage, proxy related
    # calls to storage.

    def swap(self, node_a, node_b):
        self.storage.swap(node_a, node_b)

    def insertbefore(self, newnode, refnode):
        self.storage.insertbefore(newnode, refnode)

    def insertafter(self, newnode, refnode):
        self.storage.insertafter(newnode, refnode)

    def insertfirst(self, newnode):
        self.storage.insertfirst(newnode)

    def insertlast(self, newnode):
        self.storage.insertlast(newnode)

    def movebefore(self, movenode, refnode):
        self.storage.movebefore(movenode, refnode)

    def moveafter(self, movenode, refnode):
        self.storage.moveafter(movenode, refnode)

    def movefirst(self, movenode):
        self.storage.movefirst(movenode)

    def movelast(self, movenode):
        self.storage.movelast(movenode)
