import time
import json
from logs import log


class Match:
    IN_QUEUE = 'queue'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'

    def __init__(self, teams, status=None, map_name=None, results={}, worker_id=None, start_time=None):
        self.status = status if status is not None else self.IN_QUEUE
        self.teams: list = teams
        # {team_name: score}
        self.results = results
        self.worker_id = worker_id
        self.map_name = map_name
        self.start_time = start_time

    @classmethod
    def from_dict(cls, value):
        return cls(**value)

    def assign_worker(self, worker_id):
        self.worker_id = worker_id
        self.status = self.IN_PROGRESS
        self.start_time = int(time.time())

    def unassign(self):
        self.worker_id = None
        self.status = self.IN_QUEUE
        self.start_time = None
    
    def is_expired(self):
        return self.start_time is not None and int(time.time()) - self.start_time >= 20 * 60


def save_all_matches(matches):
    normalized_matches = [match.__dict__ for match in matches]
    with open('../data/matches.json', 'w') as f:
        f.write(json.dumps(normalized_matches))


def load_matches():
    try:
        with open('../data/matches.json', 'r') as f:
            raw_matches = json.loads(f.read())
            return [Match.from_dict(raw_match) for raw_match in raw_matches]
    except Exception:
        log('Unable to load the matches from json file')
        return []


def unassign_all_expired_matches(matches):
    for match in matches:
        if match.is_expired():
            match.unassign()
    save_all_matches(matches)
