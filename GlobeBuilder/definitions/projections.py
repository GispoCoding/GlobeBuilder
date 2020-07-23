from enum import Enum
from typing import Tuple

from GlobeBuilder.qgis_plugin_tools.tools.i18n import tr


class Projection(Enum):
    AZIMUTHAL_ORTHOGRAPHIC = {'name': tr(u'Azimuthal Orthographic'),
                              'proj_str': '+proj=ortho +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0 +a=6370997 +b=6370997 +units=m +no_defs'
                              }
    # https://www.gislounge.com/how-to-use-the-equal-earth-projection-using-qgis-on-the-mac/
    EQUAL_EARTH = {'name': tr(u'Equal Earth'), 'min_proj': (5, 2),
                   'proj_str': '+proj=eqearth +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
                   # '+proj=eqearth +datum=WGS84 +wktext'
                   # '+proj=eqearth +lon_0={lon} +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs' # Unfortunately this causes rendering artifacts
                   }

    @staticmethod
    def proj_from_id(tr_name: str):
        for projection in Projection:
            if projection.tr_name == tr_name:
                return projection

    @property
    def tr_name(self) -> str:
        return self.value['name']

    @property
    def min_proj(self) -> Tuple[int, int]:
        return self.value.get('min_proj', (0, 0))

    def proj_str(self, origin: {str: float}) -> str:
        return self.value['proj_str'].format(**origin)
