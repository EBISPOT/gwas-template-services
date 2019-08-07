from flask import Flask, request, render_template, send_file, make_response
from flask_restplus import Resource, Api
from flask_cors import CORS, cross_origin
import sys

# Import logging related functions:
import logging

# Importing custom modules:
from template.spreadsheet_builder import SpreadsheetBuilder
from template.schemaJson_builder import jsonSchemaBuilder
from config.properties import Configuration
from schema_definitions.schemaLoader import schemaLoader
import endpoint_utils as eu

app = Flask(__name__)

# Initialize API with swagger parameters:
api = Api(app, default=u'Template services',
          default_label=u'GWAS Catalog template services',
          title = 'API documentation')

# Enabling cross-site scripting (might need to be removed later):
cors = CORS(app)

# Parameters for filtering template spreadsheets:
templateParams = api.parser()
templateParams.add_argument('curator', type=str, required=False, help='If the user is a curator or not.')
templateParams.add_argument('summaryStats', type=str, required=False, help='If the user wants to submit summary stats or not.')

# Pre-fill data is submitted as string that will be parsed as JSON:
templateParams.add_argument('prefillData', type=str, required=False, help='Contain data to pre-fill templates.')


# REST endpoint for providing the template spreadsheets:
@api.route('/v1/templates')
@api.expect(templateParams, validate=True)
class templateGenerator(Resource):
    def post(self):

        # Extract parameters:
        args = templateParams.parse_args()

        # parse filter based on the input parameters:
        filterParameters = {}
        if 'curator' in args: filterParameters['curator'] = True if args['curator'] == "true" else False
        if 'summaryStats' in args: filterParameters['summaryStats'] = True if args['summaryStats'] == "true" else False

        # Set submission types:
        submissionType = 'SUMMARY_STATS' if filterParameters['summaryStats'] else 'METADATA'

        # Parse pre-fill data if present:
        if args.prefillData is not None:
            prefillData = eu.preFillDataParser(args.prefillData)
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
            returnData["schema_versions"][version] = { 'href': '{}/v1/template-schema/{}'.format(request.url_root, version) }

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
            returnData["submission_types"][submissionType] = { 'href': '{}/v1/template-schema/{}/{}'.format(request.url_root, str(schema_version), submissionType) }

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

