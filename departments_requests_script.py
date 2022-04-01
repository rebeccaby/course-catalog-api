#!usr/bin/env python3

import requests
import json

BASE = 'http://127.0.0.1:5000/'

if __name__ == '__main__':
    with open('departments.json', 'r') as f:
        data = json.load(f)
    departments = data['departments']
    
    for d in departments:
        try:
            if d['id'] == 'BSAD/BUSA':
                r = requests.put(BASE + '/department/' + d['id'].replace('/', '-'), d)
            else:
                r = requests.put(BASE + '/department/' + d['id'], d)
            r.raise_for_status()
        except:
            raise SystemExit(f"Error on {d['id']}")