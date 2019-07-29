import unittest
from config.properties import Configuration

# This test is written to make sure the configuration is properly set, all required features are included in the file
attributesToTest = ['schemaVersion', 'triggerRow', 'filters', 'logging_path', 'LOG_LEVEL', 'LOGGER_LOG', 'LOGGER_HANDLER', 'LOG_CONF']

class TestConfiguration(unittest.TestCase):

    # A function to test if the object has a specific attribute:
    def assertHasAttr(self, obj, attrname, message=None):
        if not hasattr(obj, attrname):
            if message is not None:
                self.fail(message)
            else:
                self.fail(HAS_ATTR_MESSAGE.format(obj, attrname))

    # Testing if all required parameters are set:
    def test_SetupValues(self):
        for attribute in attributesToTest:
            self.assertHasAttr(Configuration, attribute, message='[Error] The tested attribute ({}) was not found in the configuration file.'.format(attribute))

    # Testing filters:
    def test_Filters(self):
        filterObject = Configuration.filters

        # List of accepted actions:
        actions = ['addColumn', 'removeColumn']

        # Test if filter object is a dictionary:
        self.assertIsInstance(filterObject, dict)

        # Test if all values are dictionaries and their values are dictionaries too
        for filterValues in filterObject.values():

            # Test if filter object is a dictionary:
            self.assertIsInstance(filterValues, dict)

            # Test if any actions in the configuration is not supported and the values are good:
            for action, values in filterValues.items():
                self.assertIn(action, actions)
                self.assertIsInstance(values, dict)

                # Test if the values of this inner dictionary are lists:
                for columnNames in values.values(): self.assertIsInstance(columnNames, list)



if __name__ == '__main__':
    unittest.main()
