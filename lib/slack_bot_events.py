from lib.import_db import import_words, import_bingo
from lib.gen_bingo import gen_bingo
from lib.manage_readonly import import_readonly, export_readonly
from random import randrange as rr
from datetime import datetime
from subprocess import check_output, call
from io import BytesIO
from time import sleep
from psycopg2 import connect
import slack
import json
import os
import re


def first_time_setup():
    return


def disable_function(client, data, functions_status):
    """Disable a specified functionality temporarily

    Arguments:
        client {object} -- Non-admin level client to send messages as (bot)
        data {dict} -- Data dictionary containing slack message information
        functions_status {dict} -- A dictionary containing the enabled/disabled status of each functionality

    Returns:
        [dict] -- The updated function status disctionary
    """

    function = data['text'].split(' ')[1]
    try:
        if(functions_status[function] == False):
            client.chat_postMessage(
                channel=data['channel'],
                text='{0} is already disabled.'.format(
                    data['text'].split(' ')[1])
            )
        else:
            functions_status[function] = False
            client.chat_postMessage(
                channel=data['channel'],
                text='{0} functionality disabled.'.format(
                    data['text'].split(' ')[1])
            )
    except:
        client.chat_postMessage(
            channel=data['channel'],
            text='{0} isn\'t a function I can disable.'.format(
                data['text'].split(' ')[1])
        )


def enable_function(client, data, functions_status):
    """Enable a previously disabled functionality

    Arguments:
        client {object} -- Non-admin level client to send messages as (bot)
        data {dict} -- Data dictionary containing slack message information
        functions_status {dict} -- A dictionary containing the enabled/disabled status of each functionality

    Returns:
        [dict] -- The updated function status disctionary
    """

    function = data['text'].split(' ')[1]
    try:
        if(functions_status[function] == True):
            client.chat_postMessage(
                channel=data['channel'],
                text='{0} is already enabled.'.format(
                    data['text'].split(' ')[1])
            )
        else:
            functions_status[function] = True
            client.chat_postMessage(
                channel=data['channel'],
                text='{0} functionality enabled.'.format(
                    data['text'].split(' ')[1])
            )
    except:
        client.chat_postMessage(
            channel=data['channel'],
            text='{0} isn\'t a function I can enable.'.format(
                data['text'].split(' ')[1])
        )


def announce(client, data_text, data_channel):
    """Post announcement messages as the UP Hype Bot to specified channel

    Arguments:
        client {obj} -- Non-admin level client to send messages as (bot)
        data_text {str} -- Incoming message text
        data_channel {str} -- Channel message was received in
    """

    if(len(data_text.split()) < 3):
        client.chat_postMessage(
            channel=data_channel,
            text='Invalid command.\nUsage: !announce [channel] [message]'
        )
    else:
        channel_list_remote = client.conversations_list(
            exclude_archived='true', types='public_channel, private_channel, im')['channels']

        channel = data_text.split()[1]
        announcement = ' '.join(data_text.split(' ')[2:])

        if any((c['id'] == data_channel and not c['is_im']) for c in channel_list_remote):
            client.chat_postMessage(
                channel=channel,
                text='Please use that command in an IM with the bot.'
            )
            return

        in_channel = False
        for c in channel_list_remote:
            if(not c['is_im'] and not c['is_archived']):
                if(channel == c['name']):
                    in_channel = True
                    client.chat_postMessage(
                        channel=channel,
                        text=announcement
                    )

        if(not in_channel):
            client.chat_postMessage(
                channel=data_channel,
                text='Bot not in that channel, or invalid channel.'
            )


def delete_readonly(api_token, data_text, data_channel, data_ts):
    """Delete messages from "Read Only" specified channels.

    Arguments:
        api_token {str} -- An Admin permission level API token so we can delete messages
        data_text {str} -- Incoming message text
        data_channel {str} -- Channel message was received in
        data_ts {str} -- Timestamp of message received

    Returns:
        str -- Function returns deleted message text
    """

    output = ''
    try:
        client = slack.WebClient(api_token)
        client.chat_delete(
            channel=data_channel,
            ts=data_ts
        )

        output = 'Deleted message: \"{0}\" from channel: {1}'.format(
            data_text, data_channel)
    except Exception as e:
        output = 'I encountered an error trying to delete a message... {0}'.format(
            e)
    return output


def list_readonly(client, data_channel):
    """List current status of channels as readonly or not

    Arguments:
        client {object} -- Non-admin level client to send messages as (bot)
        data_channel {str} -- Channel message was received in

    Returns:
        arr -- List of channels determined to be read only
    """

    channel_list_local = import_readonly()
    channel_list_remote = client.conversations_list(
        exclude_archived='true', types='public_channel, private_channel, im')['channels']

    channel_list_formatted = 'List of readonly channels (bold means I am in the channel, italics means it\'s a private channel):\n\n'

    for c in channel_list_remote:
        readonly = False
        for l in channel_list_local:
            if(l == c['id']):
                readonly = True

        if(not c['is_im'] and not c['is_archived']):
            if(c['is_private']):
                channel_list_formatted += '- _#{0}: {1}_\n'.format(
                    c['name'], readonly)
            elif(c['is_member']):
                channel_list_formatted += '- *#{0}: {1}*\n'.format(
                    c['name'], readonly)
            else:
                channel_list_formatted += '- #{0}: {1}\n'.format(
                    c['name'], readonly)

    client.chat_postMessage(
        channel=data_channel,
        text=channel_list_formatted
    )

    return channel_list_local


def make_readonly(client, data_channel, data_text):
    """Add a channel to the list of readonly channels

    Arguments:
        client {object} -- Non-admin level client to send messages as (bot)
        data_channel {str} -- Channel message was received in
        data_text {str} -- Messsage text received, cut to only the channel name

    Returns:
        arr -- List of channels determined to be read only
    """

    channel_list_local = import_readonly()
    channel_list_remote = client.conversations_list()['channels']
    readonly_channels = channel_list_local

    for c in channel_list_remote:
        if(c['name'] == data_text):
            if(not c['is_member']):
                client.chat_postMessage(
                    channel=data_channel,
                    text='*Note:* It doesn\'t look like I\'ve been added to this channel. I can\'t enforce read only.'
                )

            if(c['id'] in channel_list_local):
                client.chat_postMessage(
                    channel=data_channel,
                    text='{0} is already a readonly channel.'.format(data_text)
                )
                return readonly_channels
            readonly_channels.append(c['id'])
            client.chat_postMessage(
                channel=data_channel,
                text='{0} added to readonly channels list.'.format(data_text)
            )
            export_readonly(readonly_channels)
            return readonly_channels

    client.chat_postMessage(
        channel=data_channel,
        text='Could not add {0} to readonly channels list. Check spelling?'.format(
            data_text)
    )

    return readonly_channels


def remove_readonly(client, data_channel, data_text):
    """Remove a channel from the readonly channels list

    Arguments:
        client {object} -- Non-admin level client to send messages as (bot)
        data_channel {str} -- Channel message was received in
        data_text {str} -- Message text received, cut to only the channel name

    Returns:
        arr -- List of channels determined to be read only
    """

    channel_list_local = import_readonly()
    channel_list_remote = client.conversations_list()['channels']
    readonly_channels = channel_list_local

    for c in channel_list_remote:
        if(c['name'] == data_text):
            if(not c['is_member']):
                client.chat_postMessage(
                    channel=data_channel,
                    text='*Note:* It doesn\'t look like I\'ve been added to this channel. I can\'t enforce read only.'
                )

            if(c['id'] not in channel_list_local):
                client.chat_postMessage(
                    channel=data_channel,
                    text='{0} is not a readonly channel.'.format(data_text)
                )
                return readonly_channels

            readonly_channels.remove(c['id'])
            client.chat_postMessage(
                channel=data_channel,
                text='{0} removed from readonly channels list.'.format(
                    data_text)
            )
            export_readonly(readonly_channels)
            return readonly_channels

    client.chat_postMessage(
        channel=data_channel,
        text='could not remove {0} from readonly channels list. Check spelling?'.format(
            data_text)
    )

    return readonly_channels


def delete_replaced_message(api_token, data_text, data_channel, data_ts, re_string, replacement):
    """Delete the message we want to replace

    Arguments:
        api_token {str} -- An Admin permission level API token so we can delete messages
        data_text {str} -- Incoming message text
        data_channel {str} -- Channel message was received in
        data_ts {str} -- Timestamp of message received
        re_string {str} -- Regex to use when searching message for replacements
        replacement {str} -- String to replace matches with

    Returns:
        str -- Function returns output replaceplacement text
    """

    output = ''
    try:
        client = slack.WebClient(api_token)
        client.chat_delete(
            channel=data_channel,
            ts=data_ts
        )

        output = re.sub(re_string, replacement, data_text)
    except Exception as e:
        output = 'I encountered an error trying to replace a message... {0}'.format(
            e)
    return output


def format_replaced_message(api_token, client, data_text_filtered, filtered_data, data, up_re, replacement):
    """Process replacement of regex matches and send replacement message

    Arguments:
        api_token {str} -- Admin permission level API token to pass to delete_replaced_message
        client {object} -- Non-admin level client to send messages as (bot)
        data_text_filtered {arr} -- Incoming message text, filtered to avoid replacing "important" text
        filtered_data {arr} -- The data that was filtered out as "important"
        data {dict} -- Data dictionary containing slack message information
        up_re {str} -- Regex to use when searching message for replacements
        replacement {str} -- String to replace matches with
    """

    if(len(data_text_filtered) > 0):
        data_text_filtered_replaced = delete_replaced_message(
            api_token, ' '.join(data_text_filtered), data['channel'], data['ts'], up_re, replacement)
    else:
        data_text_filtered_replaced = delete_replaced_message(
            api_token, data['text'], data['channel'], data['ts'], up_re, replacement)

    data_text_replaced = []
    for w in data_text_filtered_replaced.split(' '):
        if(re.search(r'\(replaceme\_[0-9]\)', w)):
            data_text_replaced.append(filtered_data[int(w[11])])
        else:
            data_text_replaced.append(w)

    user = data['user']
    client.chat_postMessage(
        channel=data['channel'],
        text=f'<@{user}>' +
        ': {0}'.format(' '.join(data_text_replaced))
    )


def trigger_response(client, data, re_match, chars, dbname='slackbot_db', user='slackbot', port=5432, password='testing', host='localhost'):
    """Respond to new messages that match a pattern with two random words starting with specified chars

    Arguments:
        client {object} -- Non-admin level client to send messages as (bot)
        data {dict} -- Data dictionary containing slack message information
        re_match {str} -- Matches confirmed using the regex search

    Keyword Arguments:
        dbname {str} -- [Database name to pull from] (default: {'slackbot_db'})
        user {str} -- [User to enter database as] (default: {'slackbot'})
    """

    match_formatted = ' '.join(
        [m.capitalize() for m in re_match.groups()[0].split()])
    if(match_formatted.upper() == chars.upper()):
        match_formatted = match_formatted.upper()

    con = connect("dbname={0} user={1} port={2} password={3} host={4}".format(dbname, user, port, password, host))
    cur = con.cursor()

    response_words_counts = []
    for c in chars:
        cur.execute(
            "SELECT COUNT(word) FROM words WHERE letter='{0}';".format(c))
        response_words_counts.append(cur.fetchone()[0])

    response_words = []
    index = 0
    while index < len(chars):
        cur.execute("SELECT word FROM words WHERE id={0} AND letter='{1}';".format(
            rr(response_words_counts[index]), chars[index]))
        response_words.append(cur.fetchone()[0].strip().capitalize())
        index += 1

    client.chat_postMessage(
        channel=data['channel'],
        text='{0}, also known as: {1}'.format(
            match_formatted,
            ' '.join(response_words))
    )
    con.close()


def bingo(client, data, dbname='slackbot_db', user='slackbot', port=5432, password='testing', host='localhost', font='/usr/share/fonts/truetype/msttcorefonts/arial.ttf'):
    """Generate a bingo board from a phrase database and respond with it

    Arguments:
        client {object} -- Non-admin level client to send messages as (bot)
        data {dict} -- Data dictionary containing slack message information
    """

    bingo_generated = gen_bingo(
        dbname,
        user,
        port,
        password,
        host,
        'bingo_board',
        640,
        480,
        (13, 89, 221),
        (24, 24, 24),
        (204, 216, 255),
        font
    )

    if(bingo_generated):
        try:
            client.files_upload(
                channels=data['channel'],
                file='output/bingo_board.png',
                filename='bingo_board.png'
            )
        except:
            client.chat_postMessage(
                channel=data['channel'],
                text='I failed to send a bingo board...'
            )
    else:
        client.chat_postMessage(
            channel=data['channel'],
            text='I failed to generate a bingo board, check the logs.'
        )


def attempt_update(env, client, channel):
    """Attempt to perform a code update, restarting the bot.

    Arguments:
        env {str} -- Runtime environment of bot
        client {object} -- Non-admin level client to send messages as (bot)
        channel {str} -- Channel to send output information to
    """

    output = check_output('git pull'.split())
    client.chat_postMessage(
        channel=channel,
        text=output.decode('UTF-8') + '\nShutting down old bot...'
    )
    sleep(1)
    client.chat_postMessage(
        channel=channel,
        text='!shutdown'
    )
    sleep(5)
    command = 'pyenv exec pipenv run python slackbot.py {0}'.format(
        env).lower()
    call(command.split())
    exit(0)
