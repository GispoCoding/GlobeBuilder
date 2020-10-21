#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob

from qgis_plugin_tools.infrastructure.plugin_maker import PluginMaker

'''
#################################################
# Edit the following to match the plugin
#################################################
'''

py_files = (
        [fil for fil in glob.glob("**/*.py", recursive=True) if "test/" not in fil]
)
locales = ['fi']
profile = 'dev'
ui_files = list(glob.glob("**/*.ui", recursive=True))
resources = list()
extra_dirs = ["resources", "logs"]
compiled_resources = []

PluginMaker(py_files=py_files, ui_files=ui_files, resources=resources, extra_dirs=extra_dirs,
            compiled_resources=compiled_resources, locales=locales, profile=profile)
