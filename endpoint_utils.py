# Import custom functions:
from config.properties import Configuration as conf

def parse_prefilled_study_data(inputString):
    """
    This function parses the input string given to the template endpoint as studyData
    Checks a few things then returns a dataframe.

    :param inputString:
    :type JSON string
    :return: pandas dataframe
    """

    # Try to parse the data as JSON

    # If it goes alright, test if it is an array


    # If it is an array, test if values are dictionaries.


    # If it's values are dictionaries, read as pandas dataframe




def filter_parser(filterParameters, tabname, schemaDf):
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

    # Generate compound parameters:
    if filterParameters['curator'] and filterParameters['backgroundTrait']:
        filterParameters['curator_backgroundTrait'] = True

    # Filtering based on the provided parameters:
    for criteria, value in filterParameters.items():
        if not value: continue # We only care about true parameters.

        # The effect will be the carried value:
        if criteria == 'effect':
            criteria = value

        if criteria not in conf.filters: continue  # We won't let undocumented filters breaking the code.

        # Adding columns as defined by the properties file:
        if 'addColumn' in conf.filters[criteria] and tabname in conf.filters[criteria]['addColumn']:
            for field in conf.filters[criteria]['addColumn'][tabname]:
                print('Adding {} for {}'.format(field, tabname))
                schemaDf.loc[schemaDf.NAME == field, 'DEFAULT'] = True

        # removing columns as defined by the properties file:
        if 'removeColumn' in conf.filters[criteria] and tabname in conf.filters[criteria]['removeColumn']:
            for field in conf.filters[criteria]['removeColumn'][tabname]:
                schemaDf.loc[schemaDf.NAME == field, 'DEFAULT'] = False

    # Filter dataframe:
    schemaDf = schemaDf.loc[schemaDf.DEFAULT]

    # Resetting index:
    schemaDf = schemaDf.reset_index(drop=True)
    return(schemaDf)

def pre_fill_sheet(spreadsheetDf, colname, values):
    return 1


def set_log_path(conf):
    conf.LOG_CONF['handlers'][conf.LOGGER_HANDLER]['filename'] = conf.logging_path + "/" + conf.LOGGER_LOG
    return conf.LOG_CONF


def _set_log_level(LOG_CONF, LOG_LEVEL):
    for handler in LOG_CONF['handlers']:
        LOG_CONF['handlers'][handler]['level'] = LOG_LEVEL
    for loggr in LOG_CONF['loggers']:
        LOG_CONF['loggers'][loggr]['level'] = LOG_LEVEL
    return LOG_CONF
