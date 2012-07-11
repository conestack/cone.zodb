import os
import tempfile
import shutil
from plumber import (
    plumber,
    default,
)
from ZODB.FileStorage import FileStorage
from ZODB.blob import BlobStorage
from ZODB.DB import DB
from node.ext.zodb import (
    ZODBNode,
    OOBTNode,
)
from cone.app import root
from cone.app.testing import Security
from cone.app.model import (
    AppNode,
    UUIDAttributeAware,
)
from cone.app.security import DEFAULT_ACL
from cone.zodb import (
    ZODBEntry,
    ZODBEntryNode,
    ZODBPrincipalACL,
    ZODBEntryPrincipalACL,
    CatalogAware,
    CatalogProvidingEntry,
)


class ZODBDummyNode(OOBTNode):
    __metaclass__ = plumber
    __plumbing__ = UUIDAttributeAware
    
    node_info_name = 'dummytype'
    
    def __init__(self, name=None, parent=None):
        OOBTNode.__init__(self, name=name, parent=parent)
        self.attrs['title'] = 'foo'


class CatalogAwareZODBNode(ZODBDummyNode):
    __metaclass__ = plumber
    __plumbing__ = CatalogAware


class CatalogAwareZODBEntryNode(ZODBEntryNode):
    __metaclass__ = plumber
    __plumbing__ = CatalogAware


class CatalogAwareZODBEntry(ZODBEntry):
    __metaclass__ = plumber
    __plumbing__ = CatalogProvidingEntry
    node_factory = CatalogAwareZODBEntryNode


class ZODBPrincipalACLNode(ZODBNode):
    __metaclass__ = plumber
    __plumbing__ = AppNode, ZODBPrincipalACL

    
class ZODBPrincipalACLEntryNode(ZODBEntryNode):
    __metaclass__ = plumber
    __plumbing__ = ZODBPrincipalACL
    
    @property
    def __acl__(self):
        return DEFAULT_ACL
   
    
class ZODBPrincipalACLEntry(ZODBEntry):
    __metaclass__ = plumber
    __plumbing__ = ZODBEntryPrincipalACL
    node_factory = ZODBPrincipalACLEntryNode


class ZODBLayer(Security):

    def setUp(self, args=None):
        super(ZODBLayer, self).make_app()
        self.tempdir = tempfile.mkdtemp()
        self.zodb_connection = None
        self.init_zodb()

    def tearDown(self):
        super(ZODBLayer, self).tearDown()
        self.zodb.close()
        shutil.rmtree(self.tempdir)

    def new_request(self):
        request = super(ZODBLayer, self).new_request()
        request.environ['repoze.zodbconn.connection'] = self.zodb_connection
        return request
    
    def init_zodb(self):
        if hasattr(self, 'zodb') and self.zodb:
            self.zodb_connection.close()
            self.zodb.close()
        filestorage_dir = os.path.join(self.tempdir, 'Data.fs')
        filestorage = FileStorage(filestorage_dir)
        blobstorage_dir = os.path.join(self.tempdir, 'blobstorage')
        blobstorage = BlobStorage(blobstorage_dir, filestorage,
                                  layout='automatic')
        self.zodb = DB(blobstorage)
        self.zodb_connection = self.zodb.open()
    
    def zodb_root(self):
        return self.zodb_connection.root()