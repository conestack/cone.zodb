from cone.zodb import testing
from node.tests import NodeTestCase


class TestIndexing(NodeTestCase):
    layer = testing.zodb_layer
