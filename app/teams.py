import json


class Team:
    def __init__(self, name, submission_zip_path, score=0):
        self.name = name
        self.score = score
        self.submission_zip_path = submission_zip_path

    @classmethod
    def from_dict(cls, value):
        return cls(**value)


def save_all_teams(teams):
    normalized_data = [x.__dict__ for x in teams]
    with open('../data/teams.json', 'w') as f:
        f.write(json.dumps(normalized_data))


def load_all_teams():
    teams = []
    try:
        with open('../data/teams.json', 'r') as f:
            raw_teams = json.loads(f.read())
            teams = [Team.from_dict(x) for x in raw_teams]
    except FileNotFoundError:
        print("Can't find teams.json file in data.")
    return teams