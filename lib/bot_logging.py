from datetime import datetime as dt
import datetime


def log_output(env, logs):
    """Singleton function to log messages and bot output

    Arguments:
        env {str} -- Runtime environment of bot
        logs {str} -- String to log
    """

    log_filename = '_'.join('{0} Bot Logs {1}'.format(
        env.capitalize(), dt.now().strftime('%Y-%m-%d')).split())
    log_file = open('logs/' + log_filename, 'a+')
    log_file.write(logs)
    log_file.close()
