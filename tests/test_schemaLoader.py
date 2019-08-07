import unittest
from config.properties import Configuration
from collections import OrderedDict

from schema_definitions.schemaLoader import schemaLoader
from pandas import DataFrame

class TestSchemaLoader(unittest.TestCase):

    # Publicly accessed methods that needs to be checked:
    methodList = ['load_schema', 'get_submissionTypes', 'get_versions', 'get_schema']

    # Get supported schema version:
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

        # Testing if public methods exists:
        for method in self.methodList:
            self.assertHasAttr(loader, method)

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
    def testLoad_schema(self):
        loader = schemaLoader()
        loader.load_schema(self.mostRecentSchema)
        schemaData = loader.get_schema()

        # Is the returned data a list:
        self.assertIsInstance(schemaData, OrderedDict)

        # Checking if all values of the dictionary is a pandas dataframe:
        for data in schemaData.values():
            self.assertIsInstance(data, DataFrame)

    # Check if we have the supported submission types:
    def testGet_submisstionTypes(self):
        loader = schemaLoader()
        loader.load_schema(self.mostRecentSchema)

        # Fetch submission types:
        supportedSubmissionTypes = loader.get_submissionTypes()

        self.assertIsInstance(supportedSubmissionTypes, list)

if __name__ == '__main__':
    unittest.main()
