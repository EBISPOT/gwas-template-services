
import logging
from logging import config

# Import custom functions:
from config.properties import Configuration as conf


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

    # TODO: test if the tabneme is valid.
    # TODO: test data types... sometime in the future

    # Handling independent parameters:
    for criteria, value in filterParameters.items():
        if not value: continue # We only care about true parameters.

        if criteria == 'effect':
            criteria = value

        if tabname in conf.filters[criteria]:
            for field in conf.filters[criteria][tabname]:
                schemaDf.loc[schemaDf.NAME == field, 'DEFAULT'] = True

    # Handling compound parameters:
    if filterParameters['curator'] and filterParameters['backgroundTrait']:
        if tabname in conf.filters['curator_backgroundTrait']:
            for field in conf.filters['curator_backgroundTrait'][tabname]:
                schemaDf.loc[schemaDf.NAME == field, 'DEFAULT'] = True

    # Filter dataframe:
    schemaDf = schemaDf.loc[schemaDf.DEFAULT]

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
