import unittest
import sys
import os
import json
import pandas as pd

from config.properties import Configuration

# Adding app folder to Python path:
appFolder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(appFolder+'/../')

# TODO: fix testing for non-JSON serializable tests.
# TODO: fix dataframe equality test.

import endpoint_utils as eu

# Testing the following functions:
    # preFillDataParser
    # filter_parser
    # set_log_path
    # _set_log_level

class TestEndpointUtils(unittest.TestCase):

    # Frequently used variable is the most recent schema version:
    mostRecentSchemaVersion = Configuration.schemaVersion

    def test_preFillDataParser(self):

        # failInput1 = 'This string is not JSON serializable' # Not JSON serializable object
        failInput2 = '[12, "Test"]' # JSON serializable, but not properly formatted object
        failInput3 = '{"foo" : 12 }' # dictionary, but values are not lists
        failInput4 = '{"foo" : [12, 3, "bar"]}' # Dictionary with list, but list elements are not dictionaries
        goodInput = {
            "foo" : [
                {
                    "column1" : "c1_value1",
                    "column2" : "c2_value1",
                    "column3" : "c3_value1"
                },
                {
                    "column1": "c1_value2",
                    "column2": "c2_value2",
                    "column3": "c3_value2"
                }
            ]
        }

        # Testing if input is JSON serializable:
        # self.assertEqual(eu.preFillDataParser(failInput1), "[Error] Pre-fill data cannot be read as JSON.")

        # Testing if input is proper:
        self.assertEqual(eu.preFillDataParser(failInput2), "[Error] Pre-fill data should be an dictionary of lists.")

        # Testing if input is JSON serializable:
        self.assertEqual(eu.preFillDataParser(failInput3), "[Error] Pre-fill data should be an array of dictionaries")

        # Testing if input is proper:
        self.assertEqual(eu.preFillDataParser(failInput4), "[Error] Pre-fill data should be an array of dictionaries")

        # Testing proper output:
        output = eu.preFillDataParser(json.dumps(goodInput))

        # Test if the output is a dictionary:
        self.assertIsInstance(output, dict)

        # Test if the key of the returned dictionary is the key of the input dictionary:
        testKey = list(goodInput.keys())[0]
        self.assertIn(testKey, output)

        # Test if the value of the returned dictionary is a pandas dataframe:
        self.assertIsInstance(output[testKey], pd.DataFrame)

        # Test if the returned dataframe is exactly what we are expecting:
        testDataFrame = pd.DataFrame(goodInput[testKey])
        self.assertTrue(output[testKey].equals(testDataFrame))

    def test_schema_parser(self):

        # Generating mock input for the schema filter:
        filterParameters = {'testFilter' : True}
        filters = {
            'testFilter' : {
                'addColumn' : {
                    'testSheet' : ['column_1', 'column_2']
                },
                'removeColumn' :{
                    'testSheet' : ['column_3', 'column_4']
                }
            }
        }
        tabname = 'testSheet'
        testDataFrame = pd.DataFrame([
            {'NAME': 'column_1', 'DEFAULT': False},
            {'NAME': 'column_2', 'DEFAULT': True},
            {'NAME': 'column_3', 'DEFAULT': False},
            {'NAME': 'column_4', 'DEFAULT': True}])

        # Reading all schema files into a single ordered dictionary:
        testOutputDf = eu.schema_parser(filterParameters, filters,tabname, testDataFrame)

        # Now we have to check if the proper columns are still there:
        self.assertIn('NAME',testOutputDf.columns)
        self.assertIn('DEFAULT', testOutputDf.columns)

        # Now chack if the expected rows are there:
        self.assertIn('column_1', testOutputDf.NAME.tolist())
        self.assertIn('column_2', testOutputDf.NAME.tolist())
        self.assertNotIn('column_3', testOutputDf.NAME.tolist())
        self.assertNotIn('column_4', testOutputDf.NAME.tolist())




if __name__ == '__main__':
    unittest.main()

