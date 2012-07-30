from plumber import (
    plumber,
    default,
    override,
)
from node.behaviors import (
    AsAttrAccess,
    NodeChildValidate,
    Nodespaces,
    Attributes,
    DefaultInit,
    Nodify,
    Lifecycle,
    Storage,
)
from node.locking import locktree
from node.ext.zodb import (
    IZODBNode,
    OOBTNode,
)
from zope.interface import implementer
from pyramid.threadlocal import get_current_request
from cone.app.model import AppNode
from cone.zodb.interfaces import (
    IZODBEntry,
    IZODBEntryNode,
)


def zodb_entry_for(node):
    while node:
        if IZODBEntryNode.providedBy(node):
            return node._v_parent
        if node.parent is None or not IZODBNode.providedBy(node):
            return None
        node = node.parent


@implementer(IZODBEntryNode)
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
        # XXX: should be configurable somehow
        conn = get_current_request().environ['repoze.zodbconn.connection']
        return conn.root()
    
    @default
    @property
    def storage(self):
        entry = self.db_root.get(self.db_name)
        if not entry:
            entry = self.node_factory(name=self.name)
            self.db_root[self.db_name] = entry
        entry.__parent__ = self
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
        ZODBEntryStorage,
    )