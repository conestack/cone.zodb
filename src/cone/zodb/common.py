from cone.app.security import PrincipalACL
from node.ext.zodb import OOBTNodeAttributes
from node.utils import instance_property
from plumber import default


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
