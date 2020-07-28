## Usage
First, start up a virtual environment in the terminal when you're in the directory of the project.
```
$ python -m venv venv
$ venv\Scripts\activate
```
Now, install the dependencies:
```
pip install requirements.txt
```

Starting up the database and the app:
```
$ flask db init
$ flask db migrate
$ flask db upgrade
$ flask run
```
