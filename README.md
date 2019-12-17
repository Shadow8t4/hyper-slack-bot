# Hyper Slack Bot

A Slack bot written in Python to do a few various things.

## Usage

Clone this repo, then make sure you have the modules listed in `Pipfile` in your python environment.

If you have [pyenv](https://github.com/pyenv/pyenv) installed, you can install the proper Python environment needed by executing:

`pyenv install 3.7.4`

`pyenv local 3.7.4`

`pyenv exec pip install pipenv`

If you have [pipenv](https://pypi.org/project/pipenv) installed, you can setup the Python environment using:

`pipenv install Pipfile`

or `pyenv exec pipenv install Pipfile` if you're using pyenv.

You will need an API token from Slack, you can learn that and more on how to set up a bot from this documentation: https://github.com/slackapi/python-slackclient/blob/master/tutorial/01-creating-the-slack-app.md

You'll need both tokens for the bot to work properly, name them: `.api_token_prod` and `.api_token_admin_prod` for your bot user oauth token and admin oauth token respectively.

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
