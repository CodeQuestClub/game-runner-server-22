from flask import Flask, request
import json
import config
from logs import log
from files import process_all_submissions, make_submissions_public
from game import create_game_groups, load_groups, create_game_matches
from teams import load_all_teams, save_all_teams
from match import Match, unassign_all_expired_matches, load_matches, save_all_matches
from lock import lock_matches, unlock_matches

app = Flask(__name__)


def load_all_objects():
    return load_all_teams(), load_groups(), load_matches()


def initialize():
    log("Initializing...")
    process_all_submissions(
        config.raw_submissions_folder,
        config.clean_submissions_folder,
        config.profile_pictures_folder
    )
    make_submissions_public(
        config.clean_submissions_folder,
        config.static_folder
    )
    teams = load_all_teams()

    if config.create_game_groups:
        create_game_groups(teams, config.number_of_groups)
    groups = load_groups()

    if config.create_game_matches:
        create_game_matches(
            groups,
            config.matching_strategy,
            config.random_matching_matches_per_team
        )

initialize()


def json_response(response, status=200):
    return json.dumps(response), status, {'ContentType': 'application/json'}


@app.route('/')
def heartbeat():
    teams, groups, matches = load_all_objects()
    normalized_teams = [x.__dict__ for x in teams]
    normalized_matches = [x.__dict__ for x in matches]
    normalized_groups = groups
    return json_response({
        'teams': normalized_teams,
        'groups': normalized_groups,
        'matches': normalized_matches
    })


@app.route("/get-match", methods=['POST'])
def get_match():
    _, __, matches = load_all_objects()
    lock_matches()
    try:
        unassign_all_expired_matches(matches, False)
        worker_id = request.json['worker_id']
        index: int = None
        match: Match = None
        match_found = False
        for index, match in enumerate(matches):
            if match.status == Match.IN_QUEUE:
                match_found = True
                break
        if not match_found:
            result = json_response({'ok': False, 'message': 'No more matches', 'shutdown': True})
        else:
            match.assign_worker(worker_id)
            save_all_matches(matches, False)
            result = json_response({
                'ok': True,
                'match_index': index,
                'map_name': match.map_name,
                'teams': [
                    {'name': team_name, 'submission': f'{request.url_root}static/submissions/{team_name}.zip'}
                    for team_name in match.teams
                ]
            })
    except Exception as e:
        result = e
    
    unlock_matches()
    if isinstance(result, Exception):
        raise result
    return result


@app.route('/match-results', methods=['POST'])
def match_results():
    """
    Passed JSON should look like:
    {
        match_index: <index>,
        results: {
            <team_name>: <score>,
            <team_name>: <score>,
            <team_name>: <score>,
            <team_name>: <score>
        }
    }
    """
    teams, _, matches = load_all_objects()
    data = request.json
    if not data:
        log('Invalid match-results request received (not json).')
        return json_response({'ok': False, 'message': 'Could not parse JSON in request'})
    
    match_index = data['match_index']
    if match_index >= len(matches) or match_index < 0:
        log('Invalid match index was given to match-results.')
        return json_response({'ok': False, 'message': 'Match index not found.'})
    
    if matches[match_index].status != Match.IN_PROGRESS:
        log('Match index given to match-results is not IN_PROGRESS.')
        return json_response({'ok': False, 'message': 'Match not in progress.'})

    match = matches[match_index]
    results = data['results']
    if any(team_name not in match.teams for team_name in results.keys()):
        log('Teams do not match in the match given to match-results')
        return json_response({'ok': False, 'message': 'Match details do not match the match index.'})

    match.status = Match.DONE
    match.results = results
    for team in teams:
        if team.name in match.teams:
            team.score += match.results[team.name]
    save_all_teams(teams)
    save_all_matches(matches)
    return json_response({'ok': True, 'message': 'Match results saved.'})
