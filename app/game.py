from random import shuffle
import json
from logs import log
from itertools import combinations
from match import Match, save_all_matches


def create_game_groups(teams, number_of_groups):
    teams = [team.name for team in teams]
    teams_per_group = len(teams) // number_of_groups
    shuffle(teams)

    groups = [teams[start:start + teams_per_group] for start in range(0, len(teams), teams_per_group)]
    if len(groups) > number_of_groups:
        remainder = groups[-1]
        del groups[-1]
        while len(remainder) > 0:
            index = min([(len(groups[x]), x) for x in range(len(groups))])[1]
            groups[index].append(remainder[0])
            del remainder[0]
    
    with open('../data/groups.json', 'w') as f:
        f.write(json.dumps(groups))


def load_groups():
    try:
        with open('../data/groups.json', 'r') as f:
            return json.loads(f.read())
    except Exception:
        log('Unable to load the groups from json file')
        return []


def create_random_matches(groups, random_matches_per_team):
    matches = []
    for group in groups:
        matches_count = {x: 0 for x in group}
        while min(matches_count.values()) < random_matches_per_team:
            min_teams = [x for x in group if matches_count[x] == min(matches_count.values())]
            try:
                second_min_value = sorted(list(set(matches_count.values())))[1]
                second_min_teams = [x for x in group if matches_count[x] == second_min_value]
            except IndexError:
                second_min_teams = []
            shuffle(min_teams)
            shuffle(second_min_teams)
            selected_teams = min_teams[:4] + second_min_teams[:max(0, 4-len(min_teams))]
            if len(selected_teams) != 4:
                log(f'A match was created with {len(selected_teams)} teams! breaking the group loop')
                break
            matches.append(Match(selected_teams))
            for selected_team in selected_teams:
                matches_count[selected_team] += 1

    return matches


def create_all_matches(groups):
    matches = []
    for group in groups:
        matches.extend([Match(teams) for teams in combinations(group, 4)])
    return matches


def create_game_matches(groups, strategy, random_matches_per_team=None):
    if strategy == 'random':
        mapless_matches = create_random_matches(groups, random_matches_per_team)
    elif strategy == 'full':
        mapless_matches = create_all_matches(groups)
    else:
        log('Matching strategy not found - creating no matches.')
        mapless_matches = []

    with open('../data/maps.json', 'r') as f:
        maps = json.loads(f.read())
    
    matches = []
    for mapless_match in mapless_matches:
        for map_name in maps:
            matches.append(Match(mapless_match.teams, map_name=map_name))

    save_all_matches(matches)

