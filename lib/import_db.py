#!/usr/bin/python
from psycopg2 import connect


def import_words(dbname='slackbot_db', user='slackbot'):
    """Import a list of words into the specified database
    
    Keyword Arguments:
        dbname {str} -- Name of the database to import to (default: {'slackbot_db'})
        user {str} -- User to import to database as (default: {'slackbot'})
    """
    try:
        con = connect("dbname={0} user={1}".format(dbname, user))
        cur = con.cursor()
    except:
        print('Couldn\'t connect to the database.')
    try:
        word_db = open('assets/word_db.txt')
    except:
        print('Didn\'t find the words file.')
    
    words = word_db.readlines()

    # Create words table
    try:
        cur.execute("CREATE TABLE words (letter varchar(1), id int, word varchar);")
    except:
        pass

    # Fill word table
    index_dict = {}
    for w in words:
        if(w.strip()):
            try:
                index_dict[w.strip()[0]] += 1
            except:
                index_dict[w.strip()[0]] = 0
            try:
                cur.execute("INSERT INTO words VALUES (%s, %s, %s);", (w.strip()[0], index_dict[w.strip()[0]], w.strip()))
            except:
                pass
                
    con.commit()
    con.close()


def import_bingo(dbname='slackbot_db', user='slackbot'):
    """Import the bingo word bank database and return a dictionary of the information
    
    Keyword Arguments:
        dbname {str} -- Name of the database to import to (default: {'slackbot_db'})
        user {str} -- User to import to the database as (default: {'slackbot'})
    """

    try:
        con = connect("dbname={0} user={1}".format(dbname, user))
        cur = con.cursor()
    except:
        print('I had an issue connecting to the database.')

    try:
        bingodb = open('assets/bingo_db.txt')
    except:
        print('I had an issue finding the bingo file.')
    
    bingo = bingodb.readlines()

    # Create bingo table
    try:
        cur.execute("CREATE TABLE bingo (main bool, id int, word varchar, used bool);")
    except:
        print('Table already created.')

    # Fill bingo table
    m_index = 0
    e_index = 0
    is_main = True
    for w in bingo:
        if(w.strip()):
            if(w.strip() == '---'):
                is_main = False
            else:
                if(is_main):
                    try:
                        cur.execute("INSERT INTO bingo VALUES ({0}, {1}, '{2}', FALSE);".format(is_main, m_index, w.strip()))
                    except:
                        pass
                else:
                    try:
                        cur.execute("INSERT INTO bingo VALUES ({0}, {1}, '{2}', FALSE);".format(is_main, e_index, w.strip()))
                    except:
                        pass

    con.commit()
    con.close()


if(__name__ == '__main__'):
    # Debugging
    pass