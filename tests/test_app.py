import unittest
import sys
import os
from config.properties import Configuration

# Adding app folder to Python path:
appFolder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(appFolder+'/../')

from app import app


class TestWebApplication(unittest.TestCase):

    # Create a tester instance of the application:
    tester = app.test_client()

    # Frequently used variable is the most recent schema version:
    mostRecentSchemaVersion = Configuration.schemaVersion

    def test_endpoint_template_schema(self):

        # Get response from endpoint:
        response = self.tester.get('/v1/template-schema', content_type='html/json')
        self.assertEqual(response.status_code, 200)

        # Test if the available schemas contain the current version:
        supportedSchemas = response.get_json()['schema_versions']
        self.assertIn(self.mostRecentSchemaVersion,supportedSchemas)

    def test_endpoint_template_schema_supported_version(self):

        # Submit quiery:
        response = self.tester.get('/v1/template-schema/{}'.format(self.mostRecentSchemaVersion), content_type='html/json')
        self.assertEqual(response.status_code, 200)

        schema = response.get_json()

        # Do we find the version:
        self.assertEqual(schema['version'], self.mostRecentSchemaVersion)

        # Do we have many elements:
        self.assertGreater(len(schema.keys()), 3)

    def test_endpoint_template_schema_wrong_version(self):
        # Get a wrong schema version:
        wrongSchema = 'cicaful'

        # Submit quiery:
        response = self.tester.get('/v1/template-schema/{}'.format(wrongSchema), content_type='html/json')
        self.assertEqual(response.status_code, 200)

        schema = response.get_json()

        # Do we have errors:
        self.assertIn('error', schema)

        # Is the error message as expected:
        self.assertEqual('Unknown schema versions', schema['error'])

        # Do we see the supported schema:
        self.assertIn(self.mostRecentSchemaVersion, schema['supported_versions'])

    def test_templates(self):
        # Submit quiery:
        response = self.tester.post('/v1/templates', content_type='html/json')
        self.assertEqual(response.status_code, 200)

        # Test if the returned value is a blob:


if __name__ == '__main__':
    unittest.main()
