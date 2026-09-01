import requests
from datetime import datetime

DELTA_FLAG = 5
SUSPICOUS_SCORE_FLAG = True

def get_score_data(username, scenario_name):
    raw_score_data = requests.get(f'https://kovaaks.com/webapp-backend/user/scenario/last-scores/by-name?username={username}&scenarioName={scenario_name}').json()
    score_data = []
    personal_best = {"score": -99999}
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

    if (personal_best['delta'] > DELTA_FLAG + 60):
        scenario_data['suspicous_flag'] = True

    return scenario_data




def get_url():
    print("Enter profile name to scan:")
    url = input()
    response = requests.get(url)
    if (response.status_code == 200):
        print("Profile URL OK")
        get_score_data('Zaiko', 'VT Pasu Rasp Novice')
    else:
        print("ERROR: Not successful")

if __name__ == '__main__':
    get_score_data('Zaiko', 'VT 1w4ts Novice S5')
    get_url()
