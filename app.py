from flask import Flask, request, render_template, send_file
from flask_restplus import Resource, Api, reqparse
from flask_cors import CORS
import pandas as pd
import os

# Importing custom modules:
from template.spreadsheet_builder import SpreadsheetBuilder
from template.schemaJson_builder import jsonSchemaBuilder
from validation.validator import open_template, check_study_tags
from config.properties import Configuration
import endpoint_utils as eu

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

parser = api.parser()
parser.add_argument('submissionId', type=int, required=True, help='Submission ID.')
parser.add_argument('fileName', type=str, required=True, help='Uploaded file name.')


templateParams = api.parser()
templateParams.add_argument('curator', type=str, required=False, help='If the user is a curator or not.')
templateParams.add_argument('haplotype', type=str, required=False, help='If the associations are haplotypes or not.')
templateParams.add_argument('snpxsnp', type=str, required=False, help='If the associations are SNP x SNP interactions or not.')
templateParams.add_argument('effect', type=str, required=False, help='How the effect is expressed.')
templateParams.add_argument('backgroundTrait', type=str, required=False, help='If backgroundtrait is present or not.')


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


# REST endpoint for providing the template spreadsheets:
@api.route('/templates')
@api.expect(templateParams, validate=True)
class templateGenerator(Resource):
    def post(self):

        # Extract parameters:
        args = templateParams.parse_args()

        # parse filter based on the input parameters:
        filterParameters = {}
        if 'curator' in args: filterParameters['curator'] = True if args['curator'] == "true" else False
        if 'haplotype' in args: filterParameters['haplotype'] = True if args['haplotype'] == "true" else False
        if 'snpxsnp' in args: filterParameters['snpxsnp'] = True if args['snpxsnp'] == "true" else False
        if 'backgroundTrait' in args: filterParameters['backgroundTrait'] = True if args['backgroundTrait'] == "true" else False
        if 'effect' in args: filterParameters['effect'] = args['effect']

        # Initialize spreadsheet builder object:
        spreadsheet_builder = SpreadsheetBuilder()

        print(filterParameters)

        # All schemas are loaded from the correct location:
        dir_path = os.path.dirname(os.path.realpath(__file__))

        for tabname, filename in Configuration.schemas.items():
            # TODO: test file and other stuff

            # Open schema sheet as pandas dataframe:
            schemaDataFrame = pd.read_excel(dir_path + filename, index_col=False)

            # Set default columns:
            filteredSchemaDataFrame = eu.filter_parser(filterParameters, tabname, schemaDataFrame)

            # Add spreadsheet if at least one column remained:
            if len(filteredSchemaDataFrame): spreadsheet_builder.generate_workbook(tabname, filteredSchemaDataFrame)

        # Once all spreadsheets added to the template, saving document:
        x = spreadsheet_builder.save_workbook()
        x.seek(0)

        # Returning data:
        return send_file(
            x,
            as_attachment=True,
            attachment_filename='template.xlsx',
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


@api.route('/schemas/')
class SchemaList(Resource):
    def get(self):
        returnData = {"_links":{}}
        for schema in Configuration.schemas.keys():
            returnData["_links"][schema] = { 'href': '{}schemas/{}'.format(request.url_root, schema) }

        return returnData


@api.route('/schemas/<string:schema_name>')
class Schemas(Resource):

    # All schemas are loaded from the correct location:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def get(self, schema_name):

        # Unknown schema:
        if not schema_name in Configuration.schemas:
            return({'error' : 'Unknown schema'})

        # Known schema:
        schema = jsonSchemaBuilder(schema_name)
        schema.addTable(self.dir_path + Configuration.schemas[schema_name])
        return schema.get_schema()

# The following endpoint serves testing purposes only to demonstrate the flexibility of the template generation.
@app.route('/template_download_test')
def hello():
    return render_template('template_test.html')


if __name__ == '__main__':
    app.run(debug=True)

