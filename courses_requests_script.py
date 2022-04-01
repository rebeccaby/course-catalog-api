#!usr/bin/env python3

import requests
import json

BASE = 'http://127.0.0.1:5000/'

if __name__ == '__main__':
    with open('courses.json', 'r') as f:
        data = json.load(f)
    courses = data['courses']
    
    for c in courses:
        try:
            r = requests.put(BASE + '/course/' + c['id'], c)
            r.raise_for_status()
        except:
            raise SystemExit(f"Error on {c['id']}.")