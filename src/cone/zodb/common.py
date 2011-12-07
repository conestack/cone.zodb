from plumber import default
from node.utils import instance_property
from node.ext.zodb import OOBTNodeAttributes
from cone.app.security import PrincipalACL


class ZODBPrincipalACL(PrincipalACL):
    """Principal ACL for ZODB nodes.
    """
    
    @default
    @instance_property
    def principal_roles(self):
        return OOBTNodeAttributes('principal_roles')


class ZODBEntryPrincipalACL(PrincipalACL):
    
    @default
    @instance_property
    def principal_roles(self):
        return self.storage.principal_roles