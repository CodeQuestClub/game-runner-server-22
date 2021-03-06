import time
import json
from logs import log
from lock import lock_matches, unlock_matches
from random import random
import shutil
import os


_last_backup = 0
_matches = []


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
        return self.status == self.IN_PROGRESS and self.start_time is not None and int(time.time()) - self.start_time >= 20 * 60


def save_all_matches(matches, lock=True):
    global _last_backup
    global _matches
    normalized_matches = [match.__dict__ for match in matches]
    if time.time() - _last_backup >= 60:
        with open('../data/matches.json', 'w') as f:
            f.write(json.dumps(normalized_matches))
        _last_backup = time.time()
    _matches = matches
    # if lock:
    #     lock_matches()
    # try:
    #     normalized_matches = [match.__dict__ for match in matches]
    #     if time.time() - _last_backup >= 60:
    #         with open('../data/matches_backup.json', 'w') as f:
    #             f.write(json.dumps(normalized_matches))
    #         _last_backup = time.time()
    #     with open('../data/matches.json', 'w') as f:
    #         f.write(json.dumps(normalized_matches))
    #     time.sleep(random()/8)
    # except Exception:
    #     pass
    # if lock:
    #     unlock_matches()


def load_matches(lock=True):
    global _matches
    if len(_matches) > 0:
        return _matches
    try:
        with open('../data/matches.json', 'r') as f:
            raw_matches = json.loads(f.read())
        _matches = [Match.from_dict(raw_match) for raw_match in raw_matches]
    except Exception as e:
        log('Unable to load the matches from json file')
        log(str(e))
    return _matches
    # if lock:
    #     lock_matches()
    # result = []
    # restored = 0
    # while restored < 2:
    #     try:
    #         with open('../data/matches.json', 'r') as f:
    #             raw_matches = json.loads(f.read())
    #         result = [Match.from_dict(raw_match) for raw_match in raw_matches]
    #         break
    #     except Exception as e:
    #         log('Unable to load the matches from json file')
    #         log(str(e))
    #         try:
    #             restore_matches()
    #         except Exception as ee:
    #             log('Failed to restore matches')
    #             log(str(ee))
    #         restored += 1
    # if lock:
    #     unlock_matches()
    # return result


def unassign_all_expired_matches(matches, lock=True):
    found_any = False
    for match in matches:
        if match.is_expired():
            found_any = True
            match.unassign()
    if found_any:
        save_all_matches(matches, lock)

    
def restore_matches():
    if os.path.isfile('../data/matches.json'):
        os.remove('../data/matches.json')
    shutil.copyfile('../data/matches_backup.json', '../data/matches.json')
