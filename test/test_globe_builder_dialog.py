# coding=utf-8
"""Dialog test.

"""

__author__ = 'joona@gispo.fi'
__date__ = '2020-01-10'
__copyright__ = 'Copyright 2020, Gispo Ltd.'

import unittest

from qgis.PyQt.QtGui import QDialogButtonBox, QDialog
from utilities import get_qgis_app

from globe_builder_dialog import GlobeBuilderDialog

QGIS_APP = get_qgis_app()


class GlobeBuilderDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = GlobeBuilderDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok(self):
        """Test we can click OK."""

        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)


if __name__ == "__main__":
    suite = unittest.makeSuite(GlobeBuilderDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
