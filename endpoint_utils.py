from collections import OrderedDict
import logging
from urllib.parse import unquote
from flask import url_for


def _create_href(method_name, params=None):
    params = params or {}
    params['_external'] = True
    print(params)
    return {'href': unquote(
        url_for(method_name, **params)
    )}

