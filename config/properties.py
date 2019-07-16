
# All configurations required for the application:

class Configuration():

    # List of schemas that needs to be served:
    schemas = {
        'study': '/schema_definitions/study_schema.xlsx',
        'association': '/schema_definitions/association_schema.xlsx',
        'sample': '/schema_definitions/sample_schema.xlsx',
        'note': '/schema_definitions/notes_schema.xlsx'
    }

    # Template filter definitions:
    filters = {
        'curator' : {
            'note' : ['study_tag', 'note', 'note_subject', 'status'],
            'study' : ['efo_trait'],
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
        'backgroundTrait' : {
            'study' : ['background_trait']
        },
        'snpxsnp' : {

        },
        'curator_backgroundTrait': {
            'study': ['background_efo_trait']
        },
    }

    # Schema version:
    schemaVersion = "1.0"

    # Data line separator:
    triggerRow = "Add your data below this line"

    # Logging related configuration:
    logging_path = "./logs"
    LOG_LEVEL = "INFO"
    LOGGER_LOG = "logger.log"
    LOGGER_HANDLER = "logger"
    LOG_CONF = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'void': {
                'format': ''
            },
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'logger': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'maxBytes': 10485760,
                'backupCount': 20,
                'encoding': 'utf8'
            },
        },
        'loggers': {
            '': {
                'handlers': ['logger'],
                'level': 'INFO'
            },
        }
    }


