# Setup procedure

 - install python3.5 or 3.6
 - create a virtual environment

    cd /path/to/rhythmic_grouping
    python -m venv venv
    source venv/bin/activate

Now you're in an isolated python environment. Now install the dependencies

    pip install -r requirements.txt

Before we run the webapp we need to create a directory of our samples and initialize our database

    cd interface/interface/static/
    mkdir samples

You can put all the samples you want people to get in there. However, they won't actually be presented to users until we register them in our database.
First, go the the `rhythmic_grouping/interface` folder. 

  export FLASK_APP=interface/interface.py
  flask initdb 

Read the warning message, understand you want to proceed anyways, and do so.

You can now run the webapp with

    flask run
