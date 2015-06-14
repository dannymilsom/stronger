# Stronger #

Stronger is a Open Source workout tracking tool for people who enjoy weight training.

Users can record workouts, review progress and share achievements with other members.

## Demo ##

A demo is currently hosted at [dannymilsom.webfactional.com](dannymilsom.webfactional.com). Please note this is a work in progress - any bugs can be reported using [GitHub Issues](https://github.com/dannymilsom/stronger/issues).

## Getting Started ##

Please follow these steps to configure your local devleopment environment.

Clone the repository onto your local machine.

    git clone https://github.com/dannymilsom/stronger.git .

Create a new virtualenv

    virtualenv stronger

Activate your new virtualenv

    source stronger/bin/activate

Install dependencies using the Python package manager

    pip install -r /path/to/requirements.txt

Create the database tables

    python manage.py migrate

Run the development server (this listens on port 8000 by default)

    python manage.py runserver

We also need to activate Grunt - a task runner to watch the LESS files. To install the node dependencies run the following in the repo root.

    npm install

Finally fire up Grunt

    grunt

And you're ready to go!

## Contributions ##

All contributions to improve the platform are welcome. Before pushing code please ensure you've followed the [PEP-8 style guide](https://www.python.org/dev/peps/pep-0008/) and executed the test runner.

    python manage.py test