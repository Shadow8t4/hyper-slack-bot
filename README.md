# Hyper Slack Bot

A Slack bot written in Python to do a few various things.

## Setup

These are the requirements and steps for setup if you plan to install and run the bot on bare metal.

### Requirements

- Postgres
- Python (Native 3.X, Pyenv)

Currently, the bot requires a Postgres Database and some version of Python 3 Testing has actively been done on 3.6+, so using anything older is a risk.

### Prerequisites

On Debian-based distrobutions, you should be able to use the following to command to install prerequisites.

```
sudo apt install -y postgresql-common python3 python3-dev python3-pip gcc libgc-dev tk-dev tcl-dev
```

### Postgres Setup

Once you have postgres installed, you will need to create a new role and database.

```
CREATE ROLE "slackbot" WITH LOGIN;
\password slackbot
CREATE DATABASE "slackbot_prod" WITH OWNER "slackbot";
```

### Python Setup

It's recommended that you use `pipenv` to install the packages required.

`pipenv install Pipfile`

Otherwise, you can manually install the packges laid out in the `Pipfile`.

### Docker Compose

Alternatively, you can install and run the bot using Docker.

Check the docker-compose.yml to ensure that you have all of the directories that are referenced in the `volumes:` sections.

```
mkdir .keys pg_data
chmod -R a+w output logs pg_data
echo 'sample_password' >> .keys/.pgdb_pass
```

Additionally, you should ensure you have gone through the following configuration steps. Make sure that whatever password you put in `.keys/.pgdb_pass` is also in your `slackbot_config.json`.

Otherwise, `docker-compose up --build -d` should build and run the service.

### Config

Before attempting to run the bot, you will need to copy the `template_slackbot_config.json` file and rename it to `slackbot_config.json`.

`cp template_slackbot_config.json slackbot_config.json`

Here is a basic description of each key-value pair:
- emoji_sub: When substituting a message with an emoji, choose what emoji is set in place
- db_user: Postgres DB User
- db_name: Postgres DB Name
- db_host: Postgres DB Hostname
- db_port: Postgres DB Port
- db_password: Postgres DB User Password
- word_chars: Set of letter categories to grab words from in the word table
- phrase_re: Regular Expression for what messages to respond to with words from the word table
- emoji_re: Reguard Expression for what words to replace with emoji_sub
- fontpath: Path to a .ttf font file in the system
- functions_status: Set the status of which functions are enabled by default

### Slack API Keys

You will need an API token from Slack, you can learn that and more on how to set up a bot from this documentation: https://github.com/slackapi/python-slackclient/blob/master/tutorial/01-creating-the-slack-app.md

You'll need both tokens for the bot to work properly, name them: `.api_token_prod` and `.api_token_admin_prod` for your bot user oauth token and admin oauth token respectively, and move them to the `.keys/` directory. If you haven't already created that subdirectory, do so now.

## Usage

Once you have set up and installed your app/bot, you can run it by typing:

`python slackbot.py prod`

The bot should automatically put itself in the background, and can be killed by sending it the message: `!shutdown`.

## Updating

You should be able to update the bot with `git pull` on the master branch.

Additionally, you can use `!update` to have to bot update itself, but this isn't recommended as the bot is currently still in active in development. New requirements will likely break the bot when trying to run this.

## Features

### Phrase Triggers

The bot can be set up to trigger a response whenever certain phrases are said.

You currently must provide the bot with a trigger phrase and a database of words to pull from as a response, the phrase is regex compatible.

As a response, it will randomly select words from the database provided.

### Bingo Functionality

Make a post in the chat that says `bingo` and the bot will respond with a randomly generated bingo board from a list of provided phrases.

### Emoji Injection

Any post in the chat with a provided regex-compatible set of characters in it will be deleted and echoed in a formated response with a desired emoji in its place.

### Disable/Enable Functions

You can tell the bot to disable/enable certain functions. This can be handy if there are only certain functions you want available to users out of this bot, since there is no active form of user permission management at the time.

`!disable [phrase|emoji|bingo]` will disable the given function

`!enable [phrase|emoji|bingo]` will enable it

All functions are enabled by default, and the bot will not let you enable or disable functions that are already enabled/disabled respectively.

### ReadOnly Channels

You can set the bot up to delete all messages that aren't from itself in a specified channel.

`!readonly [channel]` will add a channel to the bot's list of read only channels

`!readonly remove [channel]` will allow messages to be sent in that channel again

`!readonly list` should list all channels visible by the bot and their readonly status

### Announcements

You can tell the bot to send messages to a channel, this is intended to be a way to announce things into channels that are "readonly".

`!announce [channel] [message]`

## Troubleshooting

Logs, while somewhat vague at times, are sent to the `logs/` directory when you run the bot. It will create the directory and the files, and add to them each time a message is sent. A new log file is created each day.

If you have any questions or need help with setup, feel free to contact me:
- email: adh9694@gmail.com
- discord: @shadow8t4#8276
- matrix: @shadow8t4:matrix.werefox.dev