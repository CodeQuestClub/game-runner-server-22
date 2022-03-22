"""Flask configuration"""
import os

ZIP_DIRECTORY = os.path.join(os.path.dirname(__file__), 'zipFiles/')
GAMEFILES_DIRECTORY = os.path.join(os.path.dirname(__file__), 'gameFiles/')
MATCH_DIRECTORY = os.path.join(os.path.dirname(__file__), 'matches/')
PLAYERS_PER_MATCH = 4