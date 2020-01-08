from PIL import Image, ImageDraw, ImageFont
from random import randrange as rr
from os.path import exists
from os import mkdir
from psycopg2 import connect


def gen_bingo(dbname, user, filename, width, height, bg_color, line_color, text_color, font_path, free_space=''):
    """Generate a bingo image

    Arguments:
        dbname {str} -- Database to access
        user {str} -- Username used to access the database
        filename {str} -- Name for the file to be output to
        width {int} -- Width of the output image
        height {int} -- Height of the output image
        bg_color {tuple} -- Tuple describing the color of the BG of the image, in RGB format
        line_color {tuple} -- Tuple describing the color of the grid lines, in RGB format
        text_color {tuple} -- Tuple describing the color of the text, in RGB format
        font_path {str} -- Path to the font wanting to be used

    Returns:
        bool -- Boolean for whether an image was created successfully
    """

    if(not exists('output')):
        mkdir('output')

    bingo_board = Image.new('RGBA', (width, height), color=bg_color)

    draw = ImageDraw.Draw(bingo_board)
    for l in range(1, 5):
        draw.line(xy=[(0, int(height/5)*l), (width, int(height/5)*l)],
                  fill=line_color, width=5, joint=None)
        draw.line(xy=[(int(width/5)*l, 0), (int(width/5)*l, height)],
                  fill=line_color, width=5, joint=None)

    board_values = []
    con = connect("dbname={0} user={1}".format(dbname, user))
    cur = con.cursor()

    it = 0
    while it < 25:
        if(it == 12):
            board_values.append('(Free Space)\n{0}'.format(free_space))
            it += 1
        else:
            roll = rr(100)
            main_len = 0
            extra_len = 0
            try:
                cur.execute(
                    "SELECT COUNT(word) FROM bingo WHERE main IS TRUE AND used IS FALSE;")
                main_len = cur.fetchone()[0]
            except:
                main_len = 0
            try:
                cur.execute(
                    "SELECT COUNT(word) FROM bingo WHERE main IS FALSE AND used IS FALSE;")
                extra_len = cur.fetchone()[0]
            except:
                extra_len = 0
                print('Something very bad happened.')

            if(main_len > 0 and roll < 80):
                cur.execute(
                    "SELECT word FROM bingo WHERE main IS TRUE AND used IS FALSE;")
                new_word = cur.fetchall()[rr(main_len)][0]
                board_values.append(new_word)
                cur.execute(
                    "UPDATE bingo SET used=TRUE WHERE word='{0}';".format(new_word))
                it += 1
            if(extra_len > 0 and roll >= 80):
                cur.execute(
                    "SELECT word FROM bingo WHERE main IS FALSE AND used IS FALSE;")
                new_word = cur.fetchall()[rr(extra_len)][0]
                board_values.append(new_word)
                cur.execute(
                    "UPDATE bingo SET used=TRUE WHERE word='{0}';".format(new_word))
                it += 1

            con.commit()

    cur.execute("UPDATE bingo SET used=FALSE;")
    con.commit()
    con.close()

    font = ImageFont.truetype(font_path, 16)
    for i in range(len(board_values)):
        text_output = board_values[i].replace('\\n', '\n').strip()
        text_size = draw.textsize(text_output, font)
        text_x = int(width/10 - text_size[0]/2) + (i % 5)*int(width/5)
        text_y = int(height/10 - text_size[1]/2) + int(i/5)*int(height/5)
        draw.text(
            xy=(text_x, text_y),
            text=text_output,
            fill=text_color,
            font=font,
            align='center'
        )

    bingo_board.save('output/{0}.png'.format(filename))

    return True
