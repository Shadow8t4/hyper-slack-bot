#!/usr/bin/python
from lib.bot_logging import log_output
from lib.import_db import import_bingo, import_words
from lib.manage_readonly import import_readonly
from lib.import_config import Config
import lib.slack_bot_events as sbe
import slack
from os import environ, fork, mkdir
from os.path import exists
from sys import argv
from datetime import datetime
from re import search


""" Initialize Global Variables """
config = Config()


def parse_args():
    """Initial logic to determine if user even input arguments

    Returns:
        input_dict -- Dictionary of environment and test number if applicable
    """

    if(len(argv) > 1):
        arg_env = argv[1].lower()
        if(arg_env.lower() == 'test'):
            if(len(argv) > 2):
                arg_num = argv[2].lower()
                return parse_input(arg_env, arg_num)
        return parse_input(arg_env)
    return parse_input()


def parse_input(env='', num=''):
    """Parse the arguments and grab new input if necessary.

    Keyword Arguments:
        env {str} -- Run environment to use. (default: {''})
        num {str} -- Test number if environment is test. (default: {''})

    Returns:
        input_dict -- Dictionary of environment and test number if applicable
    """
    input_dict = {
        'env': '',
        'num': ''
    }

    if(env):
        if(env == 'test'):
            input_dict['env'] = env
            if(num):
                try:
                    input_dict['num'] = int(num)
                except:
                    print('Invalid test number.')
                    exit(1)
            else:
                print('Please input a test number:')
                try:
                    input_dict['num'] = int(input())
                except:
                    print('Invalid test number.')
                    exit(1)
        elif(env == 'dev'):
            input_dict['env'] = 'dev'
        elif(env == 'prod'):
            input_dict['env'] = 'prod'
        else:
            print('Invalid run environment.')
            exit(1)
    else:
        print('Please input a run environment')
        input_env = str(input())
        return parse_input(input_env)

    return input_dict


@slack.RTMClient.run_on(event='hello')
def say_hello(**payload):
    """Process bot events that happen upon startup and connection to server
    """

    print('Hype Bot restarted.')


@slack.RTMClient.run_on(event='message')
def trigger_event(**payload):
    """Process bot events based on whenever a message is sent to the chat
    """

    output = '{0}\t{1}\n'.format(datetime.now(), payload['data'])
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    readonly_channels = import_readonly()

    try:

        if 'text' in data and 'user' in data:
            if(data['channel'] in readonly_channels):
                bot_user_id = web_client.auth_test()['user_id']
                if not (bot_user_id is data['user']):
                    output = sbe.delete_readonly(
                        environ['SLACK_API_TOKEN_ADMIN'], data['text'], data['channel'], data['ts'])
            else:

                if(data['text'] == '!update'):
                    log_output(environ['SLACK_BOT_ENV'],
                               '\t***** Shutdown for update *****\n')
                    web_client.chat_postMessage(
                        channel=data['channel'],
                        text='Checking for updates....'
                    )
                    sbe.attempt_update(environ['SLACK_BOT_ENV'],
                                       web_client, data['channel'])
                    return

                if(data['text'] == '!shutdown'):
                    rtm_client.stop()
                    return

                phrase_match = search(config.phrase_re, data['text'].lower())

                # Remove exceptions from text before matching for emoji injection
                filtered_data = []
                data_text = data['text'].split(' ')
                data_text_filtered = []
                for w in data_text:
                    if ((len(w) > 0) and '!' == w[0]) or ('http' in w) or (((len(w) > 1) and '#' == w[1]) or ((len(w) > 0) and '#' == w[0])):
                        data_text_filtered.append(
                            '(replaceme_{0})'.format(str(len(filtered_data))))
                        filtered_data.append(w)
                    else:
                        data_text_filtered.append(w)
                emoji_match = search(
                    config.emoji_re, ' '.join(data_text_filtered))

                if(data['text'].split(' ')[0] == '!announce'):
                    sbe.announce(web_client, data['text'], data['channel'])

                if(data['text'].split(' ')[0] == '!disable'):
                    sbe.disable_function(
                        web_client, data, config.functions_status)

                if config.functions_status['emoji'] and emoji_match and not 'files' in data:
                    bot_user_id = web_client.auth_test()['user_id']
                    if not (bot_user_id is data['user']):
                        sbe.format_replaced_message(environ['SLACK_API_TOKEN_ADMIN'], web_client,
                                                    data_text_filtered, filtered_data, data, config.emoji_re, config.emoji_sub)

                if config.functions_status['phrase'] and phrase_match:
                    sbe.trigger_response(
                        web_client, data, phrase_match, config.word_chars, dbname=config.db_name, user=config.db_user, port=config.db_port, password=config.db_password, host=config.db_host)

                if config.functions_status['bingo'] and (data['text'].lower() == 'bingo'):
                    sbe.bingo(web_client, data, dbname=config.db_name, user=config.db_user, port=config.db_port, password=config.db_password, host=config.db_host,
                              font=config.fontpath)

                if(data['text'].split(' ')[0] == '!enable'):
                    sbe.enable_function(
                        web_client, data, config.functions_status)

                if(data['text'].split(' ')[0] == '!readonly'):
                    if(len(data['text'].split(' ')) > 0):
                        if(data['text'].split(' ')[1] == 'list'):
                            if(len(data['text'].split(' ')) == 2):
                                readonly_channels = sbe.list_readonly(
                                    web_client, data['channel'])
                            else:
                                web_client.chat_postMessage(
                                    channel=data['channel'],
                                    text='Usage: !readonly [channel] or !readonly list'
                                )
                        elif(data['text'].split(' ')[1] == 'remove'):
                            readonly_channels = sbe.remove_readonly(
                                web_client, data['channel'], data['text'].split(' ')[2])
                        else:
                            readonly_channels = sbe.make_readonly(
                                web_client, data['channel'], data['text'].split(' ')[1])
                    else:
                        web_client.chat_postMessage(
                            channel=data['channel'],
                            text='Usage: !readonly [channel] or !readonly list'
                        )

    except Exception as e:
        output += '{0}\tAn error occurred: {1}\n'.format(datetime.now(), e)

    log_output(environ['SLACK_BOT_ENV'], output)


def main():
    """Ensure there's an output folder for logs, start the bot.
    """
    import_words(dbname=config.db_name, user=config.db_user, port=config.db_port, password=config.db_password, host=config.db_host)
    import_bingo(dbname=config.db_name, user=config.db_user, port=config.db_port, password=config.db_password, host=config.db_host)

    if(not exists('./logs')):
        mkdir('logs')

    log_output(environ['SLACK_BOT_ENV'], '\t***** Started Running *****\n')

    slack_token = environ['SLACK_API_TOKEN']
    rtm_client = slack.RTMClient(token=slack_token)
    rtm_client.start()

    log_output(environ['SLACK_BOT_ENV'], '\t***** Graceful Shutdown *****\n')


if(__name__ == '__main__'):
    """Act as a runner, might move to its own python file.
    """

    input_dict = parse_args()

    if(input_dict['env'] == 'test'):
        if(not exists('./output')):
            mkdir('output')
        # api_token_file = open('.api_token_admin_dev')
        # environ['SLACK_API_TOKEN'] = api_token_file.readline().strip()
        # environ['SLACK_BOT_ENV'] = 'Dev'
        # run_tests(input_dict['num'])
    else:
        if('SLACK_API_TOKEN' in environ):
            pass
        else:
            api_token_admin_file = open(
                '.keys/.api_token_admin_{0}'.format(input_dict['env']))
            api_token_file = open(
                '.keys/.api_token_{0}'.format(input_dict['env']))
            environ['SLACK_API_TOKEN_ADMIN'] = api_token_admin_file.readline().strip()
            environ['SLACK_API_TOKEN'] = api_token_file.readline().strip()
            environ['SLACK_BOT_ENV'] = input_dict['env'].capitalize()
        main()
