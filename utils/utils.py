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
from PyQt5.QtCore import QCoreApplication
from qgis.core import QgsPrintLayout


def tr(message):
    """Get the translation for a string using Qt translation API.

    We implement this ourselves since we do not inherit QObject.

    :param message: String for translation.
    :type message: str, QString

    :returns: Translated version of message.
    :rtype: QString
    """
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
    return QCoreApplication.translate('GlobeBuilder', message)


def create_layout(layout_name, qgis_instance):
    manager = qgis_instance.layoutManager()
    layouts_list = manager.printLayouts()
    # remove any duplicate layouts
    for layout in layouts_list:
        if layout.name() == layout_name:
            manager.removeLayout(layout)
    layout = QgsPrintLayout(qgis_instance)
    layout.initializeDefaults()
    layout.setName(layout_name)
    manager.addLayout(layout)
    return layout
