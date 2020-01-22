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

import enum
import os


class LayerConnectionType(enum.Enum):
    local = 1
    url = 2


class BorderDrawMethod(enum.Enum):
    geometry_generator = "Point"
    buffered_point = "Polygon"


NATURAL_EARTH_BASE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson"
S2CLOUDLESS_WMTS_URL = "url=https://tiles.maps.eox.at/wmts?SERVICE%3DWMTS%26REQUEST%3DGetCapabilities&contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/jpeg&layers=s2cloudless-2018&styles=default&tileMatrixSet=WGS84"
LOCAL_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DEFAULT_ORIGIN = {'lat': 42.5, 'lon': 0.5}
AZIMUTHAL_ORTHOGRAPHIC_PROJ4_STR = '+proj=ortho +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0 +a=6370997 +b=6370997 +units=m +no_defs'
EARTH_RADIUS = 6370997
DEFAULT_NUMBER_OF_SEGMENTS = 64
DEFAULT_LAYER_CONNECTION_TYPE = LayerConnectionType.local
DEFAULT_BORDER_DRAW_METHOD = BorderDrawMethod.buffered_point

# UI
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search/{query}?limit={limit}&format=geojson"
DEFAULT_MAX_NUMBER_OF_RESULTS = 5
MAX_NAME_PARTS = 3
DEFAULT_USE_NE_COUNTRIES = True
DEFAULT_USE_NE_GRATICULES = False
DEFAULT_USE_S2_CLOUDLESS = False
