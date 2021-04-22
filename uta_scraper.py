#!usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import unicodedata

BASE = 'https://catalog.uta.edu/coursedescriptions/'

def get_one_department():
    pass

def get_all_departments(departments):
    departments_list = []

    for d in departments:
        # Separate department name & id
        dept_str = str(d.string)[::-1]
        dept_str = dept_str[1:]
        dept_info = dept_str.split('(', 1)

        # Get department name & id (ignore 1st line, which is empty for some reason)
        if len(dept_info) > 1:
            dept_info[0] = dept_info[0][::-1]
            dept_info[1] = dept_info[1][:0:-1]
            departments_list.append(dept_info)

    return departments_list

def get_all_courses(dept, uppercase_depts):
    pass

if __name__ == '__main__':
    r = requests.get(BASE)

    base_page = BeautifulSoup(r.text, 'html.parser')
    department_container = base_page.find('div', class_='sitemap')
    departments = department_container.find_all('a')

    # Webpages that use uppercase in the GET requests
    uppercase_depts = ['UNIV-AT', 'UNIV-BU', 'UNIV-EN', 'UNIV-HN', 'UNIV-SC', 'UNIV-SW']

    all_departments = get_all_departments(departments)

    # TODO: clean below and put into functions or something, this is bad

    all_courses = []
    i = 0

    # Fetching all courses in each department ~~~
    for dept in all_departments:
        asl_univ = False
        num_of_courses = 0

        # These departments are uppercase in the URL
        if uppercase_depts and any(elem == dept[0] for elem in uppercase_depts):
            univ = dept[0]
            r = requests.get(f'{BASE}{dept[0]}')
            uppercase_depts.remove(univ)
        else:
            r = requests.get(f'{BASE}{dept[0].lower()}')

        department_page = BeautifulSoup(r.text, 'html.parser')
        
        # Only ASL department has different HTML formatting
        try:
            course_container = department_page.find('div', class_='courses')
            courses = course_container.find_all('div', class_='courseblock')
        except AttributeError:
            course_container = department_page.find('div', id='textcontainer')
            courses = course_container.find_all('p')
            asl_univ = True
        
        for c in courses:
            num_of_courses = num_of_courses + 1
            course_json = {}

            # NOTE: can find by class name here as well, but description text is wrapped in a 'strong' tag.
            # There's only 1 'strong' tag per course block, so find by 'strong' instead to cut down on a
            # few lines of code.
            course_title = c.find('strong')

            # Originally had '\xa0' instead of ' '
            course_string = unicodedata.normalize("NFKD", str(course_title.string))
            
            # Get course dept & id
            course_info = course_string.split('.', maxsplit=1)
            course_dept = course_info[0].split(' ')[0]
            course_id = int(course_info[0].split(' ')[1])

            # Get course number of hours
            course_info = course_info[1].rsplit('.', maxsplit=2)
            course_hours = int(course_info[1].strip().split(' ')[0])

            # Get course description (leave as original string)
            course_name = course_info[0].strip()

            # Get course TCCN id, if available
            course_tccn = None
            if course_info[2]:
                temp = course_info[2].split('=')
                course_tccn = temp[-1][1:-1]

            # TODO: Course descriptions for ASL are in <p>, after <strong>
            if asl_univ is True:
                #course_block_desc = c.find
                pass
            else:
                # NOTE: Tag has multiple children, which always starts with the course description & ends with a
                # 'br' and None tag. Additional children in between may include prerequisites in 'a' tags, or
                # more text in the prerequisites.
                course_desc_block = c.find('p', class_='courseblockdesc')
                course_desc = ''
                for child in course_desc_block.children:
                    if child.name != 'br' and not str(child).isspace():
                        # BUG: add 1 whitespace before <a> text
                        course_desc += str(child.string).strip('\n')

            # All courses have 'Prerequisite: ' or 'Prerequisites: '
            course_line = course_desc.split('Prerequisite')
            
            # If there were any prerequisites
            if len(course_line) > 1:
                # Originally had '\xa0' instead of ' '
                course_prerequisites = unicodedata.normalize("NFKD", course_line[1])

                # Delete ': '
                course_prerequisites = course_prerequisites[2:]

                # Delete ending '.' and ' ' for when course has 'Prerequisites: '
                if course_prerequisites[0] == ' ':
                    course_prerequisites = course_prerequisites[1:]
                if course_prerequisites[-1] == '.':
                    course_prerequisites = course_prerequisites[:-1]
            else:
                course_prerequisites = None
            
            course_json.update({
                'id': course_id,
                'department': course_dept,
                'name': course_name,
                'description': course_desc,
                'num_of_hours': course_hours,
                'prerequisites': course_prerequisites,
                'tccn_id': course_tccn})
        
        # Get number of courses per department
        all_departments[i].append(num_of_courses)
        i = i + 1

        # Add course to catalog
        all_courses.append(course_json)