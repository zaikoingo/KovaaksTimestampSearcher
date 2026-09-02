import requests
from datetime import datetime

DELTA_FLAG = 4
SUSPICOUS_SCORE_FLAG = False

def get_score_data(username, scenario_name):
    raw_score_data = requests.get(f'https://kovaaks.com/webapp-backend/user/scenario/last-scores/by-name?username={username}&scenarioName={scenario_name}').json()
    score_data = []
    personal_best = {"score": -99999}
    if ('error' in raw_score_data):
        return None

    for score in raw_score_data:
        epoch = int(score['attributes']['epoch'])
        challengeStart = score['attributes']['challengeStart'].split(':')

        startTimeFormatted = {
            "hours": int(challengeStart[0]),
            "minutes": int(challengeStart[1]) % 30,
            "seconds": int(challengeStart[2].split('.')[0]),
            "miliseconds": int(challengeStart[2].split('.')[1])
        }

        epochFormatted = datetime.fromtimestamp(epoch / 1000)
        epochMinutes = epochFormatted.minute % 30
        startTimeTotal = (startTimeFormatted['minutes'] * 60) + startTimeFormatted['seconds'] + (startTimeFormatted['miliseconds'] / 1000)
        epochTotal = (epochMinutes * 60) + epochFormatted.second + (epochFormatted.microsecond / 1000000)

        delta = epochTotal - startTimeTotal
        if (delta < 0):
            delta += 30 * 60

        pause_duration = "N/A"
        if ('pauseDuration' in score['attributes']):
            pause_duration = int(score['attributes']['pauseDuration'])
            delta -= pause_duration

        parsed_score = {
            "score": float(score['score']),
            "fps": float(score['attributes']['avgFps']),
            "pauseDuration": pause_duration,
            "delta": delta,
            "date": f'{epochFormatted.month}/{epochFormatted.day}/{epochFormatted.year}'
        }

        score_data.append(parsed_score)
        if (personal_best is None or parsed_score['score'] >= personal_best['score']):
            personal_best = parsed_score

    scenario_data = {
        "scenario_name": scenario_name,
        "scores": score_data,
        "personal_best": personal_best,
        "suspicous_flag": False
    }

    if (not 'delta' in personal_best):
        return None

    if (personal_best['delta'] > DELTA_FLAG + 60):
        scenario_data['suspicous_flag'] = True

    return scenario_data


def find_flagged_runs(collected_data):
    flagged_runs = []

    for scenario in collected_data:
        if scenario != None:
            if scenario['suspicous_flag']:
                flagged_runs.append(scenario)

    return flagged_runs


def date_filter(date, runs):
    collected_runs = []

    for scenario in runs:
        if scenario != None:
            if scenario['personal_best']['date'] == date:
                collected_runs.append(scenario)

    return collected_runs


def filter_results(collected_data):
    to_print = collected_data

    to_print = date_filter("3/25/2026", to_print)

    if SUSPICOUS_SCORE_FLAG:
        to_print = find_flagged_runs(to_print)

    for scenario in to_print:
        personal_best = scenario['personal_best']
        score_data = scenario['scores']
        scenario_name = scenario['scenario_name']

        if (scenario['suspicous_flag']) :
            print(f"!! (Flagged) {scenario_name} !!")
        else:
            print(scenario_name)

        print(f"\t{personal_best}")
        for score in score_data:
            print(f"\t\t{score}")


def get_playlist_scenarios(playlist_name):
    url = f'https://kovaaks.com/webapp-backend/playlist/playlists?page=0&max=20&search={playlist_name}'
    raw_scenario_data = requests.get(url).json()
    print(raw_scenario_data)
    scenario_titles = []
    scenario_list = raw_scenario_data['data']['scenarioList']
    for scenario in scenario_list:
        scenario_titles.append(scenario['scenarioName'])

    return scenario_titles

def get_user_playlist_scenarios(username, playlist_name):
    collected_data = []
    scenario_titles = get_playlist_scenarios(playlist_name)
    for scenario in scenario_titles:
        collected_data.append(get_score_data(username, scenario))
        print(scenario['scenarioName'])

    return collected_data

def get_user_scenarios(username):
    page = 0
    access_failed = False
    collected_data = []

    while access_failed == False and page < 50:
        url = f'https://kovaaks.com/webapp-backend/user/scenario/total-play?username={username}&page={page}&max=10&sort_param[]=count'
        response = requests.get(url)

        if (response.status_code == 200):
            scenarios = response.json()['data']
            for scenario in scenarios:
                collected_data.append(get_score_data(username, scenario['scenarioName']))
                print(scenario['scenarioName'])
            page += 1

        else:
            if page == 0:
                print("ERROR: Not successful")
                return None
            access_failed = True
    return collected_data


def prompt():
    print("Enter profile name to scan:")
    username = input()
    collected_data = []

    print("Which option would you like to scan?")
    print("\t1. - Scan by username")
    print("\t2. - Scan by profile")

    valid_input = False
    while not valid_input:
        user_choice = input()
        if user_choice == '1':
            collected_data = get_user_scenarios(username)
            valid_input = True
        elif user_choice == '2':
            print("Enter playlist name:")
            playlist_name = input()
            collected_data = get_user_playlist_scenarios(username, playlist_name)
            valid_input = True
        else:
            print("Invalid input, try again")

    filter_results(collected_data)

if __name__ == '__main__':
    prompt()
