# coding=utf-8
"""Globe test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'joona@gispo.fi'
__date__ = '2020-02-05'
__copyright__ = 'Copyright 2020, Gispo Ltd.'

import logging
import sys
import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from qgis.core import QgsProject

from ..qgis_plugin_tools.testing.utilities import get_qgis_app
from ..core.globe import Globe
from ..definitions.settings import (AZIMUTHAL_ORTHOGRAPHIC_PROJ4_STR, DEFAULT_ORIGIN)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
# noinspection PyArgumentList
QGIS_INSTANCE = QgsProject.instance()

LOGGER = logging.getLogger('QGIS')


class GlobeTest(unittest.TestCase):
    """Test Globe logic"""

    def setUp(self):
        """Runs before each test."""
        IFACE.newProject()
        self.globe = Globe(IFACE)

    def tearDown(self):
        """Runs after each test."""

    def test_projection_change_with_default_origin(self):
        """Test if projection really changes"""
        self.globe.change_project_projection_to_azimuthal_orthographic()
        expeted_proj = AZIMUTHAL_ORTHOGRAPHIC_PROJ4_STR.format(**DEFAULT_ORIGIN)
        self.assertEqual(expeted_proj, QGIS_INSTANCE.crs().toProj())

    def test_projection_change_with_custom_origin(self):
        """Test if projection really changes"""
        custom_origin = {'lat': 10, 'lon': 10}
        self.globe.set_origin(custom_origin)
        self.globe.change_project_projection_to_azimuthal_orthographic()
        expeted_proj = AZIMUTHAL_ORTHOGRAPHIC_PROJ4_STR.format(**custom_origin)
        self.assertEqual(expeted_proj, QGIS_INSTANCE.crs().toProj())

    def test_loading_countries(self):
        """Test loading data"""
        self.assertFalse((len(IFACE.getMockLayers())))
        self.globe.load_data(False, True, False, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
        names = get_existing_layer_names()
        self.assertTrue("Countries" in names)

    def test_loading_graticules(self):
        """Test loading data"""
        self.assertFalse((len(IFACE.getMockLayers())))
        self.globe.load_data(False, False, True, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
        names = get_existing_layer_names()
        self.assertTrue("Graticules" in names)

    @unittest.skipIf("pytest" in sys.modules,
                     "WMTS source adding fails when running with pytest")
    def test_loading_s2cloudless(self):
        """Test loading data"""
        self.assertFalse((len(IFACE.getMockLayers())))
        self.globe.load_data(True, False, False, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
        names = get_existing_layer_names()
        self.assertTrue("S2 Cloudless 2018" in names)

    @unittest.skipIf("pytest" in sys.modules,
                     "WMTS source adding fails when running with pytest")
    def test_loading_s2cloudless_countries_and_graticules(self):
        """Test loading data"""
        self.assertFalse((len(IFACE.getMockLayers())))
        self.globe.load_data(True, True, True, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
        names = get_existing_layer_names()
        expected_names = {"Graticules", "S2 Cloudless 2018", "Countries"}
        self.assertEqual(expected_names, names)

    def test_background_color_changing(self):
        """Test if background color really changes"""
        expected_b_color = QColor(Qt.blue)
        self.globe.change_background_color(expected_b_color)
        new_background_color = CANVAS.canvasColor()
        self.assertEqual(expected_b_color, new_background_color)

    def test_adding_halo(self):
        self.globe.add_halo(True, QColor(Qt.blue))
        names = get_existing_layer_names()
        self.assertTrue("Halo" in names)

    def test_group(self):
        group = self.globe.group
        children = QGIS_INSTANCE.layerTreeRoot().children()
        self.assertTrue(group in children)

    def test_group_deletion(self):
        group = self.globe.group
        self.globe.delete_group()
        children = QGIS_INSTANCE.layerTreeRoot().children()
        self.assertFalse(group in children)

    def test_theme_exist_if_items_in_group(self):
        self.globe.load_data(False, False, True, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
        self.globe.refresh_theme()
        self.assertTrue(Globe.THEME_NAME in QGIS_INSTANCE.mapThemeCollection().mapThemes())

    def test_theme_doesnt_exist_group_is_empty(self):
        self.globe.refresh_theme()
        self.assertFalse(Globe.THEME_NAME in QGIS_INSTANCE.mapThemeCollection().mapThemes())


def get_existing_layer_names():
    return {layer.name() for layer in IFACE.getMockLayers() + CANVAS.layers()}


if __name__ == '__main__':
    suite = unittest.makeSuite(GlobeTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)