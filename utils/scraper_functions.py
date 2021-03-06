#!usr/bin/env python3

import unicodedata
import requests
from bs4 import BeautifulSoup

BASE = 'https://catalog.uta.edu/coursedescriptions/'

""" Gets the containers with the links for each department
Parameters: None
Return: bs4.element.ResultSet containing a bs4.element.Tag for each department
"""
def setup_department_catalogs():
    try:
        r = requests.get(BASE)
        r.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise SystemError(f"A Connection error occurred to {BASE}.")
    except requests.exceptions.HTTPError:
        raise SystemError(f"An HTTP error occurred to {BASE}.")

    base_page = BeautifulSoup(r.text, 'html.parser')
    
    # "sitemap" class - one large block with all departments and their links
    department_container = base_page.find('div', class_='sitemap')

    if department_container is not None:
        # "a" tag - getting just the links to each department's course catalog page
        return department_container.find_all('a')
    else:
        raise SystemExit("No container to be parsed was found in variable \"department_container\".")

""" Extract just the necessary information to put together each department's URL
Parameters: departments -> bs4.element.ResultSet: contains multiple bs4.element.Tags
Return: list of all departments and their department IDs
"""
def get_departments_list(departments):
    departments_list = []

    for d in departments:
        # Separate department name & id
        # Made it backwards to make getting the ID a tiny bit simpler
        dept_str = str(d.string)[::-1].strip(')')
        dept_info = dept_str.split('(', 1)

        # Get department name & id (ignore 1st line, which is empty for some reason)
        if len(dept_info) > 1:
            departments_list.append({
                'id': dept_info[0][::-1], 
                'name': dept_info[1][:0:-1]
            })

    return departments_list

""" Access a department page
Parameters: id -> str: uppercase department ID
            uppercase_depts -> list: department IDs requiring uppercase URLs
Return: bs4.BeautifulSoup object of department page, modified uppercase_depts
"""
def get_department_page(id, uppercase_depts):
    # NOTE: Department pages are accessed with the lowercase department ID appended in most cases.
    # A few departments have exceptions, using uppercase or differing from the explicit ID in the department title.
    # These edge cases have their conditions listed below.

    try:
        # # The expected URL
        r = requests.get(f'{BASE}{id.lower()}')
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        try:
            if uppercase_depts and any(elem == id for elem in uppercase_depts):
                r = requests.get(f'{BASE}{id}')
                r.raise_for_status()
                uppercase_depts.remove(id)
            # BSAD/BUSA - URL only uses "bsad", not "bsad/busa"
            if id == "BSAD/BUSA":
                r = requests.get(f'{BASE}bsad')
                r.raise_for_status()
            # NURS-HI - URL uses "nurshi", not "nurs-hi"
            if id == "NURS-HI":
                r = requests.get(f'{BASE}nurshi')
                r.raise_for_status()
            # Don't think raise_for_status() can be moved here because of having to remove the uppercase department
        except requests.exceptions.HTTPError:
            raise SystemError("HTTPError - URL was invalid.")
    except requests.exceptions.RequestException:
        raise SystemError("RequestException - An unknown error has occurred.")

        # TODO: handle possible ConnectionError exception as well?

    return BeautifulSoup(r.text, 'html.parser'), uppercase_depts

""" Extract all course information from a department page
Parameters: department_page -> bs4.BeautifulSoup: department page as nested data structure
            id -> str: uppercase department ID
            asl_flag -> bool: marker that requires a different way to extract course information
Return: bs4.element.ResultSet of all course description containers, asl_flag boolean
"""
def get_departments_course_catalog(department_page, id, asl_flag):
    if id == "BSAD/BUSA":
        # NOTE: HTML in BSAD/BUSA page is slightly different from other department pages. courses are directly from department_page,
        # instead of having to get the courses list container first.
        return department_page.find_all('div', class_='courseblock'), asl_flag # ResultSet
    try:
        # The expected formatting for most departments
        courses_container = department_page.find('div', class_='courses') # Tag class
        courses = courses_container.find_all('div', class_='courseblock') # ResultSet class
    # ASL department has entirely different HTML formatting
    except AttributeError:
        courses_container = department_page.find('div', id='textcontainer')
        courses = courses_container.find_all('p')
        asl_flag = True

    return courses, asl_flag

""" Get course description from tags
Parameters: course -> bs4.element.Tag: 'div' that contains all information for a course
            asl_flag -> bool: marker that requires a different way to extract course information
Return: course description string
"""
def get_course_description(course, asl_flag):
    # Course descriptions are in <p>, after <strong>
    description = ""
    if asl_flag is True:
        for sibling in course.br.next_siblings:
            description += str(sibling.string).strip('\n')
    else:
        # NOTE: Tag has multiple children, which always starts with the course description & ends with a
        # 'br' and None tag. Additional children in between may include prerequisites in 'a' tags, or
        # more text in the prerequisites.
        description_block = course.find('p', class_='courseblockdesc')
        for child in description_block.children:
            if child.name != 'br' and not str(child).isspace():
                # BUG: add 1 whitespace before <a> text
                description += str(child.string).strip('\n')

    return description

""" Get course prerequisites from the course description
Parameters: description -> str: course description
Return: course prerequisites string
"""   
def get_course_prerequisites(description):
    # All courses have 'Prerequisite: ' or 'Prerequisites: '
    course_line = description.split('Prerequisite')
    
    # If there were any prerequisites
    if len(course_line) > 1:
        # Originally had '\xa0' instead of ' '
        prerequisites = unicodedata.normalize("NFKD", course_line[1])

        # Delete ': '
        prerequisites = prerequisites[2:]

        # Delete leading ' ' and ending '.' if exists
        if prerequisites.startswith(' '):
            prerequisites = prerequisites[1:]
        if prerequisites.endswith('.'):
            prerequisites = prerequisites[:-1]
    else:
        prerequisites = ""

    return prerequisites

""" Get course TCCN id, if available
Parameters: header_info -> str: tail end of course header that contains an equivalent TCCN ID
Return: TCCN ID string
"""
def get_course_tccn_id(header_info):
    # TCCN ID always inside parentheses
    temp = header_info.split('=')
    return temp[-1][1:-1]