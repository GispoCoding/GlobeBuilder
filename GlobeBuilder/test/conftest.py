"""
This class contains fixtures and common helper function to keep the test files shorter
"""

import pytest
from qgis.core import QgsProject

from ..core.globe import Globe
from ..qgis_plugin_tools.testing.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
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
    return Globe(iface)
