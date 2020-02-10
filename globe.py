# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GlobeBuilder
                                 A QGIS plugin
 This plugin adds Globe view
                              -------------------
        begin                : 2020-01-22
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Gispo Ltd.
        email                : joona@gispo.fi
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QColor
from qgis.core import (QgsProject, QgsCoordinateReferenceSystem, Qgis, QgsRasterLayer, QgsFillSymbol, QgsEffectStack,
                       QgsDropShadowEffect, QgsInnerShadowEffect, QgsGeometryGeneratorSymbolLayer, QgsVectorLayer,
                       QgsFeature, QgsGeometry, QgsPointXY, QgsMapThemeCollection, QgsLayoutItemMap,
                       QgsMapSettings, QgsRectangle, QgsLayoutPoint, QgsUnitTypes, QgsLayoutSize)

from .utils.settings import (LayerConnectionType, HaloDrawMethod, S2CLOUDLESS_WMTS_URL, EARTH_RADIUS, LOCAL_DATA_DIR,
                             DEFAULT_LAYER_CONNECTION_TYPE, NATURAL_EARTH_BASE_URL, AZIMUTHAL_ORTHOGRAPHIC_PROJ4_STR,
                             DEFAULT_HALO_DRAW_METHOD, DEFAULT_NUMBER_OF_SEGMENTS, DEFAULT_ORIGIN, TRANSPARENT_COLOR,
                             WGS84)
from .utils.utils import tr


class Globe:
    THEME_NAME = tr(u"Globe")
    GROUP_NAME = tr(u"Globe")

    def __init__(self, iface, origin=DEFAULT_ORIGIN):
        self.iface = iface
        self.origin = origin
        self.qgis_instance = QgsProject.instance()

    @property
    def group(self):
        root = self.qgis_instance.layerTreeRoot()
        groups = tuple(filter(lambda g: g.name() == Globe.GROUP_NAME,
                              filter(root.isGroup, root.children())))
        if len(groups) == 1:
            return groups[0]
        else:
            return root.addGroup(Globe.GROUP_NAME)

    def set_origin(self, coordinates):
        if coordinates is not None:
            self.origin = coordinates

    def set_group_visibility(self, is_visible):
        self.group.setItemVisibilityCheckedRecursive(is_visible)

    def load_data(self, load_s2, load_countries, load_graticules):
        existing_layer_names = self.get_existing_layer_names()
        s2_cloudless_layer_name = tr(u'S2 Cloudless 2018')
        if load_s2 and s2_cloudless_layer_name not in existing_layer_names:
            s2_layer = QgsRasterLayer(S2CLOUDLESS_WMTS_URL, s2_cloudless_layer_name, "wms")
            if s2_layer.isValid():
                self.insert_layer_to_group(s2_layer)
            else:
                self.iface.messageBar().pushMessage(tr(u"Could not add Sentinel 2 Cloudless layer"),
                                                    level=Qgis.Warning, duration=4)
        ne_data = {}
        if load_countries:
            ne_data[tr(u'Countries')] = 'ne_110m_admin_0_countries.geojson'
        if load_graticules:
            ne_data[tr(u'Graticules')] = 'ne_10m_graticules_30.geojson'
        len(ne_data) and self.load_natural_eath_data(ne_data)
        self.iface.mapCanvas().refresh()

    def load_natural_eath_data(self, ne_data):
        # TODO: resolution
        existing_layer_names = self.get_existing_layer_names()

        connection_type = LayerConnectionType(
            QSettings().value("/GlobeBuilder/layerConnectionType", DEFAULT_LAYER_CONNECTION_TYPE.value,
                              type=int))

        if connection_type == LayerConnectionType.local:
            root = LOCAL_DATA_DIR
        else:
            root = NATURAL_EARTH_BASE_URL

        for name, source in ne_data.items():
            if name not in existing_layer_names:

                layer = QgsVectorLayer(os.path.join(root, source), name, "ogr")
                if layer is None:
                    layer = QgsVectorLayer(os.path.join(LOCAL_DATA_DIR, source), name, "ogr")
                if layer is None:
                    self.iface.messageBar().pushMessage(
                        tr(u"Could not load Natural Earth layer '{}'".format(name)),
                        level=Qgis.Warning, duration=3)
                else:
                    layer.setName(name)
                    self.insert_layer_to_group(layer)

    def insert_layer_to_group(self, layer, index=0):
        self.qgis_instance.addMapLayer(layer, False)
        self.group.insertLayer(index, layer)

    def change_project_projection_to_azimuthal_orthographic(self):
        # Change to wgs84 to activate the changes in origin
        self.qgis_instance.setCrs(WGS84)
        proj4_string = AZIMUTHAL_ORTHOGRAPHIC_PROJ4_STR.format(**self.origin)
        crs = QgsCoordinateReferenceSystem()
        crs.createFromProj4(proj4_string)
        self.qgis_instance.setCrs(crs)

    def change_background_color(self, new_background_color):
        # Write it to the project (will still need to be saved!)
        self.qgis_instance.writeEntry("Gui", "/CanvasColorRedPart", new_background_color.red())
        self.qgis_instance.writeEntry("Gui", "/CanvasColorGreenPart", new_background_color.green())
        self.qgis_instance.writeEntry("Gui", "/CanvasColorBluePart", new_background_color.blue())

        # And apply for the current session
        self.iface.mapCanvas().setCanvasColor(new_background_color)
        self.iface.mapCanvas().refresh()

    @staticmethod
    def get_existing_layer_names():
        return [layer.name() for layer in QgsProject.instance().mapLayers().values()]

    # noinspection PyArgumentList
    @staticmethod
    def set_halo_styles(layer, draw_method, stroke_color, use_effects, fill_color=None):
        renderer = layer.renderer()
        sym = renderer.symbol()

        props = {'color': 'blue'}
        fill_symbol = QgsFillSymbol.createSimple(props)
        fill_symbol_layer = fill_symbol.symbolLayers()[0]
        fill_symbol_layer.setStrokeColor(stroke_color)
        if fill_color is not None:
            fill_symbol_layer.setColor(fill_color)
        elif not use_effects:
            fill_symbol_layer.setColor(TRANSPARENT_COLOR)

        if use_effects:
            # Assign effects
            effect_stack = QgsEffectStack()
            drop_shdw = QgsDropShadowEffect()
            drop_shdw.setColor(stroke_color)
            inner_shdw = QgsInnerShadowEffect()
            inner_shdw.setColor(stroke_color)
            effect_stack.appendEffect(drop_shdw)
            effect_stack.appendEffect(inner_shdw)

            fill_symbol_layer.setPaintEffect(effect_stack)
        if draw_method == HaloDrawMethod.buffered_point:
            renderer.setSymbol(fill_symbol)
        else:
            geom_generator_sl = QgsGeometryGeneratorSymbolLayer.create({
                'SymbolType': 'Fill',
                'geometryModifier': 'buffer($geometry, {:d})'.format(EARTH_RADIUS)
            })
            geom_generator_sl.setSubSymbol(fill_symbol)
            sym.changeSymbolLayer(0, geom_generator_sl)

        layer.triggerRepaint()
        return layer

    def add_halo(self, use_effects, stroke_color, fill_color=None, halo_with_fill=False):
        layer_name = tr(u"Halo")

        if halo_with_fill:
            self.add_halo(True, stroke_color)
        else:
            [self.qgis_instance.removeMapLayer(lyr.id()) for lyr in self.qgis_instance.mapLayersByName(layer_name)]

        draw_method = HaloDrawMethod(
            QSettings().value("/GlobeBuilder/haloDrawMethod", DEFAULT_HALO_DRAW_METHOD.value,
                              type=str))
        proj4_string = AZIMUTHAL_ORTHOGRAPHIC_PROJ4_STR.format(**self.origin)
        # Block signals required to prevent the pop up asking about the crs change
        self.iface.mainWindow().blockSignals(True)
        layer = QgsVectorLayer(draw_method.value, layer_name, "memory")
        crs = layer.crs()
        crs.createFromProj4(proj4_string)
        layer.setCrs(crs)
        self.iface.mainWindow().blockSignals(False)

        feature = QgsFeature()
        geom = QgsGeometry.fromPointXY(QgsPointXY(self.origin['lat'], self.origin['lon']))
        if draw_method == HaloDrawMethod.buffered_point:
            geom = geom.buffer(EARTH_RADIUS, DEFAULT_NUMBER_OF_SEGMENTS)
        feature.setGeometry(geom)
        provider = layer.dataProvider()
        layer.startEditing()
        provider.addFeatures([feature])
        layer.commitChanges()

        # Assign styles and to map (but not toc yet)
        self.set_halo_styles(layer, draw_method, stroke_color, use_effects, fill_color)
        self.qgis_instance.addMapLayer(layer, False)

        index = 0 if use_effects else -1
        # Remove if certain that group will be used with Halo
        # tree_root = self.qgis_instance.layerTreeRoot()
        # tree_root.insertChildNode(index, QgsLayerTreeLayer(layer))

        self.insert_layer_to_group(layer, index)

    def refresh_theme(self):
        theme_collection = self.qgis_instance.mapThemeCollection()
        layers = [layer.layer() for layer in self.group.findLayers()]
        if Globe.THEME_NAME not in theme_collection.mapThemes():
            theme_collection.removeMapTheme(Globe.THEME_NAME)
        if len(layers):
            map_theme_record = QgsMapThemeCollection.MapThemeRecord()
            map_theme_record.setLayerRecords([QgsMapThemeCollection.MapThemeLayerRecord(layer) for layer in layers])
            theme_collection.insert(Globe.THEME_NAME, map_theme_record)

    def add_to_layout(self, layout, background_color=QColor(255, 255, 255, 0)):
        '''
        Inspired by https://opensourceoptions.com/blog/pyqgis-create-and-print-a-map-layout-with-python/
        '''
        layers = [layer.layer() for layer in self.group.findLayers()]
        # create map item in the layout
        map = QgsLayoutItemMap(layout)
        map.setRect(20, 20, 20, 20)
        # set the map extent
        ms = QgsMapSettings()
        ms.setLayers(layers)  # set layers to be mapped
        crs = QgsCoordinateReferenceSystem()
        crs.createFromProj4(AZIMUTHAL_ORTHOGRAPHIC_PROJ4_STR.format(**self.origin))
        map.setCrs(crs)
        map.setFollowVisibilityPreset(True)
        map.setFollowVisibilityPresetName(Globe.THEME_NAME)
        rect = QgsRectangle(ms.fullExtent())

        ms.setExtent(rect)
        map.setExtent(rect)
        map.setBackgroundColor(background_color)
        layout.addLayoutItem(map)
        map.attemptMove(QgsLayoutPoint(5, 20, QgsUnitTypes.LayoutMillimeters))
        map.attemptResize(QgsLayoutSize(80, 80, QgsUnitTypes.LayoutMillimeters))
