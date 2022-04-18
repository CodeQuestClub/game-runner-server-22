import glob
import os
from logs import log
import zipfile
import shutil
from teams import Team, save_all_teams


def clean_dir_name(dir_name):
    if dir_name[-1] == '/':
        return dir_name[:-1]
    return dir_name


def force_delete_dir(folder_name):
    folder_name = clean_dir_name(folder_name)
    try:
        shutil.rmtree(f'{folder_name}/')
    except OSError:
        pass


def process_all_submissions(raw_submissions_folder, clean_submissions_folder, profile_pictures_folder):
    raw_submissions_folder = clean_dir_name(raw_submissions_folder)
    clean_submissions_folder = clean_dir_name(clean_submissions_folder)
    profile_pictures_folder = clean_dir_name(profile_pictures_folder)

    teams = []
    raw_files = glob.glob(raw_submissions_folder + '/*')

    log(f'Looping through raw submissions inside {raw_files}:')
    for raw_submission in raw_files:
        log(f'- {raw_submission}')
        team_name = os.path.splitext(os.path.basename(raw_submission))[0]

        # Unzip their submission in a temp folder
        os.makedirs('temp', exist_ok=True)
        try:
            with zipfile.ZipFile(raw_submission, 'r') as zip_ref:
                zip_ref.extractall('temp/')
        except Exception:
            log(f"Submission of team {team_name} is not a valid zip file.")
            with open('temp/main.py', 'w') as f:
                f.write('')
        

        # Find the folder containing main.py (clean_dir)
        clean_dir = None
        for subdir, _, files in os.walk('temp'):
            if 'main.py' in files:
                clean_dir = subdir
                break
        
        # No folder contains main.py - make an empty main.py so their code would fail
        if clean_dir is None:
            log(f"Submission of team {team_name} does not contain a main.py file.")
            with open('temp/main.py', 'w') as f:
                f.write('')
            clean_dir = 'temp'

        # Copy team profile picture in their zip file
        profile_destination = f'{clean_dir}/profile.png'
        if not os.path.isfile(profile_destination):
            extensions = ['png', 'jpg', 'jpeg']
            for extension in extensions:
                potential_profile_pic = f'{profile_pictures_folder}/{team_name}.{extension}'
                if os.path.isfile(potential_profile_pic):
                    shutil.copyfile(potential_profile_pic, profile_destination)
                    break

        # Archive their submission again
        shutil.make_archive(f'{clean_submissions_folder}/{team_name}', 'zip', clean_dir)
        force_delete_dir('temp')

        # Add team to teams
        teams.append(Team(team_name, f'{clean_submissions_folder}/{team_name}.zip'))
    
    # All submissions processed, save teams
    save_all_teams(teams)


def make_submissions_public(clean_submissions_folder, static_folder):
    clean_submissions_folder = clean_dir_name(clean_submissions_folder)
    static_folder = clean_dir_name(static_folder)

    force_delete_dir(f'{static_folder}/submissions')
    shutil.copytree(clean_submissions_folder, f'{static_folder}/submissions')
