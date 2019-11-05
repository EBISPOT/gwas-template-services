from flask import Flask, request, send_file
from flask_restplus import Resource, Api, fields
from flask_cors import CORS
from flask import Blueprint, url_for
import sys,os
from urllib.parse import unquote

# Import logging related functions:
import logging

# Importing custom modules:
from template.spreadsheet_builder import SpreadsheetBuilder
from template.schemaJson_builder import jsonSchemaBuilder
from config.properties import Configuration
from schema_definitions.schemaLoader import schemaLoader
import endpoint_utils as eu

app = Flask(__name__)

if 'BASE_PATH' not in os.environ:
    os.environ['BASE_PATH'] = ""

bp = Blueprint('template', __name__, url_prefix=os.environ['BASE_PATH'])

# Initialize API with swagger parameters:
api = Api(bp, default=u'Template services',
          default_label=u'GWAS Catalog template services',
          description='This application was written to facilitate template releated services for the new deposition interface of the GWAS Catalog.',
          doc='/documentation/',
          title = 'API documentation')

app.register_blueprint(bp)

# Enabling cross-site scripting (might need to be removed later):
cors = CORS(app)

# Parameters for filtering template spreadsheets:
templateParams = api.model( "Template generator parameters",{
    'curator' : fields.Boolean(description="Is the uploader a curator? (default: false)", required=False, default=False),
    'summaryStats' : fields.Boolean(description="Is it as summary statistics submission? (default: false)", required=False, default=False),
    'prefillData' : fields.String(description='Data to be added to the template.', required = False )
})


# REST endpoint for providing the template spreadsheets:
@api.route('/v1/templates')
class templateGenerator(Resource):

    @api.doc('Generate template')
    @api.expect(templateParams)
    def post(self):

        # Extracting parameters:
        filterParameters = request.json if request.json else {}

        # parse filter based on the input parameters:
        if 'curator' not in filterParameters: filterParameters['curator'] = False
        if 'summaryStats' not in filterParameters: filterParameters['summaryStats'] = False

        # Based on the parameters, we decide on the submission type:
        submissionType = 'SUMMARY_STATS' if filterParameters['summaryStats'] else 'METADATA'

        # Parse pre-fill data if present:
        if 'prefillData' in filterParameters:
            prefillData = eu.preFillDataParser(filterParameters['prefillData'])
        else:
            prefillData = {}

        # If the returned data is not a dictionary, the function needs to fail:
        if not isinstance(prefillData, dict):
            print({"Error" : "parsing pre-fill data failed."})

        # Reading all schema files into a single ordered dictionary:
        schemaVersion = Configuration.schemaVersion
        sv = schemaLoader()
        sv.load_schema(schemaVersion)
        schemaDataFrames = sv.get_schema(submissionType)

        # Print report:
        print('[Info] Filter paramters: {}'.format(filterParameters.__str__()))

        # Initialize spreadsheet builder object:
        spreadsheet_builder = SpreadsheetBuilder(version=schemaVersion, submissionType=submissionType)

        for schema in schemaDataFrames.keys():

            # Set default columns:
            filteredSchemaDataFrame = eu.schema_parser(filterParameters, Configuration.filters, schema, schemaDataFrames[schema])

            # Add spreadsheet if at least one column remained:
            if len(filteredSchemaDataFrame):
                spreadsheet_builder.generate_workbook(schema, filteredSchemaDataFrame)

            # Adding pre-fill data:
            if schema in prefillData:
                spreadsheet_builder.add_values(tabname=schema, preFillDataFrame=prefillData[schema])

        # Once all spreadsheets added to the template, and pre filled data is added, we are saving document:
        x = spreadsheet_builder.save_workbook()
        x.seek(0)

        # Returning data:
        return send_file(
            x,
            as_attachment=True,
            attachment_filename='template.xlsx',
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


@api.route('/v1/template-schema')
class SchemaList(Resource):
    def get(self):

        # Get all versions:
        sv = schemaLoader()
        supported_versions = sv.get_versions()

        # Initialize return data:
        returnData = {"current_schema" : Configuration.schemaVersion, "schema_versions":{}}

        for version in supported_versions:
            returnData["schema_versions"][version] = {'href': unquote('{}/{}'.format(request.url, version))}

        return returnData


@api.route('/v1/template-schema/<string:schema_version>')
class submissionTypes(Resource):
    def get(self, schema_version):

        # Get all versions:
        sv = schemaLoader()
        supported_versions = sv.get_versions()

        # Is it a supported version:
        if not schema_version in supported_versions:
            return {
                'error' : 'Unknown schema versions',
                'supported_versions': supported_versions
            }

        # Extract json schema:
        sv.load_schema(schema_version)

        # return available submission types:
        returnData = { 'schema_version' : schema_version , 'submission_types' : {}}
        for submissionType in sv.get_submissionTypes():
            returnData["submission_types"][submissionType] = {'href': unquote('{}/{}'.format(request.url, submissionType))}

        return(returnData)


@api.route('/v1/template-schema/<string:schema_version>/<string:submissionType>')
class schemaJSON(Resource):

    def get(self, schema_version, submissionType):

        # Get all versions:
        sv = schemaLoader()
        supported_versions = sv.get_versions()

        # Is it a supported version:
        if not schema_version in supported_versions:
            return {
                'error' : 'Unknown schema versions',
                'supported_versions': supported_versions
            }

        # Extract json schema:
        sv.load_schema(schema_version)

        if submissionType not in sv.get_submissionTypes():
            return {
                'error' : 'the provided submission type ({}) is not supported.'.format(submissionType),
                'schema_version' : schema_version ,
                'available_submission_types' : sv.get_submissionTypes()}

        schemaDataFrames = sv.get_schema(submissionType)

        JSON_builder = jsonSchemaBuilder(schema_version, triggerRow = Configuration.triggerRow)
        for sheet, df in schemaDataFrames.items():
            JSON_builder.addTable(sheetName = sheet, inputDataFrame=df)

        return JSON_builder.get_schema()


# Setting log level:
def _set_log_level(LOG_CONF, LOG_LEVEL):
    for handler in LOG_CONF['handlers']:
        LOG_CONF['handlers'][handler]['level'] = LOG_LEVEL
    for loggr in LOG_CONF['loggers']:
        LOG_CONF['loggers'][loggr]['level'] = LOG_LEVEL
    return LOG_CONF


# Function for logging:
def _set_log_path(properties):
    return register_logger.set_log_path(properties)


if __name__ == '__main__':
    app.run(debug=False)

    # Setting log level if gunicorn is started with this parameter:
    if '--log-level' in sys.argv:
        gunicorn_logger = logging.getLogger('gunicorn.error')
        print("[Info] Setting log level to {}".format(gunicorn_logger.level))
        Configuration.LOG_LEVEL = gunicorn_logger.level

    print("[Info] Log level to {}".format(Configuration.LOG_LEVEL))
    Configuration.LOG_CONF = eu._set_log_level(LOG_CONF=Configuration.LOG_CONF, LOG_LEVEL=Configuration.LOG_LEVEL)
    logging.config.dictConfig(Configuration.LOG_CONF)
