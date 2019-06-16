from flask import Flask
from flask_restplus import Resource, Api, reqparse
import pandas as pd
from flask import send_file
from flask_cors import CORS
import os
from werkzeug.datastructures import FileStorage
import sys

# Importing custom modules:
from template.spreadsheet_builder import SpreadsheetBuilder
from template.schemaJson_builder import jsonSchemaBuilder
from validation.validator import open_template, check_study_tags
from config.properties import Configuration
import endpoint_utils as eu

# import endpoint_utils as create_ftp_directories

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

parser = api.parser()
parser.add_argument('submissionId', type=int, required=True, help='Submission ID.')
parser.add_argument('fileName', type=str, required=True, help='Uploaded file name.')

file_upload = api.parser()
file_upload.add_argument('templateFile', type=FileStorage, location='files', required=True, help='Filled out template excel file.')
file_upload.add_argument('submissionId', type=int, required=True, help='Submission ID.')
file_upload.add_argument('fileName', type=str, required=True, help='Upload template file name.')

# curl -v -X POST -F submissionId=123123 -F file=@uploadedTemplates/template_testUpload.xlsx http://localhost:9000/upload
@api.route('/upload')
@api.expect(file_upload, validate=True)
class TemplateUploader(Resource):
    def post(self):

        # Extract parameters:
        args = file_upload.parse_args()
        xlsx_file = args['templateFile']
        submissionId = args['submissionId']
        xlsx_fileName = args['fileName']

        filePath = '{}/{}'.format(Configuration.uploadFolder, submissionId)

        # Does folder exists:
        if not os.path.exists(filePath):
            try:
                os.mkdir(filePath)
            except:
                return {'status' : 'failed', 'message' : 'Submission folder ({}) could not be created.'.format(submissionId)}

        # Is that a folder:
        if not os.path.isdir(filePath):
            return {'status': 'failed', 'message': 'Submission folder ({}) is not a directory.'.format(submissionId)}

        # Try saving the file:
        try:
            xlsx_file.save('{}/{}'.format(filePath, xlsx_fileName))

            if eu.updateFileUpload(filename= xlsx_fileName, submissionId=submissionId) == 0:
                return {'status': 'success', 'message' : 'File successfully uploaded.'}
            else:
               return {'status': 'failed', 'message': 'Upload successful, table update has failed.'}

        except:
            return {
                "status": "failed",
                "message": "Couldn't save uploaded file."
            }

# This function calls validation for a file uploaded and the file is given as a parameter:
@api.route('/validation')
class HandleUploadedFile(Resource):
    def get(self):

        # Extracting parameters:
        args = parser.parse_args()
        submissionId = args['submissionId']
        fileName = args['fileName']

        # File with path:
        xlsxFilePath = '{}/{}/{}'.format(Configuration.uploadFolder, submissionId, fileName)

        # If the file is not found:
        if not os.path.isfile(xlsxFilePath):
            eu.updateFileValidation(submissionId=submissionId, status= 0, message= "Uploaded file was not found")
            return {
                "status" : "failed",
                "message" : "Uploaded file was not found"
            }

        # Testing for opening:
        try:
            template_xlsx = pd.ExcelFile(xlsxFilePath)
        except:
            eu.updateFileValidation(submissionId=submissionId, status=0, message="Uploaded file could not be opened as an excel file.")
            return {
                "status" : "failed",
                "message" : "Uploaded file could not be opened as an excel file."
            }

        # Try to open all sheets:
        spread_sheets = {}
        missing_sheets = []

        for sheet in  ['studies', 'associations', 'samples']:
            try:
                spread_sheets[sheet] = open_template(template_xlsx, sheet)
            except:
                missing_sheets.append(sheet)

        if len(missing_sheets) > 0:
            eu.updateFileValidation(submissionId=submissionId, status=0,
                                    message="Some sheets were missing from the file.")
            return {
                    "status": "failed",
                    "message": "Some sheets were missing from the file",
                    "missingSheets": missing_sheets
                }

        # Check for study tags:
        missing_tags = check_study_tags(spread_sheets)

        if len(missing_tags) > 0:
            eu.updateFileValidation(submissionId=submissionId, status=0,
                                    message="Some study tags were not listed in the study sheet.")
            return {
                "status": "failed",
                "message": "Some study tags were not listed in the study sheet.",
                "missingTags": missing_tags
            }

        # File looks good. Update DB:
        eu.updateFileValidation(submissionId=submissionId, status=1,
                                message="First round of validation passed.")
        # Generate ftp directories:
        eu.generateFtpFolders(submissionId, spread_sheets['studies']['Study tag'].tolist())

        # Return success;
        return {
            "status": "success",
            "message": "First round of validation passed."
        }

# Non-REST endpoint for providing the templates:
@app.route('/templates/')
def returnTemplate():

    # default input files:
    inputFiles = {
        'studies': '/schema_definitions/study_schema.xlsx',
        'associations': '/schema_definitions/association_schema.xlsx',
        'samples': '/schema_definitions/sample_schema.xlsx',
        'notes' : '/schema_definitions/notes_schema.xlsx'
    }

    # This variable will be given from the input:
    filterParameters = {
        'curator': True,
        'haplotype': False,
        'effect': 'beta',
        'background': True
    }

    # Initialize spreadsheet builder object:
    spreadsheet_builder = SpreadsheetBuilder()

    # All schemas are loaded from the correct location:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # inputDataFrames = {title: pd.read_excel(dir_path + filename, index_col=False) for title, filename in inputFiles.items()}
    for tabname, filename in Configuration.schemas.items():
        # TODO: test file and other stuff

        # Open schema sheet as pandas dataframe:
        schemaDataFrame = pd.read_excel(dir_path + filename, index_col=False)

        # Set default columns:
        filteredSchemaDataFrame = eu.filter_parser(filterParameters, tabname, schemaDataFrame)

        # Add spreadsheet:
        if len(filteredSchemaDataFrame): spreadsheet_builder.generate_workbook(tabname, filteredSchemaDataFrame)

    # Once we are finished we save stuff:
    x = spreadsheet_builder.save_workbook()
    x.seek(0)
    print(x)
    return send_file(
        x,
        as_attachment=True,
        attachment_filename='template.xlsx',
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@api.route('/schemas/')
class SchemaList(Resource):
    def get(self):
        return {"available_schemas": ["study", "association", "sample", 'notes']}

@api.route('/schemas/<string:schema_name>')
class Schemas(Resource):

    # All schemas are loaded from the correct location:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # default input files:
    inputFiles = {
        'study': dir_path + '/schema_definitions/study_schema.xlsx',
        'association': dir_path + '/schema_definitions/association_schema.xlsx',
        'sample': dir_path + '/schema_definitions/sample_schema.xlsx',
        'note' : dir_path + '/schema_definitions/notes_schema.xlsx'
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

