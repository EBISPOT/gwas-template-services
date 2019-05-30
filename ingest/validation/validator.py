import pandas as pd
import sys
sys.path.insert(0,'/homes/dsuveges/Project/gwas-ingest/ingest/template/')
from spreadsheet_builder import SpreadsheetBuilder 
from schemaJson_builder import jsonSchemaBuilder
from collections import OrderedDict
import numpy as np
import datetime  
import re

class validator(object):
    def __init__(self, uploadedData, schema_obj):
        self.uploadedData = uploadedData.copy()
        self.schema_obj = schema_obj
        
        # Parsing schema object:
        self._parse_schema()
        
        # Initialize validation report:
        self.add_report()
        
        # Collecting failed values:
        self.failed = {}
        
    def clean_data(self):
        return(1)
        # Dropping unexpected columns:
        self.uploadedData.drop(unexpected_columns, axis=1, inplace=True)

        # Adding expected columns:
        for col in missing_columns:
            self.uploadedData[col] = np.nan

        # Exclude empty rows:
        self.uploadedData.drop(empty_rows, inplace=True)

        # Removing rows where missing mandatory field was found:
        self.uploadedData.drop(missing_indices, inplace=True)

        # Removing lines with bad types:
        self.uploadedData.drop(bad_types, inplace=True)
        
    def _parse_schema(self):
        # Required columns:
        self.required_columns = []
        
        # doc. type:
        self.document_type = self.schema_obj['title'].split(" ")[0]
        
        # What do we need to check:
        self.type = {}
        self.pattern = {}
        self.accepted = {}
        self.range = {}
        self.schema_columns = []
        
        # Loop through all possible fields and extract criteria:
        for key, field in self.schema_obj['properties'].items():
            # List of all possible columns:
            self.schema_columns.append(field['user_friendly'])

            # Type is mandatory:
            if field['type'] == 'string':
                self.type[field['user_friendly']] = str
            elif field['type'] == 'number':
                self.type[field['user_friendly']] = float
            else:
                self.type[field['user_friendly']] = eval(field['type'])
            
            # Range is optional:
            if 'minimum' in field and 'maximum' in field:
                self.range[field['user_friendly']] = (field['minimum'], field['maximum'])
            
            # Pattern is optional:
            if 'pattern' in field:
                self.pattern[field['user_friendly']] = field['pattern']
            
            # Accepted is optional:
            if 'enum' in field:
                self.accepted[field['user_friendly']] = field['enum']
            
            # Add required column:
            if key in self.schema_obj['required']:
                self.required_columns.append(field['user_friendly'])
    
    def select_columns(self):
        # Get unexpected columns:
        unexpected_columns = list(set(self.uploadedData.columns).difference(self.schema_columns))
        if unexpected_columns:
            self.add_report('[Warning] Unexpected columns: {}'.format(','.join(unexpected_columns)))
            

        # Get missing columns:
        missing_columns = list(set(self.schema_columns).difference(self.uploadedData.columns))
        if missing_columns:
            self.add_report('[Warning] The following columns are missing: {}'.format(','.join(missing_columns)))

        self.failed['unexpected_columns'] = unexpected_columns
        self.failed['missing_columns'] = missing_columns
        
        # Add report if everything is OK:
        if len(unexpected_columns) == 0 and len(missing_columns) == 0:
            self.add_report('[Info] The columns in the uploaded table looks OK.')
        
    def find_empty_rows(self):
        # Get empty rows:
        empty_rows = self.uploadedData.index[self.uploadedData.isnull().all(axis = 1)].tolist()
        
        # Add report: 
        if len(empty_rows) > 0:
            self.add_report('[Warning] The following lines are empty: {}'.format(', '.join(map(str, empty_rows)))) 

        # Save problem:
        self.failed['empty_rows'] = empty_rows

    def check_mandatory_fields(self):
        missing_indices = []
        for column in self.required_columns:
            missing = self.uploadedData.index[self.uploadedData[column].isna()].tolist()
            if len(missing) > 0:
                self.add_report('[Warning] {} field is missing in row(s): {}'.format(column, ', '.join(map(str, missing))))
                missing_indices += missing
        
        # Save problem:
        self.failed['Missing_fields'] = missing_indices
        
    def check_data_type(self):
        bad_types = []
        
        # Looping through all columns and check header:
        for column, expected_type in self.type.items():
            # Set column type in dataframe:
            self.uploadedData.loc[:,column].astype(expected_type, errors = 'ignore', copy=False)
            
            # Check all values for type:
            failed_types = self.uploadedData.loc[~self.uploadedData[column].isna() &
                      ~self.uploadedData.loc[:,column].apply(lambda x: isinstance(x, expected_type)),column]

            # Looping through:
            for index, value in failed_types.iteritems():
                self.add_report('[Warning] Type test failed in row: {}. {} is not {}'.format(
                        index, value, str(expected_type.__name__)))
                if not index in bad_types: bad_types.append(index)
                                
        # Save problem:
        self.failed['bad_types'] = bad_types
        
    def check_pattern(self):
        bad_pattern = []
        
        # Looping through all columns were values expected to follow a pattern:
        for column, pattern in self.pattern.items():
            for index, value in self.uploadedData.loc[ ~self.uploadedData[column].str.match(pattern, na = False),column].items():
                self.add_report('[Warning] Pattern failed in row: {} in {}, value is {}'.format(
                        index, column, value))
                if not index in bad_pattern: bad_pattern.append(index)
        
        # Removing lines:
        self.uploadedData.drop(bad_pattern, inplace=True)
        
    def check_set(self):
        return(1)
    
    def add_report(self, report = None):
        if not hasattr(self, 'validation_report'):
            self.validation_report = 'Schema validation for {} spreadsheet\n\n'.format(self.document_type)
            self.validation_report += '[Info] Date: {:%Y %h %d}'.format(datetime.date.today())
                        
        else:
            self.validation_report += '\n' + report
                        
    def get_report(self):
        return(self.validation_report)
    
    def __len__(self):
        return(len(self.uploadedData))