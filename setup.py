from distutils.core import setup

'''
This script defines the installation and packaging properties for the python packages
included in this repository
'''

setup(
    name='templateServices',
    version='0.1',
    include_package_data=True,
    package_data={ 'schema_definitions' : ['*.xlsx'] },
    packages=['config', 'template','schema_definitions'],
    entry_points={
        "console_scripts": ['gwas-spreadsheet_builder = template.spreadsheet_builder:main',
                            'gwas-JSON_schema_builder = template.schemaJson_builder:main',
                            'gwas_schema_definitions = schema_definitions.schemaVersion:main']
    },
    url='https://github.com/EBISPOT/gwas-template-services',
    license='',
    author='Daniel Suveges',
    author_email='dsuveges@ebi.ac.uk',
    description='Package to manage template related services for the data deposition system of the GWAS Catalog',
    install_requires=['pandas==0.22.0', 'xlsxwriter==1.1.8', 'flask', 'gunicorn', 'eventlet', 'pytest-cov'],
)
