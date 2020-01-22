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

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QColor
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, Qgis, QgsRasterLayer, QgsFillSymbol, QgsEffectStack, \
    QgsDropShadowEffect, QgsInnerShadowEffect, QgsGeometryGeneratorSymbolLayer, QgsVectorLayer, QgsFeature, QgsGeometry, \
    QgsPointXY

from utils.settings import (LayerConnectionType, HaloDrawMethod, S2CLOUDLESS_WMTS_URL, EARTH_RADIUS, LOCAL_DATA_DIR,
                            DEFAULT_LAYER_CONNECTION_TYPE, NATURAL_EARTH_BASE_URL, AZIMUTHAL_ORTHOGRAPHIC_PROJ4_STR,
                            DEFAULT_HALO_DRAW_METHOD, DEFAULT_NUMBER_OF_SEGMENTS, DEFAULT_ORIGIN)
from utils.utils import tr


class Globe:

    def __init__(self, iface):
        self.iface = iface
        self.origin = DEFAULT_ORIGIN

        crs = QgsCoordinateReferenceSystem()
        crs.createFromId(4326)
        self.wgs84 = crs

    def set_origin(self, coordinates):
        if coordinates is not None:
            self.origin = coordinates

    def load_data(self, load_s2, load_countries, load_graticules):
        existing_layer_names = self.get_existing_layer_names()
        s2_cloudless_layer_name = tr(u'S2 Cloudless 2018')
        if load_s2 and s2_cloudless_layer_name not in existing_layer_names:
            s2_layer = QgsRasterLayer(S2CLOUDLESS_WMTS_URL, s2_cloudless_layer_name, "wms")
            if s2_layer.isValid():
                QgsProject.instance().addMapLayer(s2_layer)
            else:
                self.iface.messageBar().pushMessage(tr(u"Could not add Sentinel 2 Cloudless layer"),
                                                    level=Qgis.Warning, duration=4)
        ne_data = {}
        if load_countries:
            ne_data[tr(u'Countries')] = 'ne_110m_admin_0_countries.geojson'
        if load_graticules:
            ne_data[tr(u'Graticules')] = 'ne_10m_graticules_30.geojson'
        len(ne_data) and self.load_natural_eath_data(ne_data)

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
                layer = self.iface.addVectorLayer(os.path.join(root, source), name, "ogr")
                if layer is None:
                    layer = self.iface.addVectorLayer(os.path.join(LOCAL_DATA_DIR, source), name, "ogr")
                if layer is None:
                    self.iface.messageBar().pushMessage(
                        tr(u"Could not load Natural Earth layer '{}'".format(name)),
                        level=Qgis.Warning, duration=3)
                else:
                    layer.setName(name)

    def change_project_projection_to_azimuthal_orthographic(self):
        # Change to wgs84 to activate the changes in origin
        QgsProject.instance().setCrs(self.wgs84)
        proj4_string = AZIMUTHAL_ORTHOGRAPHIC_PROJ4_STR.format(**self.origin)
        crs = QgsCoordinateReferenceSystem()
        crs.createFromProj4(proj4_string)
        QgsProject.instance().setCrs(crs)

    def change_background_color(self, color=Qt.black):
        new_background_color = QColor(color)

        # Write it to the project (will still need to be saved!)
        instance = QgsProject.instance()
        instance.writeEntry("Gui", "/CanvasColorRedPart", new_background_color.red())
        instance.writeEntry("Gui", "/CanvasColorGreenPart", new_background_color.green())
        instance.writeEntry("Gui", "/CanvasColorBluePart", new_background_color.blue())

        # And apply for the current session
        self.iface.mapCanvas().setCanvasColor(new_background_color)
        self.iface.mapCanvas().refresh()

    @staticmethod
    def get_existing_layer_names():
        return [layer.name() for layer in QgsProject.instance().mapLayers().values()]

    # noinspection PyArgumentList
    @staticmethod
    def set_halo_styles(layer, draw_method):
        renderer = layer.renderer()
        sym = renderer.symbol()

        props = {'color': 'blue'}
        fill_symbol = QgsFillSymbol.createSimple(props)

        # Assign effects
        effect_stack = QgsEffectStack()
        effect_stack.appendEffect(QgsDropShadowEffect.create({'color': 'white'}))
        effect_stack.appendEffect(QgsInnerShadowEffect.create({'color': 'white'}))

        fill_symbol.symbolLayers()[0].setPaintEffect(effect_stack)
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

    def add_halo(self):
        layer_name = tr(u"Halo")

        instance = QgsProject.instance()
        [instance.removeMapLayer(lyr.id()) for lyr in instance.mapLayersByName(layer_name)]

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

        # Assign styles and add to toc
        self.set_halo_styles(layer, draw_method)
        instance.addMapLayer(layer)
