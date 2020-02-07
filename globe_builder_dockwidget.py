# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GlobeBuilder
                                 A QGIS plugin
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
import sys

from PyQt5.QtCore import pyqtSignal, QSettings, pyqtSlot
from PyQt5.QtGui import QColor
from qgis.PyQt import QtWidgets
from qgis.PyQt import uic
from qgis.core import Qgis, QgsCoordinateTransform, QgsProject

from .globe import Globe
from .utils.geocoder import Geocoder
from .utils.settings import (DEFAULT_MAX_NUMBER_OF_RESULTS, DEFAULT_USE_NE_COUNTRIES,
                             DEFAULT_USE_NE_GRATICULES, DEFAULT_USE_S2_CLOUDLESS, DEFAULT_ORIGIN,
                             DEFAULT_BACKGROUND_COLOR, DEFAULT_HALO_COLOR, DEFAULT_HALO_FILL_COLOR, WGS84)

sys.path.append(os.path.dirname(__file__))
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'globe_builder_dockwidget_base.ui'), resource_suffix='')


class GlobeBuilderDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        self.is_initializing = True

        super(GlobeBuilderDockWidget, self).__init__(parent)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.iface = iface
        self.qgis_instance = QgsProject.instance()
        self.layout_manager = self.qgis_instance.layoutManager()
        self.globe = Globe(iface)
        self.geocoder = Geocoder(lambda results: self.on_geocoding_finished(results))

        # Set default values
        self.spinBoxMaxResults.setValue(
            QSettings().value("/GlobeBuilder/maxNumberOfResults",
                              DEFAULT_MAX_NUMBER_OF_RESULTS,
                              type=int))
        self.checkBoxCountries.setChecked(
            QSettings().value("/GlobeBuilder/useNE-countries",
                              DEFAULT_USE_NE_COUNTRIES,
                              type=bool))
        self.checkBoxGraticules.setChecked(
            QSettings().value("/GlobeBuilder/useNE-graticules",
                              DEFAULT_USE_NE_GRATICULES,
                              type=bool))
        self.checkBoxS2cloudless.setChecked(
            QSettings().value("/GlobeBuilder/useS2cloudless",
                              DEFAULT_USE_S2_CLOUDLESS,
                              type=bool))

        self.lineEditLonLat.setText("{lon}, {lat}".format(**DEFAULT_ORIGIN))
        self.on_radioButtonCoordinates_toggled(self.radioButtonCoordinates.isChecked())
        self.on_radioButtonLayer_toggled(self.radioButtonLayer.isChecked())
        self.on_radioButtonGeocoding_toggled(self.radioButtonGeocoding.isChecked())
        self.on_radioButtonHFill_toggled(self.radioButtonHFill.isChecked())
        self.populate_comboBoxLayouts()

        self.mColorButtonBackground.setColor(DEFAULT_BACKGROUND_COLOR)
        self.mColorButtonHalo.setColor(DEFAULT_HALO_COLOR)
        self.mColorButtonHFill.setColor(DEFAULT_HALO_FILL_COLOR)

        self.geolocations = {}

        # connections
        self.layout_manager.layoutAdded.connect(self.populate_comboBoxLayouts)
        self.layout_manager.layoutRemoved.connect(self.populate_comboBoxLayouts)
        self.layout_manager.layoutRenamed.connect(self.populate_comboBoxLayouts)

        self.is_initializing = False

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    # Without this annotation the signal is handled twice,
    # see https://stackoverflow.com/questions/14311578/event-signal-is-emmitted-twice-every-time
    @pyqtSlot(bool)
    def on_radioButtonCoordinates_toggled(self, is_checked):
        self.lineEditLonLat.setEnabled(is_checked)

    @pyqtSlot(bool)
    def on_radioButtonLayer_toggled(self, is_checked):
        self.mMapLayerComboBox.setEnabled(is_checked)

    @pyqtSlot(bool)
    def on_radioButtonGeocoding_toggled(self, is_checked):
        self.lineEditGeocoding.setEnabled(is_checked)
        self.pushButtonSearch.setEnabled(is_checked)
        self.listWidgetGeocodingResults.setEnabled(is_checked)
        self.spinBoxMaxResults.setEnabled(is_checked)

    @pyqtSlot(bool)
    def on_radioButtonHHalo_toggled(self, is_checked):
        if not self.is_initializing:
            self.add_halo_to_globe()

    @pyqtSlot(bool)
    def on_radioButtonHOutline_toggled(self, is_checked):
        if not self.is_initializing:
            self.add_halo_to_globe()

    @pyqtSlot(bool)
    def on_radioButtonHFill_toggled(self, is_checked):
        self.mColorButtonHFill.setEnabled(is_checked)
        if not self.is_initializing:
            self.add_halo_to_globe()

    @pyqtSlot(int)
    def on_spinBoxMaxResults_valueChanged(self, value):
        QSettings().setValue("/GlobeBuilder/maxNumberOfResults", value)

    def on_checkBoxCountries_stateChanged(self):
        QSettings().setValue("/GlobeBuilder/useNE-countries", self.checkBoxCountries.isChecked())

    def on_checkBoxGraticules_stateChanged(self):
        QSettings().setValue("/GlobeBuilder/useNE-graticules", self.checkBoxGraticules.isChecked())

    def on_checkBoxS2cloudless_stateChanged(self):
        QSettings().setValue("/GlobeBuilder/useS2cloudless", self.checkBoxS2cloudless.isChecked())

    @pyqtSlot()
    def on_pushButtonSearch_clicked(self):
        text = self.lineEditGeocoding.text()
        if len(text.strip()):
            self.listWidgetGeocodingResults.clear()
            self.geolocations.clear()
            self.geocoder.geocode(text, self.spinBoxMaxResults.value())

    @pyqtSlot()
    def on_pushButtonLoadData_clicked(self):
        self.globe.load_data(self.checkBoxS2cloudless.isChecked(), self.checkBoxCountries.isChecked(),
                             self.checkBoxGraticules.isChecked())

    @pyqtSlot()
    def on_pushButtonCenter_clicked(self):
        self.globe.set_origin(self.calculate_origin_coordinates())
        self.globe.change_project_projection_to_azimuthal_orthographic()
        self.add_halo_to_globe()

    @pyqtSlot()
    def on_pushButtonRun_clicked(self):
        self.globe.load_data(self.checkBoxS2cloudless.isChecked(), self.checkBoxCountries.isChecked(),
                             self.checkBoxGraticules.isChecked())
        self.globe.set_origin(self.calculate_origin_coordinates())
        self.globe.change_background_color(self.mColorButtonBackground.color())
        self.mColorButtonBackground.setColor(self.iface.mapCanvas().canvasColor())
        self.globe.change_project_projection_to_azimuthal_orthographic()
        self.add_halo_to_globe()

    @pyqtSlot(QColor)
    def on_mColorButtonBackground_colorChanged(self, color):
        if not self.is_initializing:
            self.globe.change_background_color(color)

    @pyqtSlot(QColor)
    def on_mColorButtonHalo_colorChanged(self, color):
        if not self.is_initializing:
            self.add_halo_to_globe()

    @pyqtSlot(QColor)
    def on_mColorButtonHFill_colorChanged(self, color):
        if not self.is_initializing:
            self.add_halo_to_globe()

    def populate_comboBoxLayouts(self, *args):
        self.comboBoxLayouts.clear()
        for layout in self.layout_manager.layouts():
            self.comboBoxLayouts.addItem(layout.name())
        self.pushButtonAddToLayout.setEnabled(self.comboBoxLayouts.count() > 0)

    def add_halo_to_globe(self):
        self.globe.add_halo(self.radioButtonHHalo.isChecked(), self.mColorButtonHalo.color(),
                            self.get_halo_fill_color())

    def get_halo_fill_color(self):
        return self.mColorButtonHFill.color() if self.radioButtonHFill.isChecked() else None

    def on_geocoding_finished(self, geolocations):
        self.geolocations = geolocations.copy()
        [self.listWidgetGeocodingResults.addItem(name) for name in self.geolocations.keys()]

    def get_geocoded_coordinates(self):
        coordinates = None
        if (len(self.geolocations) and
                self.listWidgetGeocodingResults.count() > 0 and
                self.listWidgetGeocodingResults.currentItem() is not None):
            geolocation = self.listWidgetGeocodingResults.currentItem().text()
            coordinates = self.geolocations.get(geolocation, None)
            coordinates = {'lon': coordinates[0], 'lat': coordinates[1]}

        return coordinates

    def calculate_origin_coordinates(self):
        coordinates = None
        try:
            if self.radioButtonCoordinates.isChecked():
                coordinates = tuple(map(lambda c: float(c.strip()), self.lineEditLonLat.text().split(',')))
                coordinates = {'lon': coordinates[0], 'lat': coordinates[1]}

            elif self.radioButtonGeocoding.isChecked():
                coordinates = self.get_geocoded_coordinates()
                if not coordinates:
                    raise ValueError(self.tr(u"Make sure to select an item from the Geolocation list"))
                coordinates = None

            elif self.radioButtonLayer.isChecked():
                layer = self.mMapLayerComboBox.currentLayer()
                if layer is None:
                    raise ValueError(self.tr(u"Make sure to have at least one layer in the project"))
                center_point = layer.extent().center()

                transformer = QgsCoordinateTransform(layer.crs(), WGS84, self.qgis_instance)
                center_point = transformer.transform(center_point)
                coordinates = {'lon': center_point.x(), 'lat': center_point.y()}


        except ValueError as e:
            self.iface.messageBar().pushMessage(self.tr(u"Error occurred while parsing center of the globe"),
                                                "{}: {}".format(self.tr(u"Traceback"), e),
                                                level=Qgis.Warning, duration=6)
        return coordinates
