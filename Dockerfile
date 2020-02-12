FROM python:3.8.1-alpine
WORKDIR /
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
COPY .api_token_admin_dev .api_token_admin_dev
COPY .api_token_dev .api_token_dev
COPY assets assets
COPY lib lib
COPY Pipfile Pipfile
RUN pip install pipenv
RUN pipenv install Pipfile
COPY slackbot.py slackbot.py
COPY slackbot_config.json slackbot_config.json
