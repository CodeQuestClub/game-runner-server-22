import os

static_folder = 'static'
raw_submissions_folder = '../data/raw_submissions'
clean_submissions_folder = '../data/submissions'
profile_pictures_folder = '../data/profile_pictures'


create_game_groups = not os.path.isfile('../data/groups.json')
number_of_groups = 1  # 8

create_game_matches = not os.path.isfile('../data/matches.json')
# matching_strategy = 'random'
matching_strategy = 'full'
random_matching_matches_per_team = 1 # None