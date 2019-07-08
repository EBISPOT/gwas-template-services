
from config.properties import Configuration as conf
import pandas as pd
import os


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

def schema_reader(schema_name):
    """

    :param schema_name: This is the name of the schema eg. study, association etc.
    :type str
    :return: dataframe with the
    """
    # # List of schemas that needs to be served:
    # schemas = {
    #     'study': '/schema_definitions/study_schema.xlsx',
    #     'association': '/schema_definitions/association_schema.xlsx',
    #     'sample': '/schema_definitions/sample_schema.xlsx',
    #     'note': '/schema_definitions/notes_schema.xlsx'
    # }
    dir_path = os.path.dirname(os.path.realpath(__file__))

    try:
        schema_dataframe = pd.read_excel(dir_path + conf.schemas[schema_name], index_col=False)
        schema_dataframe = schema_dataframe.where((schema_dataframe.notnull()), None)
        return schema_dataframe
    except KeyError as e:
        return '[Error] Schema: {} is not found in the configuration. Available schemas: {}'.format(schema_name, list(conf.schemas.keys()))





