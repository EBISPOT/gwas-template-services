from flask import Flask
from flask_restplus import Resource, Api, reqparse
import pandas as pd
from flask import send_file
from flask_cors import CORS
import os

# Importing custom modules:
from ingest.template.spreadsheet_builder import SpreadsheetBuilder
from ingest.template.schemaJson_builder import jsonSchemaBuilder

import endpoint_utils as epu

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

parser = api.parser()
parser.add_argument('submissionId', type=int, required=True, help='Submission ID.')
parser.add_argument('fileName', type=str, required=True, help='Uploaded file name.')

@api.route('/validation')
class HandleUploadedFile(Resource):
    def get(self):
        args = parser.parse_args()
        return {
            'submissionId' : args['submissionId'],
            'fileName' : args['fileName']
        }

        # # Testing for file:
        # if not file_exist:
        #     return {}
        #
        # # Testing for opening:
        # try:
        #     open send_file()
        # except:
        #     return {"cicaful"}
        #
        # # Testing for available sheets:
        #
        #
        # # Start validation process:
        #
        #
        # return response

@app.route('/templates/')
def returnTemplate():

    # default input files:
    inputFiles = {
        'studies': '/schema_definitions/study_schema.xlsx',
        'associations': '/schema_definitions/association_schema.xlsx',
        'samples': '/schema_definitions/sample_schema.xlsx',
    }

    # All schemas are loaded from the correct location:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    inputDataFrames = {title: pd.read_excel(dir_path + filename, index_col=False) for title, filename in inputFiles.items()}

    # Submitting all dataframes to the spreadsheet builders:
    spreadsheet_builder = SpreadsheetBuilder()
    spreadsheet_builder.generate_workbook(inputDataFrames)
    x = spreadsheet_builder.save_workbook()

    # The spreadsheet is returned as bytestream:
    return send_file(
        x.seek(0),
        as_attachment=True,
        attachment_filename='template.xlsx',
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@api.route('/schemas/')
class SchemaList(Resource):
    def get(self):
        return {"available_schemas": ["study", "association", "sample"]}

@api.route('/schemas/<string:schema_name>')
class Schemas(Resource):

    # All schemas are loaded from the correct location:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # default input files:
    inputFiles = {
        'study': dir_path + '/schema_definitions/study_schema.xlsx',
        'association': dir_path + '/schema_definitions/association_schema.xlsx',
        'sample': dir_path + '/schema_definitions/sample_schema.xlsx',
    }

    def get(self, schema_name):
        # Unknown schema:
        if not schema_name in self.inputFiles.keys():
            return({'error' : 'Unknown schema'})

        # Known schema:
        schema = jsonSchemaBuilder(schema_name)
        schema.addTable(self.inputFiles[schema_name])
        return schema.get_schema()



@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        return {"hello": "world"}


if __name__ == '__main__':
    app.run(debug=True)

