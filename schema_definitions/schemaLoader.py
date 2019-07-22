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

        self.allVersions = self.__schema_versions()
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

    # Interface to get all available versions:
    def get_versions(self):
        return self.allVersions

    # Open schema for a given version:
    def read_schema(self, version):

        # Raising error if unsupported schema is requested:
        if not version in self.allVersions:
            raise unknownShemaVersionError("[Error] The requested schema version ({}) is not supported.".format(version))

        # A dictionary is populated with all the spreadsheets read as pandas dataframes:
        schema_dfs = OrderedDict()

        # Looping through all sheets, generating file name and load the file:
        filename = self.schemaFilePattern % (self.schemaFolder, version)
        try:
            xls = pd.ExcelFile(filename, index_col=False)
        except FileNotFoundError:
            logging.error('Schema file ({}) was not found.'.format(filename))
            return(schema_dfs)

        for sheet in xls.sheet_names:
            schema_dataframe = pd.read_excel(xls, sheet)
            schema_dataframe = schema_dataframe.where((schema_dataframe.notnull()), None)
            schema_dfs[sheet] = schema_dataframe

        # return ordered dict:
        return(schema_dfs)


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
