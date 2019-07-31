import pandas.io.formats.excel
from xlsxwriter.utility import xl_rowcol_to_cell
import pandas as pd
from argparse import ArgumentParser
import io

# Resetting pandas dataframe header:
pandas.io.formats.excel.header_style = None

class SpreadsheetBuilder:
    """
    This class generates formatted template files in xlsx format based on the provided dataframes.
    """

    # What can users do if worksheet is protected:
    protectionOptions = {
        'format_columns': True,
    }

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

    # Protected format:
    formatProtected = {'locked' : 0}

    def __init__(self, output_file = None, version = None, dataMarker = None):

        if not output_file:
            output_file = io.BytesIO()

        if dataMarker:
            self.dataMarker = dataMarker

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

        # Defining format for protected cells:
        self.protected_format = self.workbook.add_format(self.formatProtected)

        # Define column format to set values as text:
        self.setTextFormat = self.workbook.add_format()
        self.setTextFormat.set_num_format('@')

        # Saving column names to this dictionary:
        self._columnNames = {}

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

        # Saving column names:
        self._columnNames[tabname] = dataframe.NAME.tolist()

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
        worksheet_object.write(3, 0, self.dataMarker, self.header_format)
        worksheet_object.set_row(3, None, self.header_format)

        # highlight mandatory fields:
        for index, title in dataframe.loc[dataframe.MANDATORY, 'HEADER'].items():
            worksheet_object.write(1, index, title, self.mandatory_format)

    def save_workbook(self):
        self.workbook.close()
        return self.output_file

    def add_values(self, tabname, preFillDataFrame):
        """
        This function adds data to a given column of a given sheet

        :param tabname:
        :param colname:
        :param data:
        :return:
        """

        # Test if tab exists:
        if tabname not in self.writer_object.sheets:
            print("[Warning] {} tab does not exist in spreadsheet.".format(tabname))
            return None

        # Protecting spreadsheet: .add_format({'locked': 0})
        self.writer_object.sheets[tabname].protect(password= 'gwas', options=self.protectionOptions)

        # Excluding all columns of the dataframe which is not in the sheet:
        preFillDataFrame = preFillDataFrame[[x for x in preFillDataFrame.columns if x in self._columnNames[tabname]]]
        if len(preFillDataFrame.columns) == 0: return None

        # Get column index for all columns:
        colIndexes = {}
        for columnName in preFillDataFrame.columns:
            colIndexes[columnName] = self._columnNames[tabname].index(columnName)

        # Adding index as a column:
        preFillDataFrame.loc[preFillDataFrame.index, 'rowIndex'] = preFillDataFrame.index

        # A private function is applied on all rows of the prefill dataframe:
        def __add_prefill_data(row):

            # Loop-through all columns:
            for columnName, value in row.items():
                # Skipping rowIndex:
                if columnName == 'rowIndex': continue

                # Get column index:
                colIndex = colIndexes[columnName]

                # Update value in dataframe:
                cell = xl_rowcol_to_cell(row['rowIndex'] + 4, colIndex)
                self.writer_object.sheets[tabname].write(cell, value)

        # Looping through all the
        for columnIndex in range(len(self._columnNames[tabname])):

            # Skipping columns where we added data:
            if columnIndex in colIndexes.values():
                self.writer_object.sheets[tabname].set_column(columnIndex, columnIndex, 35)
            else:
                # Empty columns are released from the lock:
                self.writer_object.sheets[tabname].set_column(columnIndex, columnIndex,  20, self.protected_format)

        preFillDataFrame.apply(__add_prefill_data, axis = 1)

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
