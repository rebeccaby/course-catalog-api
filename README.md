# UTA Course Catalog Scraper and REST API
The UTA Course Catalog REST API catalogs all course information on classes offered by all colleges at the University of Texas at Arlington. Information is scraped from the university catalog page.

## Installation
Download the ZIP of or clone this repository:
```bash
$ git clone https://github.com/rebeccaby/course-catalog-api.git
$ cd course-catalog-api
```

## Usage
Run `uta_scraper.py`, which will scrape the university catalog and store the extracted data into `courses.json` and `departments.json`.
```bash
$ python3 uta_scraper.py
```

Run both `departments_requests_script.py` and `courses_requests_script.py` to populate the database with all department and course information through the REST API.
```bash
$ python3 departments_requests_script.py
$ python3 courses_requests_script.py
```

`uta_scraper.py`, `departments_requests_script.py`, and `courses_requests_script.py` only need to be run once, or after UTA adds new departments and/or courses to their catalog.

Requests can be made locally (currently) with `curl`. An example of sending a GET request for a specific department:
```bash
$ curl http://127.0.0.1:5000/department/CSE
```
Output:
```yaml
{'id': "CSE", 'name': "Computer Science and Engineering", 'num_of_courses': 190}
```

An example of sending a GET request for a specific course:
```bash
$ curl http://127.0.0.1:5000/course/CSE1325
```
Output:
```yaml
{'id': 'CSE1325', 'course_num': 1325, 'name': 'OBJECT-ORIENTED PROGRAMMING', 'description': 'Object-oriented concepts, class diagrams, collection classes, generics, polymorphism, and reusability.  Projects involve extensive programming and include graphical user interfaces and multithreading.', 'num_of_hours': 3, 'prerequisites': 'CSE 1320', 'tccn_id': '', 'department_model_id': 'CSE'}
```

## Bugs
  * `\u00a0` appearing instead of ` `

## Future Additions
  * Better eexception handling and null checking in scraper
  * Have courses work off "{department}/" endpoints
    * Ex. `http://127.0.0.1:5000/ACCT/2301` instead of `http://127.0.0.1:5000/course/ACCT2301`
  * Asynchronous requests with scraper and PUT scripts
    * grequests
  * Skip a department if one page can't be scraped instead of exiting
  * Create unit tests for API
  * Abstract out the database adapter
  * Add basic security measures
  * Deployment