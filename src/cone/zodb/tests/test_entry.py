from cone.zodb import testing
from node.tests import NodeTestCase


class TestEntry(NodeTestCase):
    layer = testing.zodb_layer
