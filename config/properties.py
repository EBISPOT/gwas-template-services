
# All configurations required for the application:

class Configuration():

    # Template filter definitions:
    filters = {
        'curator' : {
            'addColumn' : {
                'notes': ['study_tag', 'note', 'note_subject', 'status'],
                'study': ['efo_trait', 'background_efo_trait'],
                'sample': ['ancestry'],
                'association': ['study_tag', 'variant_id', 'pvalue', 'pvalue_text', 'proxy_variant', 'effect_allele',
                                'other_allele', 'effect_allele_frequency', 'odds_ratio', 'ci_lower', 'ci_upper', 'beta',
                                'beta_unit', 'standard_error'],

            }
        },
        'summaryStats' : {
            'removeColumn': {
                'study': [ 'background_trait', 'efo_trait','array_manufacturer', 'genotyping_technology','efo_trait', 'background_efo_trait',
                          'array_information', 'imputation', 'variant_count', 'statistical_model', 'study_description'],
                'sample': ['study_tag', 'stage', 'size', 'cases', 'controls', 'sample_description', 'ancestry_category',
                           'ancestry', 'ancestry_description', 'country_recruitement'],
                'notes': ['study_tag', 'note', 'note_subject', 'status'],
                'association': ['study_tag', 'variant_id', 'pvalue', 'pvalue_text', 'proxy_variant', 'effect_allele',
                                'other_allele', 'effect_allele_frequency', 'odds_ratio', 'ci_lower', 'ci_upper', 'beta',
                                'beta_unit', 'standard_error']
            },
            'addColumn': {
                'study': ['study_accession', 'sample_description','cohort', 'cohort_id']
            }
        }
    }

    # Schema version:
    schemaVersion = "1.2"

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


