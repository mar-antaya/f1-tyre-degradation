"""Dated latest-race roster, separate from historical lap observations."""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

PATH = Path(__file__).parent / 'data' / 'current_grid.json'
URL = 'https://api.jolpi.ca/ergast/f1/current/last/results.json?limit=100'

def parse_roster(payload):
    races = payload['MRData']['RaceTable']['Races']
    if len(races) != 1:
        raise ValueError('Expected one latest completed race')
    race = races[0]
    drivers = []
    for result in race['Results']:
        d = result['Driver']
        drivers.append({'id': d['driverId'], 'code': d['code'],
                        'name': d['givenName'] + ' ' + d['familyName']})
    if len(drivers) < 10 or len({d['code'] for d in drivers}) != len(drivers):
        raise ValueError('Incomplete or duplicate roster; keeping saved snapshot')
    return {'season': int(race['season']), 'round': int(race['round']),
            'race': race['raceName'], 'race_date': race['date'],
            'fetched_at': datetime.now(timezone.utc).isoformat(),
            'source': URL, 'drivers': sorted(drivers, key=lambda d: d['name'])}

def read_roster():
    return json.loads(PATH.read_text())

def refresh_roster():
    with urlopen(Request(URL, headers={'User-Agent': 'COTA-Education/1.0'}), timeout=20) as response:
        snapshot = parse_roster(json.load(response))
    temporary = PATH.with_suffix('.tmp')
    temporary.write_text(json.dumps(snapshot, indent=2))
    temporary.replace(PATH)
    return snapshot

if __name__ == '__main__':
    snapshot = refresh_roster()
    print(f"Saved {len(snapshot['drivers'])} drivers from {snapshot['season']} round {snapshot['round']}")
