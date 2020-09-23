Development of GlobeBuilder plugin
===========================

The code for the plugin is in the [Qaava](../GlobeBuilder) folder. Make sure you have required tools, such as
Qt with Qt Editor and Qt Linquist installed by following this 
[tutorial](https://www.qgistutorials.com/en/docs/3/building_a_python_plugin.html#get-the-tools). 

For building the plugin use platform independent [build.py](../GlobeBuilder/build.py) script. 

### Adding or editing  source files
If you create or edit source files make sure that:
* they contain relative imports
    ```python
    '''file GlobeBuilder/database_tools/db_initializer.py'''
    
    from ..utils.exceptions import GlobeBuilderAuthConfigException # Good
    
    from GlobeBuilder.utils.exceptions import GlobeBuilderAuthConfigException # Bad
    ```
* they will be found by [build.py](../GlobeBuilder/build.py) script (`py_files` and `ui_files` values)
* you consider adding test files for the new functionality

### Deployment

Edit [build.py](../GlobeBuilder/build.py) to contain working values for *profile*, *lrelease* and *pyrcc*. 
If you are running on Windows, make sure the value *QGIS_INSTALLATION_DIR* points to right folder

Run the deployment with:
```shell script
python build.py deploy
```

After deploying and restarting QGIS you should see the plugin in the QGIS installed plugins
where you have to activate it.

#### Testing
Install Docker, docker-compose and python packages listed in [requirements.txt](requirements.txt) 
to run tests with:

```shell script
python build.py test
```

#### Translating

The translation files are in [i18n](../GlobeBuilder/resources/i18n) folder.
Translatable content in python files is code such as `tr(u"Hello World")`. 

To update language *.ts* files to contain newest lines to translate, run
```shell script
python build.py transup
```

You can then open the *.ts* files you wish to translate with Qt Linguist and make the changes.

Compile the translations to *.qm* files with:
```shell script
python build.py transcompile
```

### Creating a release
Follow these steps to create a release
* Add changelog information to [CHANGELOG.md](../CHANGELOG.md) using this
[format](https://raw.githubusercontent.com/opengisch/qgis-plugin-ci/master/CHANGELOG.md)
* Make a new commit. (`git add -A && git commit -m "Release v0.1.0"`)
* Create new tag for it (`git tag -a v0.1.0 -m "Version 0.1.0"`)
* Push tag to Github using `git push --follow-tags`
* Create Github release
* [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci) adds release zip automatically as an asset
