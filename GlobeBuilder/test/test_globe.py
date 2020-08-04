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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from .conftest import QGIS_INSTANCE, IFACE, CANVAS
from ..core.globe import Globe
from ..definitions.projections import Projections
from ..definitions.settings import (DEFAULT_ORIGIN)


def test_projection_change_with_default_origin(globe):
    """Test if projection really changes"""
    globe.set_projection(Projections.AZIMUTHAL_ORTHOGRAPHIC)
    globe.change_project_projection()
    expeted_proj = Projections.AZIMUTHAL_ORTHOGRAPHIC.value.proj_str(DEFAULT_ORIGIN)
    assert QGIS_INSTANCE.crs().toProj() == expeted_proj


def test_projection_change_with_custom_origin(globe):
    """Test if projection really changes"""
    custom_origin = {'lat': 10, 'lon': 10}
    globe.set_origin(custom_origin)
    globe.change_project_projection()
    expeted_proj = Projections.AZIMUTHAL_ORTHOGRAPHIC.value.proj_str(custom_origin)
    assert QGIS_INSTANCE.crs().toProj() == expeted_proj


def test_loading_countries(globe):
    """Test loading data"""
    assert len(IFACE.getMockLayers()) == 0
    globe.load_data(False, True, False, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
    names = get_existing_layer_names()
    assert "Countries" in names


def test_loading_graticules(globe):
    """Test loading data"""
    assert len(IFACE.getMockLayers()) == 0
    globe.load_data(False, False, True, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
    names = get_existing_layer_names()
    assert "Graticules" in names


def test_loading_s2cloudless(globe):
    """Test loading data"""
    assert len(IFACE.getMockLayers()) == 0
    globe.load_data(True, False, False, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
    names = get_existing_layer_names()
    assert "S2 Cloudless 2018" in names


def test_loading_s2cloudless_countries_and_graticules(globe):
    """Test loading data"""
    assert len(IFACE.getMockLayers()) == 0
    globe.load_data(True, True, True, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
    names = get_existing_layer_names()
    expected_names = {"Graticules", "S2 Cloudless 2018", "Countries"}
    assert names == expected_names


def test_background_color_changing(globe):
    """Test if background color really changes"""
    expected_b_color = QColor(Qt.blue)
    globe.change_background_color(expected_b_color)
    new_background_color = CANVAS.canvasColor()
    assert new_background_color == expected_b_color


def test_adding_halo(globe):
    globe.add_halo(True, QColor(Qt.blue))
    names = get_existing_layer_names()
    assert "Halo" in names


def test_group(globe):
    group = globe.group
    children = QGIS_INSTANCE.layerTreeRoot().children()
    assert group in children


def test_group_deletion(globe):
    group = globe.group
    globe.delete_group()
    children = QGIS_INSTANCE.layerTreeRoot().children()
    assert group not in children


def test_theme_exist_if_items_in_group(globe):
    globe.load_data(False, False, True, QColor(Qt.blue), QColor(Qt.blue), None, '50m', 10)
    globe.refresh_theme()
    assert Globe.THEME_NAME in QGIS_INSTANCE.mapThemeCollection().mapThemes()


def test_theme_doesnt_exist_group_is_empty(globe):
    globe.refresh_theme()
    assert Globe.THEME_NAME not in QGIS_INSTANCE.mapThemeCollection().mapThemes()


def get_existing_layer_names():
    return {layer.name() for layer in IFACE.getMockLayers() + CANVAS.layers()}
