from flask import Flask, request, send_file
import os
import zipfile
import glob
from collections import defaultdict
from itertools import combinations as combs

app = Flask(__name__)
app.config.from_pyfile('config.py')


class Game:
    def __init__(self, _group_size):
        self.team_names = []
        self.num_teams = len(self.team_names)
        self.groups = defaultdict(list)
        self.group_size = _group_size
        self.matches = []
        self.match_history = []

    def add_team(self, name):
        self.team_names.append(name)
        self.num_teams = len(self.team_names)

    def assign_groups(self):
        group_no = 0
        count = 0
        for team in self.team_names:
            self.groups[group_no].append(team)

            count += 1
            if count == self.group_size:
                group_no += 1
                count = 0

    def create_matches(self, num_players = app.config['PLAYERS_PER_MATCH']):
        for key in self.groups:
            self.matches.extend(combs(self.groups[key], num_players))

    def get_next_match(self):
        # need to implement logic to give next match after every call
        self.match_history.append(self.matches.pop())
        return self.match_history[-1]

    def serve_match(self, source=app.config['GAMEFILES_DIRECTORY'], dest=app.config['MATCH_DIRECTORY']):
        while len(self.matches) > 0:
            next_match = self.get_next_match()
            zip_name = dest + 'Match' + str(len(self.match_history)) + '.zip'
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for team in next_match:
                    zipdir(source + team, zipf)


def unzip_files(game: Game, source=app.config['ZIP_DIRECTORY'], dest=app.config['GAMEFILES_DIRECTORY']):
    files = glob.iglob(source + '*')
    for file in files:
        file = os.path.basename(file)
        game.add_team(os.path.splitext(file)[0])

        with zipfile.ZipFile(os.path.join(source, file), 'r') as zip_ref:
            zip_ref.extractall(dest)


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))

@app.route("/")
def send_report():
    game = Game(10)
    unzip_files(game)
    game.assign_groups()
    game.create_matches()
    game.serve_match()
    zip_name = 'matches\\' + 'Match' + '1' + '.zip'

    return send_file(os.path.join(app.root_path,  zip_name))
