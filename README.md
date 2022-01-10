# About


Also can announce new/changes to Rocket.Chat

REST API for automatic management

Very early version but working software.

Author: https://github.com/henrik-andreasson/

Heavily based on the excellent tutorial  [Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by Miguel Grinberg.

Big Thanks to Miguel!

# demo

![animation](docs/pics/pyra.gif)

login with:

    user: admin
    pass: admin

[pyra demo](todo)

# Running

## Running on debian

Install python3 and sqlite

    apt-get install --no-install-recommends -y python3 \
        sqlite3 jq python3-pip python3-setuptools  cargo \
        python3-wheel gunicorn3


Used modules

    pip3 install -U pip
    pip3 install -r requirements.txt

install source

    download pyra from github
    mkdir /opt/pyra
    cd /opt/pyra
    unzip inventorpy-x.y.z.zip

start

    export FLASK_APP=pyra.py
    cd /opt/pyra
    flask run --host=0.0.0.0

See also the systemd service file pyra.service to run with gunicorn

## Running in Docker

build docker:

    docker build -t pyra  .

Run the app

    docker run -p8080:8080 pyra

Developer mode, ie mount the current directory into the docker container and have it self reload when python files are written

    docker run --rm --name pyra -p5000:5000 -it  --mount type=bind,source="$(pwd)",target=/pyra pyra flask run --host=0.0.0.0 --reload

# docs

<https://henrik-andreasson.github.io/pyra/>
