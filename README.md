Setup project environment with virtualenv and pip.
For Ubuntu
$ virtualenv envOne
$ source envOne/bin/activate


For windows
$ python3 -m venv envOne (https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
$ envOne\Script\activate

For All
$ pip install -r req.txt
$ cd datascraping/
$ python manage.py migrate
$ python manage.py runserver