import requests
from datetime import datetime

DELTA_FLAG = 5
SUSPICOUS_SCORE_FLAG = True

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
        "scores": score_data,
        "personal_best": personal_best,
        "suspicous_flag": False
    }

    if (personal_best['delta'] > DELTA_FLAG + 60) and SUSPICOUS_SCORE_FLAG:
        scenario_data['suspicous_flag'] = True

    return scenario_data


def find_flagged_runs(collected_data):
    flagged_runs = []

    for scenario in collected_data:
        if scenario != None:
            if scenario['suspicous_flag']:
                flagged_runs.append(scenario)

    return flagged_runs


def filter_results(collected_data):


def get_url():
    print("Enter profile name to scan:")
    username = input()
    page = 0
    access_failed = False
    collected_data = []

    while access_failed == False and page < 5:
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
            access_failed = True

    if page != 0:
        filter_results(collected_data)

if __name__ == '__main__':
    get_score_data('Zaiko', 'VT 1w4ts Novice S5')
    get_url()
