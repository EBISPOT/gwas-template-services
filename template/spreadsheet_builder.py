import pandas.io.formats.excel
import pandas as pd
from argparse import ArgumentParser
import io

# Resetting pandas dataframe header:
pandas.io.formats.excel.header_style = None

class SpreadsheetBuilder:
    '''
    This class generates formatted template files in xlsx format based on the provided dataframes.
    '''

    # Data line marker:
    dataMarker = 'Add your data below this line'

    # Formatting of the column header:
    formatHeader = {'bold': True, 'bg_color': '#D0D0D0',
                    'font_size': 12, 'valign': 'vcenter','locked': True}

    # Formatting of the column description:
    formatDescription = {'font_color': '#808080', 'italic': True, 'text_wrap': True,
                         'font_size': 12, 'valign': 'bottom', 'locked': True}

    # Mandatory field highlight:
    formatHighlightManadatory = {'bold': True, 'bg_color': '#F2CBA9',
                                 'font_size': 12, 'valign': 'vcenter','locked': True}

    def __init__(self, output_file = None, version = None):

        if not output_file:
            output_file = io.BytesIO()

        self.output_file = output_file
        
        # Define workbook object:
        self.writer_object = pd.ExcelWriter(output_file, engine ='xlsxwriter')
        self.workbook = self.writer_object.book

        # Set version if specified:
        if version:
            self.workbook.set_properties({
                'comments' : 'schemaVersion={}'.format(version),
                'subject': 'GWAS Catalog template spreadsheet.'})

        # Define formatting for the column headers:
        self.header_format = self.workbook.add_format(self.formatHeader)

        # Define formatting for the column descriptions:
        self.desc_format = self.workbook.add_format(self.formatDescription)

        # Defining format for header highlights:
        self.mandatory_format = self.workbook.add_format(self.formatHighlightManadatory)

        # Define column format to set values as text:
        self.setTextFormat = self.workbook.add_format()
        self.setTextFormat.set_num_format('@')

    def generate_workbook(self, tabname, dataframe):
        """

        :param tabname: name of the spreadsheet tab of the excel file.
        :type tabname: str
        :param dataframe: the schema definition as a dataframe
        :type dataframe: pandas DataFrame
        :return: None

        """

        # Generate the template dataframe:
        templateSheet = self._prepare_dataframe(dataframe)

        # Adding data to sheet:
        templateSheet.to_excel(self.writer_object, index=False, sheet_name=tabname)
        worksheet_object = self.writer_object.sheets[tabname]

        # Set column width:
        worksheet_object.set_column(0, len(templateSheet.columns), 20, self.setTextFormat)

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

        # highlight mandatory fields:
        for index, title in dataframe.loc[dataframe.MANDATORY, 'HEADER'].items():
            worksheet_object.write(1, index, title, self.mandatory_format)

    def save_workbook(self):
        self.workbook.close()
        return self.output_file
        
    def _prepare_dataframe(self, df):
        
        # As part of the table preparation, the description field needs to be generated:
        def _generate_description(row):
            description = row['DESCRIPTION'] if isinstance(row['DESCRIPTION'], str) else ''

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


def main():

    parser = ArgumentParser()
    parser.add_argument("-o", "--output", dest="output", help="Name of the output spreadsheet", required=False,
                        default='output.xlsx')
    parser.add_argument("-i", "--input", dest="input", help="List of tab names and the corresponding excel spreadsheets describing the schema separated by colon.",
                        required=True, nargs='+')

    args = parser.parse_args()
    outputFileName = args.output

    # Initialize spreadsheet object:
    spreadsheet_builder = SpreadsheetBuilder(output_file=outputFileName)

    # The provided input files are read and the data is prepared for the spreadsheet building:
    for sheet in args.input:
        name, file = sheet.split(':')
        spreadsheet_builder.generate_workbook(name, pd.read_excel(file, index_col=False))

    spreadsheet_builder.save_workbook()


if __name__ == '__main__':
    main()
