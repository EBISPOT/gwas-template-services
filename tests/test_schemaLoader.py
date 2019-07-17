import unittest
from config.properties import Configuration
from collections import OrderedDict

from schema_definitions.schemaLoader import schemaLoader
from pandas import DataFrame

class TestSchemaLoader(unittest.TestCase):

    mostRecentSchema = Configuration.schemaVersion

    # A function to test if the object has a specific attribute:
    def assertHasAttr(self, obj, attrname, message=None):
        if not hasattr(obj, attrname):
            if message is not None:
                self.fail(message)
            else:
                self.fail(HAS_ATTR_MESSAGE.format(obj, attrname))

    # Testing if the loader can be properly initialized:
    def testInit(self):
        # <class 'schema_definitions.schemaLoader.schemaLoader'>
        loader = schemaLoader()

        # Was the initialization successful:
        self.assertIsInstance(loader, schemaLoader)

        # Testing if method exists:
        self.assertHasAttr(loader, 'get_versions')

        # Testing if method exists:
        self.assertHasAttr(loader, 'read_schema')

        # Store loader object:
        self.loader = loader

    # Testing if the loader could load available schemas:
    def testGet_versions(self):
        loader = schemaLoader()
        versions = loader.get_versions()

        # Is the returned data a list:
        self.assertIsInstance(versions, list)

        # Is the returned data contains the most recent schema:
        self.assertIn(self.mostRecentSchema,versions)

    # Testing if the returned schema data looks good:
    def testRead_schema(self):
        loader = schemaLoader()
        schemaData = loader.read_schema(self.mostRecentSchema)

        # Is the returned data a list:
        self.assertIsInstance(schemaData, OrderedDict)

        # Checking if all values of the dictionary is a pandas dataframe:
        for data in schemaData.values():
            self.assertIsInstance(data, DataFrame)

if __name__ == '__main__':
    unittest.main()
