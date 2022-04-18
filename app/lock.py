import os
from pathlib import Path
from time import sleep
from random import random


def touch(file_name):
    Path(file_name).touch()


def lock(resource_name):
    file_name = f'.lock_{resource_name}'
    while os.path.isfile(file_name):
        sleep(random())
    touch(file_name)


def unlock(resource_name):
    file_name = f'.lock_{resource_name}'
    os.remove(file_name)


def lock_matches():
    lock('matches')


def unlock_matches():
    unlock('matches')
