# coding: utf-8

# Copyright Luna Technology 2015
# Matthieu Riviere <mriviere@luna-technology.com>

import random
import string


def choices_from_mapping(mapping):
    ''' return a list of tuple (key, value) from dict '''
    return list([(k, mapping[k]) for k in mapping])


def generate_random_string(length):
    characters = string.letters + string.digits
    return ''.join([random.choice(characters) for i in range(length)])


def reverse_key_value_dict(dictionnary):
    return {value: key for key, value in dictionnary.items()}
