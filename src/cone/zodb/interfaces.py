from node.interfaces import IUUIDAware
from node.ext.zodb import IZODBNode


class IZODBEntryNode(IZODBNode):
    """Marker interface for first level ZODB nodes.
    """


class ICatalogAware(IUUIDAware):
    """Marker interface if node is ZODB catalog aware.
    """