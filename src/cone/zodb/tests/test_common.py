from cone.zodb import testing
from node.tests import NodeTestCase


class TestCommon(NodeTestCase):
    layer = testing.zodb_layer
