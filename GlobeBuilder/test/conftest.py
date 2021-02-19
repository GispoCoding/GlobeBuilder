"""
This class contains fixtures and common helper function to keep the test files shorter
"""

#  Gispo Ltd., hereby disclaims all copyright interest in the program GlobeBuilder
#  Copyright (C) 2020-2021 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of GlobeBuilder.
#
#  GlobeBuilder is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  GlobeBuilder is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with GlobeBuilder.  If not, see <https://www.gnu.org/licenses/>.

import pytest
from qgis.core import QgsProject

from ..core.globe import Globe
from ..definitions.projections import Projections
from ..qgis_plugin_tools.testing.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
# noinspection PyArgumentList
QGIS_INSTANCE = QgsProject.instance()


@pytest.fixture(scope='function')
def new_project() -> None:
    """Initializes new iface project"""
    yield IFACE.newProject()


@pytest.fixture(scope='function')
def qgs_instance():
    return QGIS_INSTANCE


@pytest.fixture(scope='function')
def iface():
    return IFACE


@pytest.fixture(scope='function')
def canvas():
    return CANVAS


@pytest.fixture(scope='function')
def globe(new_project, iface) -> Globe:
    globe = Globe(iface)
    globe.set_projection(Projections.AZIMUTHAL_ORTHOGRAPHIC)
    return globe
