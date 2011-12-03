import os
import tempfile
import shutil
from plumber import plumber
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
from node.parts import UUIDAware
from node.ext.zodb import OOBTNode
from cone.app import root
from cone.app.testing import Security
from cone.zodb import CatalogAware


class ZODBDummyNode(OOBTNode):
    __metaclass__ = plumber
    __plumbing__ = UUIDAware
    
    node_info_name = 'dummytype'
    
    def __init__(self, name=None, parent=None):
        OOBTNode.__init__(self, name=name, parent=parent)
        self.attrs['title'] = 'foo'
        self.state = 'state_1'


class CatalogAwareZODBDummyNode(ZODBDummyNode):
    __metaclass__ = plumber
    __plumbing__ = CatalogAware


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
        storage = FileStorage(os.path.join(self.tempdir, 'Data.fs'))
        if hasattr(self, 'zodb') and self.zodb:
            self.zodb_connection.close()
            self.zodb.close()
        self.zodb = DB(storage)
        self.zodb_connection = self.zodb.open()
    
    def zodb_root(self):
        return self.zodb_connection.root()