from cone.app.security import PrincipalACL
from node.ext.zodb import OOBTNodeAttributes
from node.utils import instance_property
from plumber import default
from plumber import plumb


class ZODBPrincipalACL(PrincipalACL):
    """Principal ACL for ZODB nodes.
    """

    @plumb
    def __init__(next_, self, *a, **kw):
        next_(self, *a, **kw)
        self.principal_roles

    @default
    @instance_property
    def principal_roles(self):
        return OOBTNodeAttributes(name='principal_roles')


class ZODBEntryPrincipalACL(PrincipalACL):

    @default
    @property
    def principal_roles(self):
        return self.storage.principal_roles
