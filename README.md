# swapdrop.v2.backend
Django REST API backend for swapdrop 2.0

# Installation

1. Clone the repo: </br> `git clone https://github.com/lukasmyth96/swapdrop.v2.backend.git`
2. Ensure you have python 3 installed 
3. Navigate into root directory of project and create a virtual python environment: </br> `python3 -m venv venv` </br>
(the first venv is the name of the command - the second venv is the name of the folder it will create.)
4. In terminal activate your virtual environment by running: </br> `source venv/bin/activate` </br>
Note- this is command for linux - will differ for other OS. </br>
5. Install the project requirements: </br>
    `pip install -r requirements.txt`
6. Run the Django migration process: </br>
    `python manage.py migrate` </br>
    This will create a file called db.sqlite3 in the root directory. <br>
    This file works as our database during development. </br>
    **Do NOT commit this file ever! - It doesn't play nicely with git**

# Development Guidelines

1. Never commit the db.sqlite3 database file
2. Never delete django migration files!
3. Always branch off develop for new work 
4. Once a chunk of new work is complete - open a pull request (PR) into develop
5. Don't try and push new code directly to develop, staging or master branches - you won't be able to!
6. Try to keep Pull Requests as small and frequent as possible - It's a pain to review massive PRs
7. Whenever you pip install a new package make sure you add it to the requirements.txt file. Specify the exact version number in there too. 
