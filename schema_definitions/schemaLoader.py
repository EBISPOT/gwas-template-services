import pandas as pd
from collections import OrderedDict
import os
import glob
import re
from argparse import ArgumentParser
import logging


class unknownShemaVersionError(Exception):
    """Unsupported schema version was requested."""
    pass


class schemaLoader(object):

    schemaFolder = os.path.dirname(os.path.realpath(__file__))
    schemaFilePattern = '%s/template_schema_v%s.xlsx'

    def __init__ (self):

        # Get available schemas:
        self.allVersions = self.__schema_versions()

        # Define empty schema:
        self.schema = OrderedDict()

        # Define empty submission type:
        self.submissionTypes = ['general']

        return None

    # Get a list of available versions:
    def __schema_versions(self):
        availableVersions = []

        # Lisiting all Excel files:
        for schemaFile in glob.glob(self.schemaFolder + "/*.xlsx"):
            m = re.search(r"template_schema_v(.+?)\.xlsx", schemaFile)
            if m and m.group(1) not in availableVersions:
                availableVersions.append(m.group(1))

        # Return list with version:
        return(availableVersions)

    # Interface to get all the supported submission types:
    def __parse_submission_types(self):
        mandatoryPattern = 'MANDATORY-(.*)'
        submissionTypes = []

        # Looping through all sheets, and parse the header:
        for df in self.schema.values():
            for columnName in df.columns:
                if re.search(mandatoryPattern, columnName):
                    submissionTypes.append(re.findall(mandatoryPattern, columnName)[0])

        self.submissionTypes = list(set(submissionTypes))

    # Open schema for a given version:
    def load_schema(self, version):

        # Raising error if unsupported schema is requested:
        if not version in self.allVersions:
            raise unknownShemaVersionError("[Error] The requested schema version ({}) is not supported.".format(version))

        # A dictionary is populated with all the spreadsheets read as pandas dataframes:
        schema_dfs = OrderedDict()

        # Looping through all sheets, generating file name and load the file:
        filename = self.schemaFilePattern % (self.schemaFolder, version)
        try:
            xls = pd.ExcelFile(filename)
        except FileNotFoundError:
            logging.error('Schema file ({}) was not found.'.format(filename))
            return(schema_dfs)

        for sheet in xls.sheet_names:
            schema_dataframe = pd.read_excel(xls, sheet, index_col=False)
            schema_dataframe = schema_dataframe.where((schema_dataframe.notnull()), None)
            schema_dfs[sheet] = schema_dataframe

        # ordered dictionary is added to the object:
        self.schema = schema_dfs

        # Get supported submission type for this shema version:
        self.__parse_submission_types()

    # Interface to retrieve submission types from the object:
    def get_submissionTypes(self):
        return(self.submissionTypes)

    # Interface to get all available versions:
    def get_versions(self):
        return self.allVersions

    # Interface to retrieve schema for a given submission type:
    def get_schema(self, submissionType = None):

        # If no submission type is defined, we return everything:
        if not submissionType:
            return self.schema

        # Else we filter out the required submission type and return only that:
        for schameName in self.schema.keys():
            try:
                specificMandatory = self.schema[schameName]['MANDATORY-{}'.format(submissionType)]
                self.schema[schameName] = self.schema[schameName].filter(regex='^(?!MANDATORY)')
                self.schema[schameName]['MANDATORY'] = specificMandatory

            except KeyError:
                raise KeyError

        # Return the updated data:
        return self.schema

def main():

    parser = ArgumentParser()
    parser.add_argument("-v", "--schemaVersion", dest="schemaVersion", help="Schema version eg. 1.0", required=False)

    args = parser.parse_args()
    if args.schemaVersion:
        schemaVersion = args.schemaVersion
    else:
        schemaVersion = '1.0'

    # Initialize schema versioning object:
    sv = schemaLoader()

    # Get available versions:
    availableVersions = sv.get_versions()
    print('[Info] Availabe versions: {}'.format(','.join(availableVersions)))

    # Load all schemas for the specified version:
    schemas = sv.read_schema(schemaVersion)
    print('[Info] The following spreadsheets for v.{} were successfully loaded: {}'.format(schemaVersion, ', '.join(schemas.keys())))


if __name__ == '__main__':
    main()
