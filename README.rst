Telephone
=========

Telephone is a Django web app that implements the childhood game "telephone"
<http://en.wikipedia.org/wiki/Chinese_whispers>. It is a product of the Lupyan
Lab <http://sapir.psych.wisc.edu>, a research lab in the psychology department
at the University of Wisconsin-Madison. We are using it to simulate the
iterative process of evolution in order to test theories about how human
language evolved and continues to change.

Running the app locally using the Django test server
-------

1. Clone the repository.

    .. code::

        git clone http://github.com/lupyanlab/telephone.git

2. Install the required packages.

    Best practice dictates installing the python packages used for this project
    in a virtualenv. First make a directory to hold the virtualenv.

    .. code::

        mkdir ~/.venvs
        virtualenv --python=python2.7 ~/.venvs/telephone

    Then activate the virtualenv and install the required packages.

    .. code::

        source ~/.venvs/telephone/bin/activate
        pip install -r requirements.txt

    You will also need `jspm <http://jspm.io/>` for package management. First you'll need
    to install node and npm <nodejs.org>, then install jspm.

    .. code::

        nom install jspm --save-dev

    To install packages, managed by jspm, run:

    .. code::

        jspm install

    To install package under jspm control, just run:

    .. code::

        jspm install <package_name>

3. Run the django test server.

    .. code::

        python manage.py runserver
