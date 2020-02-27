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
                       postgresql-dev \
                       msttcorefonts-installer \
                       fontconfig

# Update the fonts cache
RUN update-ms-fonts && \
    fc-cache -f && \
    rm -rf /var/cache/*

# Create a new user to run as and set the working directory
ENV USER=slackbot
ENV UID=991
ENV GID=991

RUN addgroup -g "${GID}" slackbot
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/slackbot" \
    --ingroup "${USER}" \
    --uid "${UID}" \
    "${USER}"

USER slackbot
WORKDIR /home/slackbot/
ENV PATH="${PATH}:/home/slackbot/.local/bin"

# Copy the Pipfile, it shouldn't change unless during development
COPY Pipfile Pipfile

# Install the necessary Python environment packages
RUN pip install pipenv
RUN pipenv install Pipfile

# Copy the slackbot script, shouldn't change unless during development
COPY slackbot.py slackbot.py

# This should also later be handled with a mount
COPY slackbot_config.json slackbot_config.json

# Makes it easier to run the container, especially when running individually
ENTRYPOINT [ "pipenv", "run", "python", "slackbot.py" ]