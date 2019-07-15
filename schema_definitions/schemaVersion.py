import pandas as pd
from collections import OrderedDict
import os
import glob
import re
from argparse import ArgumentParser


class schemaVersioning(object):

    sheets = ['study', 'association', 'sample', 'notes']
    schemaFolder = os.path.dirname(os.path.realpath(__file__))
    schemaFilePattern = '%s/%s_schema_v%s.xlsx'

    def __init__ (self):
        return None

    def get_versions(self):
        availableVersions = []

        # Lisiting all Excel files:
        for schemaFile in glob.glob(self.schemaFolder + "/*.xlsx"):
            m = re.search(r"_schema_v(.+?)\.xlsx", schemaFile)
            if m and m.group(1) not in availableVersions:
                availableVersions.append(m.group(1))

        # Return list with version:
        return(availableVersions)

    def read_schema(self, version):
        schema_dfs = OrderedDict()

        # Looping through all sheets, generating file name and load the file:
        for sheet in self.sheets:
            filename = self.schemaFilePattern % (self.schemaFolder, sheet, version)

            try:
                schema_dataframe = pd.read_excel(filename, index_col=False)
                schema_dataframe = schema_dataframe.where((schema_dataframe.notnull()), None)
                schema_dfs[sheet] = schema_dataframe
            except:
                print('[Warning] The schema file ({}) was not found.'.format(filename))
                continue

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
    sv = schemaVersioning()

    # Get available versions:
    availableVersions = sv.get_versions()
    print('[Info] Availabe versions: {}'.format(','.join(availableVersions)))

    # Load all schemas for the specified version:
    schemas = sv.read_schema(schemaVersion)
    print('[Info] The following spreadsheets for v.{} were successfully loaded: {}'.format(schemaVersion, ', '.join(schemas.keys())))



if __name__ == '__main__':
    main()
