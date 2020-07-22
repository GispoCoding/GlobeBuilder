from qgis.core import Qgis


class MockMessageBar:

    def __init__(self):
        self.messages = {Qgis.Info: [], Qgis.Warning: [], Qgis.Critical: []}

    def get_messages(self, level):
        """Used to test which messages have been logged"""
        return self.messages[level]

    def pushMessage(self, text, level, duration):
        self.messages[level].append(text)


class MainWindow:

    def blockSignals(self, *args):
        pass
