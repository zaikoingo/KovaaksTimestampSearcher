import requests
from datetime import datetime

def get_score_data(username, scenarioName):
    raw_score_data = requests.get(f'https://kovaaks.com/webapp-backend/user/scenario/last-scores/by-name?username={username}&scenarioName={scenarioName}').json()
    score_data = []
    for score in raw_score_data:
        epoch = int(score['attributes']['epoch'])
        challengeStart = score['attributes']['challengeStart'].split(':')

        startTimeFormatted = {
            "hours": int(challengeStart[0]),
            "minutes": int(challengeStart[1]) % 30,
            "seconds": int(challengeStart[2].split('.')[0]),
            "miliseconds": int(challengeStart[2].split('.')[1])
        }
        print(epoch)
        epochFormatted = datetime.fromtimestamp(epoch / 1000)
        epochMinutes = epochFormatted.minute % 30
        startTimeTotal = (startTimeFormatted['minutes'] * 60) + startTimeFormatted['seconds'] + (startTimeFormatted['miliseconds'] / 1000)
        epochTotal = (epochMinutes * 60) + epochFormatted.second + (epochFormatted.microsecond / 1000000)

        delta = epochTotal - startTimeTotal

        pause_duration = "N/A"
        if 'pauseDuration' in score['attributes']:
            pause_duration = int(score['attributes']['pauseDuration'])
            delta -= pause_duration

        parsed_score = {
            "score": score['score'],
            "fps": score['attributes']['avgFps'],
            "pauseDuration": pause_duration,
            "delta": delta
        }

        score_data.append(parsed_score)
        print(parsed_score)


def get_url():
    print("Enter profile name to scan:")
    url = input()
    response = requests.get(url)
    if response.status_code == 200:
        print("Profile URL OK")
        get_score_data('Zaiko', 'VT Pasu Rasp Novice')
    else:
        print("ERROR: Not successful")

if __name__ == '__main__':
    get_score_data('Zaiko', 'VT 1w4ts Novice S5')
    get_url()
