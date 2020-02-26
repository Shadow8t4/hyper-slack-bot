# Pull Python 3.8.1 on alpine
FROM python:3.8.1-alpine

# Install the necessary prerequisites for the bot
RUN apk --no-cache add jpeg-dev \
                       zlib-dev \
                       freetype-dev \
                       lcms2-dev \
                       openjpeg-dev \
                       tiff-dev \
                       tk-dev \
                       tcl-dev \
                       harfbuzz-dev \
                       fribidi-dev \
                       gcc \
                       musl-dev \
                       python3-dev \
                       postgresql-dev

# Set the end work directory to root
# NOTE: Want to not be root user for security
WORKDIR /

# Copy the Pipfile, it shouldn't change unless during development
COPY Pipfile Pipfile

# Install the necessary Python environment packages
RUN pip install pipenv
RUN pipenv install Pipfile

# Copy the slackbot script, shouldn't change unless during development
COPY slackbot.py slackbot.py

# This should also later be handled with a mount
COPY slackbot_config.json slackbot_config.json
