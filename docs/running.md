# Running

## Running on Debian

Install os packages

    apt-get install --no-install-recommends -y python3 \
            sqlite3 jq python3-pip python3-setuptools  cargo \
            python3-wheel gunicorn3


install source

    mkdir /opt/pyra
    cd /opt/pyra
    unzip pyra-x.y.z.zip

Used modules

    pip3 install -U pip
    pip3 install -r requirements.txt


start

    export FLASK_APP=pyra.py
    cd /opt/pyra
    flask run --host=0.0.0.0

See also the systemd service file inventorpy.service to run with gunicorn

## Running in Docker

build docker:

    docker build -t pyra  .

Run the app interactively

    docker run -it -p8080:8080 pyra

Run the app in background

    docker run --name pyra -p8080:8080 pyra

Developer mode, ie mount the current directory into the docker container and have it self reload when python files are written

    docker run -p5000:5000 -it --rm --mount type=bind,source="$(pwd)",target=/pyra pyra flask run --host=0.0.0.0 --reload
