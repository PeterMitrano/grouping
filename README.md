# Setup procedure

 - install python3.5 or 3.6
 - create a virtual environment

    cd /path/to/rhythmic_grouping
    python -m venv venv
    source interface/venv/bin/activate

Now you're in an isolated python environment. Now install the dependencies

    pip install -r requirements.txt

Before we run the webapp we need to list which samples we want in our database. Open the following file in a text editor:

    interface/interface/static/samples/index.txt

You can pick any file that's in the directory https://users.wpi.edu/~mprlab/grouping/data/samples

  export FLASK_APP=interface/interface.py
  flask initdb

Read the warning message, understand you want to proceed anyways, and do so.

You can now run the webapp with

    flask run
