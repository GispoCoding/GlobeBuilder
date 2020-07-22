# coding=utf-8
"""Safe Translations Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from ..qgis_plugin_tools.tools.resources import resources_path

__author__ = 'ismailsunni@yahoo.co.id'
__date__ = '12/10/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os

from PyQt5.QtCore import QCoreApplication, QTranslator


def test_translations(new_project):
    """Test that translations work."""
    if 'LANG' in iter(os.environ.keys()):
        os.environ.__delitem__('LANG')
    translator = QTranslator()
    translator.load(resources_path("i18n", 'fi.qm'))
    QCoreApplication.installTranslator(translator)

    expected_message = 'Hyvää huomenta'
    real_message = QCoreApplication.translate("@default", 'Good morning')
    assert real_message == expected_message
