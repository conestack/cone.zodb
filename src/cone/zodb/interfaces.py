from node.ext.zodb import IZODBNode
from node.interfaces import IMappingStorage
from node.interfaces import IUUIDAware


class IZODBEntry(IMappingStorage):
    """Marker interface for ZODB entry. ``storage`` attribute contains a
    ``IZODBEntryNode`` implementing instance.
    """


class IZODBEntryNode(IZODBNode):
    """Marker interface for first level ZODB nodes.
    """


class ICatalogAware(IUUIDAware):
    """Marker interface if node is ZODB catalog aware.
    """
