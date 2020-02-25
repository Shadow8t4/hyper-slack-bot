# Pull Python 3.8.1 on alpine
FROM python:3.8.1-alpine

# Set the end work directory to root
# NOTE: Want to not be root user for security
WORKDIR /

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

# Copy the necessary API keys to the container's filesystem
# NOTE: May want to remove this for security reasons...
COPY .api_token_admin_dev .api_token_admin_dev
COPY .api_token_dev .api_token_dev

# All of these directories don't need to and shouldn't be copied
# This should be handled with a mount instead.
COPY assets assets
COPY lib lib

# Copy the Pipfile, it shouldn't change unless during development
COPY Pipfile Pipfile

# Install the necessary Python environment packages
RUN pip install pipenv
RUN pipenv install Pipfile

# Copy the slackbot script, shouldn't change unless during development
COPY slackbot.py slackbot.py

# This should also later be handled with a mount
COPY slackbot_config.json slackbot_config.json
