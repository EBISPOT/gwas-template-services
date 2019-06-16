import os


class Configuration():

    # Path where the template files are saved:
    rootPath = os.path.dirname(os.path.realpath(__file__))
    uploadFolder = '{}/../uploadedTemplates'.format(rootPath)  #'/Users/dsuveges/Project/gwas-template-services/uploadedTemplates'

    # Credentials for the private sftp:
    FTP = {
        'ftpServer': 'ftp-private.ebi.ac.uk',
        'ftpUser': 'gwas_cat',
        'ftpPassword': 'y9vYPfvg'
    }

    # GWAS deposition service app:
    serviceAppAddress = 'http://snoopy.ebi.ac.uk'
    serviceAppPort = '5000'

    # List of schemas that needs to be served:
    schemas = {
        'study': '/schema_definitions/study_schema.xlsx',
        'association': '/schema_definitions/association_schema.xlsx',
        'sample': '/schema_definitions/sample_schema.xlsx',
        'note': '/schema_definitions/notes_schema.xlsx'
    }

    # Template filter definitions:
    # {
    #     "curator": true,
    #     "haplotype": true,
    #     "snpxsnp": true,
    #     "effect": "beta", // or "OR"
    #                             "backgroundTrait": true,
    # }
    filters = {
        'curator' : {
            'note' : ['study_tag', 'note', 'note_subject', 'status'],
            'study' : ['efo_trait','background_efo_trait'],
            'sample' : ['ancestry']
        },
        'haplotype' : {
            'association' : ['haplotype_id']
        },
        'beta' : {
            'association': ['beta', 'beta_unit', 'standard_error']
        },
        'OR' : {
            'association': ['odds_ratio', 'ci_lower', 'ci_upper']
        },
        'background' : {
            'study' : ['background_trait']
        }
    }


