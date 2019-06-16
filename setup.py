from distutils.core import setup

'''
This script defines the installation and packaging properties for the python packages
included in this repository
'''

setup(
    name='templateServices',
    version='0.1',
    packages=['config', 'validation', 'template'],
    entry_points={
        "console_scripts": ['gwas-spreadsheet_builder = template.spreadsheet_builder:main',
                            'gwas-JSON_schema_builder = template.schemaJson_builder:main',
                            'gwas-validator = validation.validator:main']
    },
    url='https://github.com/EBISPOT/gwas-template-services',
    license='',
    author='Daniel Suveges',
    author_email='dsuveges@ebi.ac.uk',
    description='Package to manage template related services for the data deposition system of the GWAS Catalog',
    install_requires=['pandas==0.22.0', 'xlsxwriter==1.1.8', 'flask', 'gunicorn', 'eventlet', 'pytest-cov']
)