import importlib
from os import listdir, getcwd
from os.path import isfile, join


def get_list_of_engines():
    engine_path = '.\\uniback\\plugins\\engines'
    for file in listdir(engine_path):
        print(file)


get_list_of_engines()