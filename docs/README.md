# Docs Home

This is the main page of the documentation for the webservice. 

## Configure dev environment

Create a virutal environment for your python instance. The easiet way to do this is to change directories into wherever you have downloaded this repo and use.

```
python3 -m venv ./env
```

This will create a virutal environment in folder env.

### Activate virtual environment on Windows

In powershell type in

```
env/Scripts/activate
```

### Activate virtual environment on Linux and MacOS

In a terminal instance type

```
source ./env/bin/activate
```

### Install necessary dependencies

Once you've activated your virtual python environment you'll have to make sure that you have all of the required packages installed. To do this run the following command

```
pip install -r ./requirements.txt
```

This command will download all necessary dependencies for this project.

### Start the development server

Django is conviently equiped with an HTTP server for local testing purposes. This will be immensely helpful when it comes to testing slight changes and working out bugs. In order to start the HTTP remember that you must have your virutal environment intialized and you must also have the dependencies from the requirements.txt installed.

1. Switch directories into the webservice folder.
1. Execute the command ```python manage.py runserver 8000```

This will start a local http server listening on port 8000. For more detailed information please see the [official documentation](https://docs.djangoproject.com/en/3.1/intro/tutorial01/)

For information on the models used by the django webservice please see [models](./django/models.md)

set up database: python manage.py makemigrations distclassifier