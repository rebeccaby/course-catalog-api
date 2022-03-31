# UTA Course Catalog Scraper and REST API
The UTA Course Catalog REST API catalogs all course information on classes offered by all colleges at the University of Texas at Arlington. Information is scraped from the university catalog page.

## Installation
Download the ZIP of or clone this repository:
```bash
$ git clone https://github.com/rebeccaby/course-catalog-api.git
$ cd course-catalog-api
```

## Usage
Run 'uta_scraper.py', which will scrape the university catalog and store the extracted data into 'courses.json' and 'departments.json'.
```bash
$ python3 uta_scraper.py
```

Run 'req_script.py' to populate the database via the REST API.
```bash
$ python3 req.script.py
```

'uta_scraper.py' and 'req_script.py' only need to be run once, or after UTA adds new departments and/or courses to their catalog.

Requests can be made locally with 'curl':
```bash
$ curl http://127.0.0.1:5000/course/cse1325
```

Output:
```json
example
```