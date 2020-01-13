# coding=utf-8
"""Resources test.

"""

__author__ = 'joona@gispo.fi'
__date__ = '2020-01-10'
__copyright__ = 'Copyright 2020, Gispo Ltd.'

import unittest

from qgis.PyQt.QtGui import QIcon


class GlobeBuilderDialogTest(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icon_png(self):
        """Test we can click OK."""
        path = ':/plugins/GlobeBuilder/icon.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())


if __name__ == "__main__":
    suite = unittest.makeSuite(GlobeBuilderResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
