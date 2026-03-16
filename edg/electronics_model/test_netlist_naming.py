import unittest

from ..core import TransformUtil
from .NetlistGenerator import NetlistTransform


class NetlistNameTestCase(unittest.TestCase):
    def test_net_name_ordering(self) -> None:
        path_block = TransformUtil.Path.empty().append_block("block")
        path_link = TransformUtil.Path.empty().append_link("link")
        path_porta = TransformUtil.Path.empty().append_block("block").append_port("a")
        path_portb = TransformUtil.Path.empty().append_block("block").append_port("a")
        order = {path_block: 0,
                 path_link: 1,
                 path_porta: 2,
                 path_portb: 3}
        self.assertEqual(NetlistTransform.name_net([path_block, path_portb, path_porta, path_link], order), path_link)
        self.assertEqual(NetlistTransform.name_net([path_block, path_portb, path_porta], order), path_block)
        self.assertEqual(NetlistTransform.name_net([path_portb, path_porta], order), path_porta)
