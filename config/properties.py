
# All configurations required for the application:

class Configuration():

    # Template filter definitions:
    filters = {
        'curator' : {
            'addColumn' : {
                'notes': ['study_tag', 'note', 'note_subject', 'status'],
                'study': ['efo_trait'],
                'sample': ['ancestry']
            }
        },
        'haplotype' : {
            'addColumn': {
                'association' : ['haplotype_id']
            }
        },
        'beta' : {
            'addColumn': {
                'association': ['beta', 'beta_unit', 'standard_error']
            }
        },
        'OR' : {
            'addColumn': {
                'association': ['odds_ratio', 'ci_lower', 'ci_upper']
            }
        },
        'backgroundTrait' : {
            'addColumn': {
                'study' : ['background_trait']
            }
        },
        'snpxsnp' : {

        },
        'curator_backgroundTrait': {
            'addColumn': {
                'study': ['background_efo_trait']
            }
        },

        'accessionIDs' : {
            'removeColumn': {
                'study': ['array_manufacturer', 'genotyping_technology', 'array_information', 'imputation', 'variant_count', 'statistical_model', 'study_description', 'trait'],
                'sample': ['study_tag', 'stage', 'size', 'cases', 'controls', 'sample_description', 'ancestry_category', 'ancestry', 'ancestry_description', 'country_recruitement'],
                'association': ['study_tag', 'variant_id', 'pvalue', 'pvalue_text', 'effect_allele', 'other_allele', 'effect_allele_frequency']
            },
            'addColumn': {
                'study': ['study_accession']
            }
        }
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


