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

    # Generally supported submission type:
    submissionType = 'METADATA'

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
        self.assertEqual(schema['schema_version'], self.mostRecentSchemaVersion)

        # Do we have a list of submission types?
        self.assertIn('submission_types', schema)

        # Is this a dictionary with submission types:
        self.assertIsInstance(schema['submission_types'], dict)

        # At least metadata must be there:
        self.assertIn('METADATA', schema['submission_types'])

    def test_endpoint_template_schema_submission_type(self):

        # Submit query:
        response = self.tester.get('/v1/template-schema/{}/{}'.format(self.mostRecentSchemaVersion, self.submissionType),
                                   content_type='html/json')
        self.assertEqual(response.status_code, 200)

        # Extract response content:
        responseSchema = response.get_json()

        # Must not contain errror:
        self.assertNotIn('error', responseSchema)

        # Must contain version:
        self.assertIn('version', responseSchema)

        # Version must be the requested version:
        self.assertEqual(self.mostRecentSchemaVersion, responseSchema['version'])

        # Must be man keys:
        self.assertGreater(len(responseSchema), 3)

    def test_endpoint_template_schema_wrong_submission_type(self):
        wrongSubmissionType = 'cicaful'

        # Submit query:
        response = self.tester.get('/v1/template-schema/{}/{}'.format(self.mostRecentSchemaVersion, wrongSubmissionType),
                                   content_type='html/json')
        self.assertEqual(response.status_code, 200)

        # Error must be in the key:
        self.assertIn('error', response.get_json())

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
