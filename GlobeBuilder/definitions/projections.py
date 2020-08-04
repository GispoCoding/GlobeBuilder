from enum import Enum
from typing import Tuple

from GlobeBuilder.qgis_plugin_tools.tools.i18n import tr


class Projection:

    def __init__(self, name: str, proj_str: str, min_proj_version: Tuple[int, int] = (0, 0)):
        self.name = name
        self.proj_str_raw = proj_str
        self.min_proj = min_proj_version

    def proj_str(self, origin: {str: float}) -> str:
        return self.proj_str_raw.format(**origin)


class Projections(Enum):
    AZIMUTHAL_ORTHOGRAPHIC = Projection(tr(u'Azimuthal Orthographic'),
                                        '+proj=ortho +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0 +a=6370997 +b=6370997 +units=m +no_defs')
    # https://www.gislounge.com/how-to-use-the-equal-earth-projection-using-qgis-on-the-mac/
    EQUAL_EARTH = Projection(tr(u'Equal Earth'), '+proj=eqearth +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs', (5, 2))

    # '+proj=eqearth +lon_0={lon} +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs' # Unfortunately this causes rendering artifacts

    # HAMMER_ECKERT = 'https://proj.org/operations/projections/hammer.html'
    # EULER = 'https://proj.org/operations/projections/euler.html'
    # EKC = 'https://proj.org/operations/projections/eck1.html'
    # ALBERTS = 'https://proj.org/operations/projections/aea.html'
    # AITOFF = 'https://proj.org/operations/projections/aitoff.html'

    @staticmethod
    def proj_from_id(tr_name: str):
        for projection in Projections:
            if projection.value.name == tr_name:
                return projection
