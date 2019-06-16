from collections import OrderedDict
from argparse import ArgumentParser
import pandas as pd
import json
import pkg_resources

class jsonSchemaBuilder:
    def __init__(self, schemaType):
        
        # Adding fixed values to schema document:
        self.schema = OrderedDict({
            "$schema": 'http://json-schema.org/draft-07/schema#',
            "description": 'Spreadsheet describing {}.'.format(schemaType),
            "additionalProperties": False,
            "required" : [],
            "title": '{} spreadsheet'.format(schemaType),
            "name": '{}_spreadsheet'.format(schemaType),
            "type": "object",
            'properties' : OrderedDict()
        })
        
        self.schemaType = schemaType
        
    def addTable(self, schemaSpreadsheet):

        # Reading the template into a df:
        inputDataFrame = pd.read_excel(schemaSpreadsheet, index_col=False)
        
        # Adding df to schema:
        inputDataFrame.apply(self._addPropertyToSchema, axis = 1)

        # Adding mandatory fields:
        inputDataFrame.loc[ inputDataFrame.MANDATORY, 'NAME'].apply(lambda x: self.schema['required'].append(x))

         
    def _addPropertyToSchema(self, row):
        
        # Initialize property description:
        propObj = {
            "description": row['DESCRIPTION'],
            "type": row['TYPE'],
            "user_friendly": row['HEADER'],
        }
        
        # Adding pattern:
        if not pd.isna(row['PATTERN']): propObj['pattern'] = row['PATTERN']

        # Adding example:
        if not pd.isna(row['EXAMPLE']): propObj['example'] = row['EXAMPLE']

        # Adding boundaries:
        if not pd.isna(row['LOWER']) and not pd.isna(row['UPPER']): 
            propObj['minimum'] = row['LOWER']
            propObj['maximum'] = row['UPPER']

        # Adding Accepted values:
        if not pd.isna(row['ACCEPTED']): propObj['ACCEPTED'] = row['ACCEPTED'].split('|')

        # Adding property to schema:
        self.schema['properties'][row['NAME']] = propObj
    
    def saveJson(self, fileName = None):
        if not fileName: 
            fileName = '{}_schema.json'.format(self.schemaType)
            
        # Save file:
        with open(fileName, 'w') as outfile:
            json.dump(self.schema, outfile, indent=4)
            
    def get_schema(self):
        return(self.schema)
            
            
if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('-o', '--output', dest='output', help='Filename for the resulting json file.', required=False, default='output_schema.json')
    parser.add_argument('-i', '--input', dest='input', help='Excel spreadsheet describing the schema.', required=True)
    parser.add_argument('-t', '--type', dest='type', help='Type of schema eg. association.', required = True)

    args = parser.parse_args()
    outputFileName = args.output
    inputFileName = args.input
    schemaType = args.type

    # Open input file into a dataframe:
    inputDataFrame = pd.read_excel(inputFileName, index_col=False)

    # Generate json schema:
    schemaBuilder = jsonSchemaBuilder(schemaType)
    schemaBuilder.addTable() #inputDataFrame)
    schemaBuilder.saveJson(outputFileName)
    schema = schemaBuilder.get_schema()

