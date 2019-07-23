from flask import Flask, request, render_template, send_file
from flask_restplus import Resource, Api
from flask_cors import CORS
import sys

# Import logging related functions:
# from logging.config import dictConfig
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
templateParams.add_argument('haplotype', type=str, required=False, help='If the associations are haplotypes or not.')
templateParams.add_argument('snpxsnp', type=str, required=False, help='If the associations are SNP x SNP interactions or not.')
templateParams.add_argument('effect', type=str, required=False, help='How the effect is expressed.')
templateParams.add_argument('backgroundTrait', type=str, required=False, help='If backgroundtrait is present or not.')
templateParams.add_argument('accessionIDs', type=str, required=False, help='To generate summary stat sheet post all accession IDs.', action='append')


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
        if 'haplotype' in args: filterParameters['haplotype'] = True if args['haplotype'] == "true" else False
        if 'snpxsnp' in args: filterParameters['snpxsnp'] = True if args['snpxsnp'] == "true" else False
        if 'backgroundTrait' in args: filterParameters['backgroundTrait'] = True if args['backgroundTrait'] == "true" else False
        if 'effect' in args: filterParameters['effect'] = args['effect']

        # Parsing accession IDs is a bit complex:
        filterParameters['accessionIDs'] = []
        if 'accessionIDs' in args and args['accessionIDs']:
            for accessionID in args['accessionIDs']:
                filterParameters['accessionIDs'] += accessionID.split(',')

        # Reading all schema files into a single ordered dictionary:
        schemaVersion = Configuration.schemaVersion
        sv = schemaLoader()
        schemaDataFrames = sv.read_schema(schemaVersion)

        print(filterParameters)

        # Initialize spreadsheet builder object:
        spreadsheet_builder = SpreadsheetBuilder(version=schemaVersion)

        for schema in schemaDataFrames.keys():

            # Set default columns:
            filteredSchemaDataFrame = eu.filter_parser(filterParameters, schema, schemaDataFrames[schema])

            # Add spreadsheet if at least one column remained:
            if len(filteredSchemaDataFrame):
                spreadsheet_builder.generate_workbook(schema, filteredSchemaDataFrame)

        # Adding data:
        if filterParameters['accessionIDs']:
            print(filterParameters['accessionIDs'])
            spreadsheet_builder.add_values(tabname='study', colname='study_accession', data=filterParameters['accessionIDs'])

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


@api.route('/v1/template-schema')
class SchemaList(Resource):
    def get(self):

        # Get all versions:
        sv = schemaLoader()
        supported_versions = sv.get_versions()

        # Initialize return data:
        returnData = {"schema_versions":{}}

        for version in supported_versions:
            returnData["schema_versions"][version] = { 'href': '{}/v1/template-schema/{}'.format(request.url_root, version) }

        return returnData


@api.route('/v1/template-schema/<string:schema_version>')
class schemaJSON(Resource):

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
        schemaDataFrames = sv.read_schema(schema_version)
        # return { 'sheets' : list(schemaDataFrames.keys())}

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

# The following endpoint serves testing purposes only to demonstrate the flexibility of the template generation.
@app.route('/template_download_test')
def hello():
    return render_template('template_test.html')


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

