from cone.app.model import AppNode
from cone.app.model import UUIDAttributeAware
from cone.app.security import DEFAULT_ACL
from cone.app.testing import Security
from cone.zodb import CatalogAware
from cone.zodb import CatalogProvidingEntry
from cone.zodb import ZODBEntry
from cone.zodb import ZODBEntryNode
from cone.zodb import ZODBEntryPrincipalACL
from cone.zodb import ZODBPrincipalACL
from node.ext.zodb import OOBTNode
from node.ext.zodb import ZODBNode
from plumber import plumbing
from ZODB.blob import BlobStorage
from ZODB.DB import DB
from ZODB.FileStorage import FileStorage
import os
import shutil
import tempfile


@plumbing(UUIDAttributeAware)
class ZODBDummyNode(OOBTNode):
    node_info_name = 'dummytype'

    def __init__(self, name=None, parent=None):
        OOBTNode.__init__(self, name=name, parent=parent)
        self.attrs['title'] = 'foo'


@plumbing(CatalogAware)
class CatalogAwareZODBNode(ZODBDummyNode):
    pass


@plumbing(CatalogAware)
class CatalogAwareZODBEntryNode(ZODBEntryNode):
    pass


@plumbing(CatalogProvidingEntry)
class CatalogAwareZODBEntry(ZODBEntry):
    node_factory = CatalogAwareZODBEntryNode


@plumbing(CatalogAware, UUIDAttributeAware)
class CatalogIncludedZODBEntryNode(ZODBEntryNode):
    include_entry = True


@plumbing(CatalogProvidingEntry)
class CatalogIncludedZODBEntry(ZODBEntry):
    node_factory = CatalogIncludedZODBEntryNode


@plumbing(AppNode, ZODBPrincipalACL)
class ZODBPrincipalACLNode(ZODBNode):
    pass


@plumbing(ZODBPrincipalACL)
class ZODBPrincipalACLEntryNode(ZODBEntryNode):

    @property
    def __acl__(self):
        return DEFAULT_ACL


@plumbing(ZODBEntryPrincipalACL)
class ZODBPrincipalACLEntry(ZODBEntry):
    node_factory = ZODBPrincipalACLEntryNode


class ZODBLayer(Security):

    def setUp(self, args=None):
        self.tempdir = tempfile.mkdtemp()
        self.zodb_connection = None
        self.init_zodb()
        super(ZODBLayer, self).setUp(args=args)

    def tearDown(self):
        super(ZODBLayer, self).tearDown()
        self.zodb.close()
        shutil.rmtree(self.tempdir)

    def new_request(self, type=None, xhr=False):
        request = super(ZODBLayer, self).new_request(type=type, xhr=xhr)
        setattr(request, '_primary_zodb_conn', self.zodb_connection)
        return request

    def init_zodb(self):
        if hasattr(self, 'zodb') and self.zodb:
            self.zodb_connection.close()
            self.zodb.close()
        filestorage_dir = os.path.join(self.tempdir, 'Data.fs')
        filestorage = FileStorage(filestorage_dir)
        blobstorage_dir = os.path.join(self.tempdir, 'blobstorage')
        blobstorage = BlobStorage(
            blobstorage_dir,
            filestorage,
            layout='automatic'
        )
        self.zodb = DB(blobstorage)
        self.zodb_connection = self.zodb.open()

    def zodb_root(self):
        return self.zodb_connection.root()


zodb_layer = ZODBLayer()
