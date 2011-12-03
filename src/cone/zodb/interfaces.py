from node.interfaces import (
    IStorage,
    IUUIDAware,
)
from node.ext.zodb import IZODBNode


class IZODBEntry(IStorage):
    """Marker interface for ZODB entry. ``storage`` attribute contains a
    ``IZODBEntryNode`` implementing instance.
    """


class IZODBEntryNode(IZODBNode):
    """Marker interface for first level ZODB nodes.
    """


class ICatalogAware(IUUIDAware):
    """Marker interface if node is ZODB catalog aware.
    """