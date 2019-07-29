from argparse import ArgumentParser
import pandas as pd
import json


class jsonSchemaBuilder:
    def __init__(self, schemaVersion, triggerRow):

        # Saving parameters:
        self.version = schemaVersion
        self.triggerRow = triggerRow

        # Initialize JSON schema:
        self.JSON_schema = {'version' : schemaVersion}

    def addTable(self, sheetName, inputDataFrame):

        # Initialize sheet in the JSON object:
        self.JSON_schema[sheetName] = {
            'triggerRow' : self.triggerRow,
            'studyTagColumnName' : 'study_tag'
        }

        # Adding df to schema:
        self.JSON_schema[sheetName]["columns"] = list(inputDataFrame.apply(self._addPropertyToSchema, axis = 1))


    def _addPropertyToSchema(self, row):
        
        # Initialize property description:
        columnData  = {
            "columnName" : row['NAME'],
            "description": row['DESCRIPTION'],
            "baseType": row['TYPE'],
            "columnHeading": row['HEADER'],
            "required" : row['MANDATORY'],
            "default" : row['DEFAULT'],
        }
        
        # Adding pattern:
        if not pd.isna(row['PATTERN']): columnData['pattern'] = row['PATTERN']

        # Adding example:
        if not pd.isna(row['EXAMPLE']): columnData['example'] = row['EXAMPLE']

        # Adding boundaries:
        if not pd.isna(row['LOWER']) and not pd.isna(row['UPPER']):
            columnData['lowerBound'] = row['LOWER']
            columnData['upperBound'] = row['UPPER']

        # Adding Accepted values:
        if not pd.isna(row['ACCEPTED']): columnData['acceptedValues'] = row['ACCEPTED'].split('|')

        return columnData

    def saveJson(self, fileName = None):
        if not fileName:
            fileName = '{}_schema.json'.format(self.schemaType)

        # Save file:
        with open(fileName, 'w') as outfile:
            json.dump(self.schema, outfile, indent=4)

    def get_schema(self):
        return(self.JSON_schema)


def main():

    parser = ArgumentParser()

    parser.add_argument('-f', '--file', dest='file', help='Excel spreadsheet file describing the schema.', required=True)
    parser.add_argument('-n', '--name', dest='name', help='Name of schema eg. association.', required = True )
    parser.add_argument('-v', '--version', dest='schemaVersion', help='Version of the schema.', required=True)
    parser.add_argument('-t', '--triggerRow', dest='triggerRow', help='Row label signaling where the data is going to be read.', required=False, default="Add your data below this line")

    args = parser.parse_args()
    inputFileName = args.file
    schemaType = args.name
    triggerRow = args.triggerRow
    schemaVersion = args.schemaVersion

    # Open input file into a dataframe:
    inputDataFrame = pd.read_excel(inputFileName, index_col=False)

    # Generate json schema:
    schemaBuilder = jsonSchemaBuilder(schemaVersion = schemaVersion, triggerRow=triggerRow)
    schemaBuilder.addTable(sheetName=schemaType, inputDataFrame=inputDataFrame)

    print(schemaBuilder.get_schema())


if __name__ == '__main__':
    main()

