from cone.app.interfaces import IWorkflowState
from cone.app.model import AppRoot
from cone.zodb.entry import ZODBEntry
from cone.zodb.entry import ZODBEntryNode
from node.interfaces import IUUIDAware
from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.path import CatalogPathIndex
import datetime


FLOORDATETIME = datetime.datetime(1980, 1, 1)  # XXX tzinfo


def force_dt(value):
    if not isinstance(value, datetime.datetime):
        return FLOORDATETIME
    return value


def zodb_path(node, default=None):
    path = list()
    while True:
        if isinstance(node, ZODBEntryNode):
            node = node.entry
        path.append(node.name)
        if node.parent is None or isinstance(node, ZODBEntry):
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
    return IUUIDAware.providedBy(node) and node.uuid or default


def get_type(node, default):
    if hasattr(node, 'node_info_name'):
        return node.node_info_name
    return default


def get_state(node, default):
    if hasattr(node, 'state'):
        return node.state
    return default


def get_title(node, default):
    if hasattr(node, 'metadata'):
        title = node.metadata.title
        if title:
            return title
    return node.attrs.get('title', default)


def combined_title(node):
    titles = list()
    while True:
        titles.append(node.attrs.get('title', node.name))
        if node.parent is None or isinstance(node, (ZODBEntry, ZODBEntryNode)):
            break
        node = node.parent
    titles.reverse()
    return ' - '.join(titles)


def create_default_catalog():
    catalog = Catalog()
    catalog['uid'] = CatalogFieldIndex(get_uid)
    catalog['type'] = CatalogFieldIndex(get_type)
    catalog['state'] = CatalogFieldIndex(get_state)
    catalog['path'] = CatalogPathIndex(str_zodb_path)
    catalog['app_path'] = CatalogPathIndex(str_app_path)
    catalog['title'] = CatalogFieldIndex(get_title)
    return catalog


def create_default_metadata(node):
    metadata = dict()
    metadata['uid'] = node.uuid
    metadata['path'] = zodb_path(node)
    metadata['app_path'] = app_path(node)
    metadata['title'] = get_title(node, node.name)
    metadata['combined_title'] = combined_title(node)
    if IWorkflowState.providedBy(node):
        metadata['state'] = node.state
    return metadata
