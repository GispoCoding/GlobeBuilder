# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GlobeBuilder
                                 A QGIS plugin
 This plugin adds Globe view
                              -------------------
        begin                : 2020-01-23
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

from PyQt5.QtCore import QSettings, QUrl
from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply, QNetworkAccessManager
from qgis.core import Qgis, QgsMessageLog

from utils.settings import NOMINATIM_URL, MAX_NAME_PARTS


class Geocoder:
    def __init__(self, callback):
        self.network_access_manager = QNetworkAccessManager()
        self.network_access_manager.finished.connect(self.on_search_response)
        self.callback = callback

    def geocode(self, query, max_results):
        params = {
            'query': query,
            'limit': max_results
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
        result_dict = {}
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
                result_dict[name] = coordinates
        else:
            QgsMessageLog.logMessage(str(error), "GlobeBuilder", Qgis.Warning)
            QgsMessageLog.logMessage(search_result.errorString(), "GlobeBuilder", Qgis.Warning)

        self.callback(result_dict)
