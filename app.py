from flask import Flask, request, send_file, json
import os
import zipfile
import glob
from collections import defaultdict
from itertools import combinations as combs

app = Flask(__name__)
app.config.from_pyfile('config.py')


class Game:
    """ This class represents the whole game """
    def __init__(self, _group_size):
        self.team_names = []
        self.num_teams = len(self.team_names)
        self.groups = defaultdict(list)
        self.group_size = _group_size
        self.matches = []
        self.match_history = []

    def add_team(self, name):
        """ add a team to the game and update number of teams """
        self.team_names.append(name)
        self.num_teams = len(self.team_names)

    def assign_groups(self):
        """ assign each team to a group """
        group_no = 0
        count = 0
        for team in self.team_names:
            self.groups[group_no].append(team)

            count += 1
            if count == self.group_size:
                group_no += 1
                count = 0

    def create_matches(self, num_players = app.config['PLAYERS_PER_MATCH']):
        """ Inside each group create every possible match with num_players number of players """
        for key in self.groups:
            self.matches.extend(combs(self.groups[key], num_players))

    def get_next_match(self):
        """ get the next match to be played """
        self.match_history.append(self.matches.pop())
        return self.match_history[-1]

    def create_match_zips(self, source=app.config['GAMEFILES_DIRECTORY'], dest=app.config['MATCH_DIRECTORY']):
        """ create zip files which include the files of the teams that have to compete in a match """
        if not os.path.exists(dest):
            os.makedirs(dest)

        while len(self.matches) > 0:
            match = self.get_next_match()
            zip_name = dest + 'Match' + str(len(self.match_history)) + '.zip'

            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for team in match:
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


@app.route("/get-match")
def send_report():
    matches = glob.glob(app.config['MATCH_DIRECTORY']+'*')
    print(len(matches))

    played_path = os.path.join(app.root_path, 'played/')
    if not os.path.exists(played_path):
        os.makedirs(played_path)

    os.replace(matches[0], played_path + matches[0].split('\\')[-1])
    matches = glob.glob(played_path+'*')
    print(len(matches))
    return send_file(matches[0])


@app.route("/init-game")
def init_game():
    try:
        game = Game(10)
        unzip_files(game)
        game.assign_groups()
        game.create_matches()
        game.create_match_zips()

        return 'game initialised'

    except:
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
