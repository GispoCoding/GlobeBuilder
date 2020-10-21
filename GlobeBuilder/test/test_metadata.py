from ..qgis_plugin_tools.tools.resources import slug_name


def test_meta():
    tt = slug_name()
    assert tt == 'GlobeBuilder'
