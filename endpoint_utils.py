import json
import pandas as pd

# Import custom functions:
from config.properties import Configuration as conf


def preFillDataParser(inputString):
    """
    This function parses the input string given to the template generator.
    Checks a few things then returns a dictionary of dataframes.

    {
        sheetName1 : [
            {columnName : value1},
            {columnName : value2},
            {columnName : value3},
            {columnName : value4},
        ]
    }

    :param inputString:
    :type JSON string
    :return: pandas dataframe
    """

    # Try to parse the data as JSON:
    try:
        inputData = json.loads(inputString)
    except TypeError:
        return "[Error] Pre-fill data cannot be read as JSON."

    # If it goes alright, test if it is a dictionary:
    if not isinstance(inputData, dict):
        return "[Error] Pre-fill data should be an dictionary of lists."

    # Output data is a dictionary with pandas dataframes:
    outputDataDict = {}

    # If it is a dictionary, test if values are lists of dictionaries:
    for sheetName, values in inputData.items():
        if not isinstance(values, list):
            return "[Error] Pre-fill data should be an array of dictionaries"

        for value in values:
            if not isinstance(value, dict):
                return "[Error] Pre-fill data should be an array of dictionaries"

        # If it's values are dictionaries, read as pandas dataframe
        try:
            outputDataDict[sheetName] = pd.DataFrame(values)
        except TypeError:
            return "[Error] Study data could not be imported as "

    # Return data:
    return outputDataDict


def schema_parser(filterParameters, filters, tabname, schemaDf):
    """
    This function filters out the schema definition based on the provided parameters.
    Only the default columns are visible: the list of default columns can be changed by the provided parameters.
    Parameter definitions are in the properties file.

    :param filterParameters: the payload of the POST request
    :type dict

    :param tabname: name of the schema eg. study or association
    :type str

    :param schemaDf: the schema definition of the entity
    :type pandas DataFrame

    :return: dictionary with the filtered dataframe.
    """

    # TODO: test data types... sometime in the future

    # Test if

    # Generate compound parameters:
    try:
        if filterParameters['curator'] and filterParameters['backgroundTrait']:
            filterParameters['curator_backgroundTrait'] = True
    except KeyError:
        pass

    # Filtering based on the provided parameters:
    for criteria, value in filterParameters.items():
        if not value: continue # We only care about true parameters.

        # The effect will be the carried value:
        if criteria == 'effect':
            criteria = value

        if criteria not in filters: continue  # We won't let undocumented filters breaking the code.

        # Adding columns as defined by the properties file:
        if 'addColumn' in filters[criteria] and tabname in filters[criteria]['addColumn']:
            for field in filters[criteria]['addColumn'][tabname]:
                print('Adding {} for {}'.format(field, tabname))
                schemaDf.loc[schemaDf.NAME == field, 'DEFAULT'] = True

        # removing columns as defined by the properties file:
        if 'removeColumn' in filters[criteria] and tabname in filters[criteria]['removeColumn']:
            for field in filters[criteria]['removeColumn'][tabname]:
                schemaDf.loc[schemaDf.NAME == field, 'DEFAULT'] = False

    # Filter dataframe:
    try:
        schemaDf = schemaDf.loc[schemaDf.DEFAULT]
    except:
        print(tabname)

    # Resetting index:
    schemaDf = schemaDf.reset_index(drop=True)
    return(schemaDf)


def set_log_path(conf):
    conf.LOG_CONF['handlers'][conf.LOGGER_HANDLER]['filename'] = conf.logging_path + "/" + conf.LOGGER_LOG
    return conf.LOG_CONF


def _set_log_level(LOG_CONF, LOG_LEVEL):
    for handler in LOG_CONF['handlers']:
        LOG_CONF['handlers'][handler]['level'] = LOG_LEVEL
    for loggr in LOG_CONF['loggers']:
        LOG_CONF['loggers'][loggr]['level'] = LOG_LEVEL
    return LOG_CONF
