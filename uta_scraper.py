#!usr/bin/env python3

import json
from utils.scraper_functions import *

if __name__ == '__main__':
    try:
        # URLs that use uppercase in the GET requests, regular method won't work
        uppercase_depts = ['UNIV-AT', 'UNIV-BU', 'UNIV-EN', 'UNIV-HN', 'UNIV-SC', 'UNIV-SW']

        # Returns ResultSet containing all department 'a' containers and their own catalog links
        departments = setup_department_catalogs()

        # Returns list of dicts containing department initials and names
        all_departments = get_departments_list(departments)

        all_courses = [] # Final list of dicts that will contain all offered courses
        course_counter = 0 # Index for keeping track of which department has a number of courses

        # Fetching all courses in each department ~~~
        for dept in all_departments:
            asl_flag = False # Explicit flag used since HTML of entire department page is different from the rest
            num_of_courses = 0

            print(f"Processing {dept['name']} page...")

            department_page, uppercase_depts = get_department_page(dept['id'], uppercase_depts)

            courses, asl_flag = get_departments_course_catalog(department_page, dept['id'], asl_flag)
            
            # Extracting all course data
            for c in courses:
                num_of_courses += 1
                tccn_id = ""

                # NOTE: can find by class name here as well, but description text is wrapped in a 'strong' tag.
                # There's only 1 'strong' tag per course block, so find by 'strong' instead to cut down on a
                # few lines of code.
                header_block = c.find('strong')

                # Originally gave '\xa0' instead of ' '
                header = unicodedata.normalize("NFKD", str(header_block.string))

                # Separating the course ID (and TCCN ID, if there is one) from the rest of the header
                # '.'s act as delimiters
                header_info = header.split('.', maxsplit=1)
                department_model_id = header_info[0].split(' ')[0]
                course_num = int(header_info[0].split(' ')[1])
                
                header_info = header_info[1].rsplit('.', maxsplit=2)
                num_of_hours = int(header_info[1].strip().split(' ')[0])

                name = header_info[0].strip()

                if header_info[2]:
                    tccn_id = get_course_tccn_id(header_info[2])
                
                # NOTE: Course descriptions are in a <p> inside of c, but ASL doesn't have the same <p> description format. For ease
                # of processing both in the same function, just send the whole c instead of c.find('p', class_='courseblockdesc').
                description = get_course_description(c, asl_flag)
                prerequisites = get_course_prerequisites(description)

                # Removing redundant "Prerequisite" section from description
                if description:
                    description = description.split("Prerequisite")[0].rstrip()

                # Add course to catalog
                all_courses.append({                                        # Example:
                    'id': department_model_id + str(course_num),            # "CSE1325"
                    'course_num': course_num,                               # 1325
                    'name': name,                                           # "OBJECT-ORIENTED PROGRAMMING"
                    'description': description,                             # "Object-oriented concepts, ...""
                    'num_of_hours': num_of_hours,                           # 3
                    'prerequisites': prerequisites,                         # "CSE 1320"
                    'tccn_id': tccn_id,                                     # ''
                    'department_model_id': department_model_id              # "CSE"
                })
            
            # Add number of courses to department JSON
            all_departments[course_counter].update({'num_of_courses': num_of_courses})
            course_counter = course_counter + 1

            print(f"Adding {dept} to department list.\n")

        departments_json = {'departments': all_departments}
        departments_json_string = json.dumps(departments_json, indent=4)
        with open('departments.json', 'w') as outfile:
            outfile.write(departments_json_string)

        courses_json = {'courses': all_courses}
        courses_json_string = json.dumps(courses_json, indent=4)
        with open('courses.json', 'w') as outfile:
            outfile.write(courses_json_string)
    except Exception as e:
        print(e)
        raise SystemExit("Some error occurred in main().")