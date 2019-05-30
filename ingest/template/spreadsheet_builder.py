import pandas.io.formats.excel
import xlsxwriter
import pandas as pd
from argparse import ArgumentParser
import io


# Resetting pandas dataframe header:
pandas.io.formats.excel.header_style = None


class SpreadsheetBuilder:

    # Data line marker:
    dataMarker = 'Add your data below this line'

    def __init__(self, output_file = None):

        if not output_file:
            output_file = io.BytesIO()

        self.output_file = output_file
        
        # Define workbook object:
        self.writer_object = pd.ExcelWriter(output_file, engine ='xlsxwriter')
        self.workbook = self.writer_object.book

        # Define formatting for the column headers:
        self.header_format = self.workbook.add_format({'bold': True, 'bg_color': '#D0D0D0', 
                                                       'font_size': 12, 'valign': 'vcenter','locked': True})

        # Define formatting for the column descriptions:
        self.desc_format = self.workbook.add_format({'font_color': '#808080', 'italic': True, 'text_wrap': True, 
                                                     'font_size': 12, 'valign': 'bottom', 'locked': True})

    def generate_workbook(self, dataframes=dict()):
        
        # Looping through all the dataframes and add each to the workbook as a separate sheet:
        for title, df in dataframes.items():
            
            # Generate the template dataframe:
            templateSheet = self._prepare_dataframe(df)
            
            # Pass the template dataframe to the builder:
            self._build_sheet(templateSheet, title)

    def save_workbook(self):
        self.workbook.close()
        return self.output_file
        
    def _prepare_dataframe(self, df):
        
        # As part of the table preparation, the description field needs to be generated:
        def _generate_description(row):
            description = row['DESCRIPTION']

            # Adding example:
            if not pd.isna(row['EXAMPLE']):
                description += ' Example: {}'.format(row['EXAMPLE'])

            # Providing the list of accepted values:
            if not pd.isna(row['ACCEPTED']):
                description += ' Select from: {}'.format(', '.join(row['ACCEPTED'].split('|')))

            # Adding example:
            if not pd.isna(row['LOWER']) and not pd.isna(row['UPPER']):
                description += ' Values between {} and {}'.format(row['LOWER'], row['UPPER'])

            return description
        
        # Creating a dataframe for the excel:
        templateSheet = pd.DataFrame([df.HEADER.tolist()], columns = df.apply(_generate_description, axis = 1))
        return templateSheet

    def _build_sheet(self, df, title):
        
        # Adding data to sheet:
        df.to_excel(self.writer_object, index = False, sheet_name = title)
        worksheet_object = self.writer_object.sheets[title] 
        
        # Set column width:
        worksheet_object.set_column(0, len(df.columns), 20)
        
        # Formatting comment row:
        worksheet_object.set_row(0, None, self.desc_format)
        
        # Formatting column names:
        worksheet_object.set_row(1, None, self.header_format)

        # Freeze top rows:
        worksheet_object.freeze_panes(1, 0)
        worksheet_object.freeze_panes(2, 0)
        
        # Add Comment and format row:
        worksheet_object.write(3, 0, "Add your data below this line", self.header_format)
        worksheet_object.set_row(3, None, self.header_format)

if __name__ == '__main__':

    # default input files:
    inputFiles = {
        'studies' : '../../schema_definitions/study_schema.xlsx',
        'associations' : '../../schema_definitions/association_schema.xlsx',
        'samples' : '../../schema_definitions/sample_schema.xlsx',
        'genotyping_technologies' : '../../schema_definitions/genotyping_schema.xlsx',
    }

    parser = ArgumentParser()

    parser.add_argument("-o", "--output", dest="output", help="Name of the output spreadsheet", required=False, default = 'output.xlsx')
    parser.add_argument("-i", "--input", dest="input", help="List of excel spreadsheets describing the schema.", required=False, nargs='+')

    args = parser.parse_args()
    outputFileName = args.output
    
    # If input files are not specified we read all built in ones:
    if args.input:
        inputDataFrames = { f : pd.read_excel(f, index_col=False) for f in args.input }
    else:
        inputDataFrames = { title : pd.read_excel(filename, index_col=False) for title, filename in inputFiles.items() }


    spreadsheet_builder = SpreadsheetBuilder(output_file = outputFileName)
    spreadsheet_builder.generate_workbook(inputDataFrames) 
    spreadsheet_builder.save_workbook()

