from collections import OrderedDict
import logging
from urllib.parse import unquote
from flask import url_for
from ftplib import FTP


def _create_href(method_name, params=None):
    params = params or {}
    params['_external'] = True
    print(params)
    return {'href': unquote(
        url_for(method_name, **params)
    )}


def create_ftp_directories(submissionId, studyTags):
    ftpAddress = ' ftp-private.ebi.ac.uk'
    user = 'gwas_cat'
    passWord = 'y9vYPfvg'

    # Initialize connection:
    ftp = FTP(ftpAddress, user, passWord)

    # Go to gwas directory:

    # Create folder with submission ID:

    # Enter directory:

    # Create directories for all study tags:

