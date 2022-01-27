from cone.zodb import testing
from cone.zodb.testing import ZODBPrincipalACLEntry
from cone.zodb.testing import ZODBPrincipalACLNode
from cone.zodb.testing import ZODBPrincipalACLEntryNode
from node.ext.zodb import OOBTNodeAttributes
from node.tests import NodeTestCase
from pyramid.security import ALL_PERMISSIONS


class TestCommon(NodeTestCase):
    layer = testing.zodb_layer

    def test_ZODBPrincipalACL(self):
        node = ZODBPrincipalACLNode()
        self.assertTrue(isinstance(node.principal_roles, OOBTNodeAttributes))
        self.assertEqual(node.principal_roles.name, 'principal_roles')

        node.principal_roles['someuser'] = ['manager']
        acl = node.__acl__

        self.assertEqual(acl[0][0], 'Allow')
        self.assertEqual(acl[0][1], 'someuser')
        self.assertEqual(sorted(acl[0][2]), [
            'add', 'change_order', 'change_state', 'copy', 'cut', 'delete',
            'edit', 'list', 'manage', 'manage_permissions', 'paste', 'view'
        ])

        self.assertEqual(acl[1][0], 'Allow')
        self.assertEqual(acl[1][1], 'system.Authenticated')
        self.assertEqual(sorted(acl[1][2]), ['view'])

        self.assertEqual(acl[2][0], 'Allow')
        self.assertEqual(acl[2][1], 'role:viewer')
        self.assertEqual(sorted(acl[2][2]), ['list', 'view'])

        self.assertEqual(acl[3][0], 'Allow')
        self.assertEqual(acl[3][1], 'role:editor')
        self.assertEqual(
            sorted(acl[3][2]),
            ['add', 'change_order', 'edit', 'list', 'view']
        )

        self.assertEqual(acl[4][0], 'Allow')
        self.assertEqual(acl[4][1], 'role:admin')
        self.assertEqual(sorted(acl[4][2]), [
            'add', 'change_order', 'change_state', 'copy', 'cut', 'delete',
            'edit', 'list', 'manage_permissions', 'paste', 'view'
        ])

        self.assertEqual(acl[5][0], 'Allow')
        self.assertEqual(acl[5][1], 'role:manager')
        self.assertEqual(sorted(acl[5][2]), [
            'add', 'change_order', 'change_state', 'copy', 'cut', 'delete',
            'edit', 'list', 'manage', 'manage_permissions', 'paste', 'view'
        ])

        self.assertEqual(acl[6][0], 'Allow')
        self.assertEqual(acl[6][1], 'role:owner')
        self.assertEqual(sorted(acl[6][2]), [
            'add', 'change_order', 'change_state', 'copy', 'cut', 'delete',
            'edit', 'list', 'manage_permissions', 'paste', 'view'
        ])

        self.assertEqual(acl[7][0], 'Allow')
        self.assertEqual(acl[7][1], 'system.Everyone')
        self.assertEqual(sorted(acl[7][2]), ['login'])

        self.assertEqual(acl[8][0], 'Deny')
        self.assertEqual(acl[8][1], 'system.Everyone')
        self.assertEqual(acl[8][2], ALL_PERMISSIONS)

    def test_ZODBEntryPrincipalACL(self):
        self.layer.new_request()
        node = ZODBPrincipalACLEntry()
        self.assertTrue(isinstance(node.storage, ZODBPrincipalACLEntryNode))

        self.assertTrue(isinstance(node.principal_roles, OOBTNodeAttributes))
        self.assertEqual(node.principal_roles.name, 'principal_roles')
        self.assertTrue(node.storage.principal_roles is node.principal_roles)

        node.principal_roles['someuser'] = ['manager']
        acl = node.__acl__

        self.assertTrue(node.storage.__acl__ == node.__acl__)

        self.assertEqual(acl[0][0], 'Allow')
        self.assertEqual(acl[0][1], 'someuser')
        self.assertEqual(sorted(acl[0][2]), [
            'add', 'change_order', 'change_state', 'copy', 'cut', 'delete',
            'edit', 'list', 'manage', 'manage_permissions', 'paste', 'view'
        ])

        self.assertEqual(acl[1][0], 'Allow')
        self.assertEqual(acl[1][1], 'system.Authenticated')
        self.assertEqual(sorted(acl[1][2]), ['view'])

        self.assertEqual(acl[2][0], 'Allow')
        self.assertEqual(acl[2][1], 'role:viewer')
        self.assertEqual(sorted(acl[2][2]), ['list', 'view'])

        self.assertEqual(acl[3][0], 'Allow')
        self.assertEqual(acl[3][1], 'role:editor')
        self.assertEqual(
            sorted(acl[3][2]),
            ['add', 'change_order', 'edit', 'list', 'view']
        )

        self.assertEqual(acl[4][0], 'Allow')
        self.assertEqual(acl[4][1], 'role:admin')
        self.assertEqual(sorted(acl[4][2]), [
            'add', 'change_order', 'change_state', 'copy', 'cut', 'delete',
            'edit', 'list', 'manage_permissions', 'paste', 'view'
        ])

        self.assertEqual(acl[5][0], 'Allow')
        self.assertEqual(acl[5][1], 'role:manager')
        self.assertEqual(sorted(acl[5][2]), [
            'add', 'change_order', 'change_state', 'copy', 'cut', 'delete',
            'edit', 'list', 'manage', 'manage_permissions', 'paste', 'view'
        ])

        self.assertEqual(acl[6][0], 'Allow')
        self.assertEqual(acl[6][1], 'role:owner')
        self.assertEqual(sorted(acl[6][2]), [
            'add', 'change_order', 'change_state', 'copy', 'cut', 'delete',
            'edit', 'list', 'manage_permissions', 'paste', 'view'
        ])

        self.assertEqual(acl[7][0], 'Allow')
        self.assertEqual(acl[7][1], 'system.Everyone')
        self.assertEqual(sorted(acl[7][2]), ['login'])

        self.assertEqual(acl[8][0], 'Deny')
        self.assertEqual(acl[8][1], 'system.Everyone')
        self.assertEqual(acl[8][2], ALL_PERMISSIONS)
