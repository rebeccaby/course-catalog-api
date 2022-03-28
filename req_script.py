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
# POST Script:
#   Check diff of department and class files 
#   If no files exist, just exit after saying 'run the other program'
#   Send each request, wait 500ms in between
#   Save and display all failed POST requests at the end
#   Have test function to GET all courses
#
#
#
# Notes:
# Active venv: $ source venv/bin/activate
# Deactivate venv: $ deactivate
