import os
import re

import logging
from lxml import etree
from pathlib import Path

LOGGER = logging.getLogger('atdf.reader')

class ATDFReader:
    _PARSER = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')

    def __init__(self, path):
        self.filename = path
        self.tree = self._openDeviceATDF(self.filename)

    def _openDeviceATDF(self, filename):
        LOGGER.debug("Opening XML file '%s'", os.path.basename(filename))
        xml_file = Path(filename).read_text("utf-8", errors="replace")
        xml_file = re.sub(' xmlns="[^"]+"', '', xml_file, count=1).encode("utf-8")
        xmltree = etree.fromstring(xml_file, parser=ATDFReader._PARSER)
        return xmltree

    def query(self, query):
        """
        queries the device tree and returns one of three things
        - list of element nodes,
        - list of strings or
        - None on failure.
        """
        try:
            return self.tree.xpath(query)
        except:
            LOGGER.error("Query failed for '%s'", str(query))
        return None

    def _getTopSection(self, name):
        """
        Convenience method that will get a top level atdf section, making sure it is singular
        """
        section = self.query(name)
        assert len(section) == 1
        return section[0]

    def getModules(self):
        return self._getTopSection('//modules')

    def getPinout(self):
        return self._getTopSection('//pinouts')

    def getVariants(self):
        return self._getTopSection('//variants')

    def getDevices(self):
        return self._getTopSection('//devices')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "ATDFReader({})".format(os.path.basename(self.filename))
