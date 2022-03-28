#!usr/bin/env python3

import requests
import json

BASE = 'http://127.0.0.1:5000/'

if __name__ == '__main__':
    """ with open('departments.json', 'r') as f:
        data = json.load(f)
    departments = data['departments'] """
    
    with open('courses.json', 'r') as f:
        data = json.load(f)
    courses = data['courses']
    
    """ for dept in departments:
        r = requests.put(BASE + '/department/' + dept['id'], dept) """

    for course in courses:
        r = requests.put(BASE + '/course/' + course['id'], course)



# Scraper:
#   Store departments/classes to respective local files
# 
# Notes:
# Active venv: $ source venv/bin/activate
# Deactivate venv: $ deactivate
