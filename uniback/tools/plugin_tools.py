import importlib
from os import listdir, getcwd
from os.path import isfile, join, splitext
from uniback.dictionary.uniback_variables import Config


def get_list_of_engines():
    return_list = []
    engine_path = Config.ENGINES_LOCATION
    for file in listdir(engine_path):
        return_list.append((splitext(file)[0], splitext(file)[0]))
    return return_list


def get_engine_class(engine, engine_class):
    return_class = getattr(importlib.import_module('uniback.plugins.engines.' + engine), engine_class)
    return return_class


def get_engine_classes(engine):
    classes = get_engine_class(engine, 'AVAILABLE_JOBS')
    classes = [(item, item) for item in classes]
    return classes
