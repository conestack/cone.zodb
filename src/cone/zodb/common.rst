ZODBPrincipalACL::

    >>> from cone.zodb.testing import ZODBPrincipalACLNode
    >>> node = ZODBPrincipalACLNode()
    >>> node.principal_roles
    <OOBTNodeAttributes object 'principal_roles' at ...>
    
    >>> node.principal_roles['someuser'] = ['manager']
    >>> node.__acl__
    [('Allow', 'someuser', ['cut', 'edit', 'view', 'add', 'change_state', 
    'manage', 'copy', 'paste', 'manage_permissions', 'delete']), 
    ('Allow', 'system.Authenticated', ['view']), 
    ('Allow', 'role:viewer', ['view']), 
    ('Allow', 'role:editor', ['view', 'add', 'edit']), 
    ('Allow', 'role:admin', ['view', 'add', 'edit', 'delete', 'cut', 'copy', 
    'paste', 'manage_permissions', 'change_state']), 
    ('Allow', 'role:owner', ['view', 'add', 'edit', 'delete', 'cut', 'copy', 
    'paste', 'manage_permissions', 'change_state']), 
    ('Allow', 'role:manager', ['view', 'add', 'edit', 'delete', 'cut', 'copy', 
    'paste', 'manage_permissions', 'change_state', 'manage']), 
    ('Allow', 'system.Everyone', ['login']), 
    ('Deny', 'system.Everyone', <pyramid.security.AllPermissionsList object at ...>)]

ZODBEntryPrincipalACL::

    >>> from cone.zodb.testing import (
    ...     ZODBPrincipalACLNode,
    ...     ZODBPrincipalACLEntry,
    ... )
    
    >>> request = layer.new_request()
    >>> node = ZODBPrincipalACLEntry()
    >>> node
    <ZODBPrincipalACLEntry object 'None' at ...>
    
    >>> node.storage
    <ZODBPrincipalACLEntryNode object 'None' at ...>
    
    >>> node.principal_roles
    <OOBTNodeAttributes object 'principal_roles' at ...>
    
    >>> node.storage.principal_roles is node.principal_roles
    True
    
    >>> node.principal_roles['someuser'] = ['manager']
    >>> node.__acl__
    [('Allow', 'someuser', ['cut', 'edit', 'view', 'add', 'change_state', 
    'manage', 'copy', 'paste', 'manage_permissions', 'delete']), 
    ('Allow', 'system.Authenticated', ['view']), 
    ('Allow', 'role:viewer', ['view']), 
    ('Allow', 'role:editor', ['view', 'add', 'edit']), 
    ('Allow', 'role:admin', ['view', 'add', 'edit', 'delete', 'cut', 'copy', 
    'paste', 'manage_permissions', 'change_state']), 
    ('Allow', 'role:owner', ['view', 'add', 'edit', 'delete', 'cut', 'copy', 
    'paste', 'manage_permissions', 'change_state']), 
    ('Allow', 'role:manager', ['view', 'add', 'edit', 'delete', 'cut', 'copy', 
    'paste', 'manage_permissions', 'change_state', 'manage']), 
    ('Allow', 'system.Everyone', ['login']), 
    ('Deny', 'system.Everyone', <pyramid.security.AllPermissionsList object at ...>)]
    
    >>> node.storage.__acl__ == node.__acl__
    True
