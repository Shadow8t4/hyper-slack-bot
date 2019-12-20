#!/usr/bin/python
from json import load
from re import compile


class Config:

    def __init__(self):
        # Load from a config json file the necessary parameters
        config_dict = load(open('slackbot_config.json', 'rb'))
        # Emoji to substitute when matching
        self.emoji_sub = config_dict['emoji_sub']
        # Name of database to use
        self.db_name = config_dict['db_name']
        # Database user to read from database as
        self.db_user = config_dict['db_user']
        # Database port
        self.port = config_dict['port']
        # Characters to generate words for when matching a phrase
        self.word_chars = config_dict['word_chars']
        # Regex for phrase replacement searches in messages
        self.phrase_re = compile(config_dict['phrase_re'])
        # Regex for emoji injection searches in messages
        self.emoji_re = compile(config_dict['emoji_re'])
        # Path to the font used for generating bingo boards
        self.fontpath = config_dict['fontpath']
        # Dict for enabling/disabling bot functionality
        self.functions_status = config_dict['functions_status']


    def reload_config(self, config_path='slackbot_config.json'):
        """Optional method to reload config file for changes
        
        Keyword Arguments:
            config_path {str} -- Optional argument for path to config file (default: {'slackbot_config.json'})
        """
        
        config_dict = load(open(config_path, 'rb'))
        self.emoji_sub = config_dict['emoji_sub']
        self.db_name = config_dict['db_name']
        self.db_user = config_dict['db_user']
        self.word_chars = config_dict['word_chars']
        self.phrase_re = compile(config_dict['phrase_re'])
        self.emoji_re = compile(config_dict['emoji_re'])
        self.fontpath = config_dict['fontpath']
        self.functions_status = config_dict['functions_status']
