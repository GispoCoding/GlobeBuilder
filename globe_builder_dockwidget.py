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
import json
import os
import sys

from PyQt5.QtCore import pyqtSignal, QSettings, pyqtSlot, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from qgis.PyQt import QtWidgets
from qgis.PyQt import uic
from qgis._core import Qgis, QgsMessageLog

from .globe import Globe
from .utils.settings import (NOMINATIM_URL, DEFAULT_MAX_NUMBER_OF_RESULTS, DEFAULT_USE_NE_COUNTRIES,
                             DEFAULT_USE_NE_GRATICULES, DEFAULT_USE_S2_CLOUDLESS, MAX_NAME_PARTS, DEFAULT_ORIGIN)

sys.path.append(os.path.dirname(__file__))
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'globe_builder_dockwidget_base.ui'), resource_suffix='')


class GlobeBuilderDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(GlobeBuilderDockWidget, self).__init__(parent)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.iface = iface
        self.globe = Globe(iface)

        self.network_access_manager = QNetworkAccessManager()
        self.network_access_manager.finished.connect(self.on_search_response)

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
        self.on_radioButtonGeocoding_toggled(self.radioButtonGeocoding.isChecked())

        self.geolocations = {}

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    # Without this annotation the signal is handled twice,
    # see https://stackoverflow.com/questions/14311578/event-signal-is-emmitted-twice-every-time
    @pyqtSlot(bool)
    def on_radioButtonCoordinates_toggled(self, isChecked):
        self.lineEditLonLat.setEnabled(isChecked)

    @pyqtSlot(bool)
    def on_radioButtonGeocoding_toggled(self, isChecked):
        self.lineEditGeocoding.setEnabled(isChecked)
        self.pushButtonSearch.setEnabled(isChecked)
        self.listWidgetGeocodingResults.setEnabled(isChecked)
        self.spinBoxMaxResults.setEnabled(isChecked)

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
            self.geocode(text)

    @pyqtSlot()
    def on_pushButtonLoadData_clicked(self):
        self.globe.load_data(self.checkBoxS2cloudless.isChecked(), self.checkBoxCountries.isChecked(),
                             self.checkBoxGraticules.isChecked())

    @pyqtSlot()
    def on_pushButtonCenter_clicked(self):
        self.globe.set_origin(self.calculate_origin_coordinates())
        self.globe.change_background_color()
        self.globe.change_project_projection_to_azimuthal_orthographic()
        self.globe.add_halo()

    def geocode(self, query):
        self.listWidgetGeocodingResults.clear()
        self.geolocations.clear()

        params = {
            'query': query,
            'limit': self.spinBoxMaxResults.value()
        }
        url = NOMINATIM_URL.format(**params)

        # http://osgeo-org.1560.x6.nabble.com/QGIS-Developer-Do-we-have-a-User-Agent-string-for-QGIS-td5360740.html
        user_agent = QSettings().value("/qgis/networkAndProxy/userAgent", "Mozilla/5.0")
        user_agent += " " if len(user_agent) else ""
        user_agent += "QGIS/{}".format(Qgis.QGIS_VERSION_INT)
        user_agent += " GlobeBuilder-plugin"

        QgsMessageLog.logMessage(url, "GlobeBuilder", Qgis.Info)
        geocoding_request = QNetworkRequest(QUrl(url))
        # https://www.riverbankcomputing.com/pipermail/pyqt/2016-May/037514.html
        geocoding_request.setRawHeader(b"User-Agent", bytes(user_agent, "utf-8"))
        self.network_access_manager.get(geocoding_request)

    def on_search_response(self, search_result):
        error = search_result.error()
        if error == QNetworkReply.NoError:
            bytes_string = search_result.readAll()
            data_string = str(bytes_string, 'utf-8')

            result = json.loads(data_string)

            for f in result['features']:
                name_parts = f['properties']['display_name'].split(",")
                name = "{} ({})".format(",".join(
                    name_parts[0:min(MAX_NAME_PARTS, len(name_parts) - 1)]),
                    name_parts[-1].strip()) if len(name_parts) > 1 else name_parts[0]
                coordinates = f['geometry']['coordinates']
                self.listWidgetGeocodingResults.addItem(name)
                self.geolocations[name] = coordinates
        else:
            QgsMessageLog.logMessage(str(error), "GlobeBuilder", Qgis.Warning)
            QgsMessageLog.logMessage(search_result.errorString(), "GlobeBuilder", Qgis.Warning)

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
        except ValueError as e:
            self.origin = DEFAULT_ORIGIN
            self.iface.messageBar().pushMessage(self.tr(u"Error occurred while parsing center of the globe"),
                                                "{}: {}".format(self.tr("uTraceback"), e),
                                                level=Qgis.Warning, duration=4)
        return coordinates
