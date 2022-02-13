# Use an official Python runtime as a parent image
FROM debian:latest

# Set the working directory to /app
WORKDIR /pyra

COPY . /pyra

# Install any needed packages
RUN apt-get update

# Install any needed packages
#RUN apt-get install --no-install-recommends -y python3 \
#        sqlite3 jq python3-pip python3-setuptools  cargo \
#        python3-wheel gunicorn3

RUN apt-get install --no-install-recommends -y python3 python3-pip gunicorn3
#        sqlite3 jq python3-pip python3-setuptools  cargo \
#        python3-wheel gunicorn3


RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Make port available to the world outside this container
EXPOSE 8080

ENV FLASK_APP=/pyra/pyra.py

# Run flask when the container launches
CMD [ "/pyra/gunicorn-start.sh"]
