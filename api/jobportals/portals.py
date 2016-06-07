# coding: utf-8

# Copyright Luna Technology 2016
# Matthieu Riviere <mriviere@luna-technology.com>


PORTAL_FORMS = [
    {
        'pk': 1,
        'portal': {
            'name': 'HADDOCK',
            'pk': 1
        },
        'name': 'HADDOCK server: the Easy interface',
        'original_url': 'http://haddock.science.uu.nl/enmr/services/HADDOCK2.2/haddockserver-easy.html',
        'submit_url': 'http://haddock.science.uu.nl/cgi/enmr/services/HADDOCK2.2/haddockserver-easy.cgi',
        'template_name': 'ejpf_haddock_easy.html',
    },
    {
        'pk': 2,
        'portal': {
            'name': 'HADDOCK',
            'pk': 1
        },
        'name': 'HADDOCK server: the Prediction interface',
        'original_url': 'http://haddock.science.uu.nl/enmr/services/HADDOCK2.2/haddockserver-prediction.html',
        'submit_url': 'http://haddock.science.uu.nl/cgi/enmr/services/HADDOCK2.2/haddockserver-prediction.cgi',
        'template_name': 'ejpf_haddock_prediction.html',
    }
]
