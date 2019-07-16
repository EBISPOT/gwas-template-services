import unittest
import sys
import os

appFolder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(appFolder+'/../')
print(sys.path)

from app import app


from config.properties import Configuration

class BasicTestCase(unittest.TestCase):
    def test_endpoint_template_schema(self):
        tester = app.test_client()

        # Get response from endpoint:
        response = tester.get('/v1/template-schema', content_type='html/json')
        self.assertEqual(response.status_code, 200)

        # Test if the available schemas contain the current version:
        supportedSchemas = response.get_json()['schema_versions']
        self.assertIn(Configuration.schemaVersion,supportedSchemas)


if __name__ == '__main__':
    unittest.main()
