# Swisstour Standings

## Overview
Swisstour Standings is a Python project designed to populate the backend model of the Swiss Disc Golf Tour standings. It scrapes tournament data, calculates the results, and stores the standings in a database. The results can be displayed using any desired front-end view. 

## Files
- **dbconn.py**: Handles the connection to the database, so that it can easily be switched between development and production. 
- **dbinteract.py**: Controller that handles all the interactions with the database.
- **dbobjects.py**: Contains the sqlalchemy model definitions for the database structure.
- **dbscrape.py**: Contains the functions and helpers that are used to scrape the data from the pdga website.
- **main.py**: File that is executed in order to run everything, including the scraping, calculations and creation of the database standing tables.
- **swisstour_standings.png**: Visual representation of the database structure.

## Versioning
There is a branch for the working code used for each year. For example the code used to calculate the 2024 standings is located on a branch which will never be merged to main. Main is reserved for the development of the code for the current year.

## Installation
### Python Version & Dependencies
If using pyenv, run:
```bash
pyenv install
```
Otherwise to guarantee compatibility manually install the version of python specified by the .python-version file.

Create a virtual environment:
```bash
python -m venv .venv
```

To install the required dependencies, run:
```bash
pip install -r requirements.txt
```
### Environment File
In order to interact with the production database an environment file (.env) in the root directory with the following variables needs to be defined:
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_NAME
