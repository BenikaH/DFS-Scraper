#import db_connect
from DB import DB
import datetime
#import write_missing

# def check_id(name, player_id, sport):
#     """
#     Checks if the player id exists in the player_ids table and tried to
#     update it if not.
#     :param name:
#         name in the format 'first last'
#     :param player_id:
#         roto guru id number.
#     :return:
#     """
#
#     conn, cur = db_connect.connect(sport)
#
#     if sport == 'baseball':
#         cur.execute("SELECT COUNT(*) FROM player_ids WHERE rguru_id = %s", (player_id))
#         num_rguru_id = cur.fetchone()[0]
#         if num_rguru_id == 1:
#             return
#         else:
#             fname, lname = name.split(' ', 1)
#             cur.execute("SELECT COUNT(*), bbm_id FROM player_ids WHERE first_name=%s AND last_name=%s",
#                         (fname, lname))
#             cursor_val = cur.fetchone()
#             name_counts = cursor_val[0]
#             if name_counts == 1:
#                 bbm_id = cursor_val[1]
#                 cur.execute("UPDATE player_ids SET rguru_id=%s WHERE bbm_id=%s",
#                             (player_id, bbm_id))
#                 conn.commit()
#             elif name_counts > 1:
#                 write_missing.missing_player(name, player_id, sport, True)
#
#             elif name_counts == 0:
#                 write_missing.missing_player(name, player_id, sport)

def get_last_entry(sport):
    """
    Gets the last date entered into the database.
    :return:
    """
    cursor = DB()

    if sport == 'football':
        q = "SELECT MAX(week) AS date from rguru_stats"
    elif sport == 'baseball':
        q = "SELECT MAX(date) AS date from rguru_hitters"
    else:
        return

    last_date = cursor.query(q)[0][0]

    # If no entries in DB, get first date of season.
    if last_date is None:
        if sport == 'baseball':
            last_date = datetime.date(2015, 4, 5)
        elif sport == 'football':
            last_date = 1

    cursor.finish()

    return last_date

def write_lines(stat_line, sport):
    """
    Takes a list of stat lines and inserts them into the database.
    :param player_list:
        List of player stats.
    :param sport:
        String of sport, e.g. 'baseball'
    :return:
    """
    cursor = DB()

    player_id = stat_line[0]
    date = stat_line[2]
    q = []
    if sport == 'baseball':
        if stat_line[3] != 'P':
            q.append(["DELETE FROM rguru_hitters WHERE id = %s AND date = %s", (player_id, date)])
            q.append(["INSERT INTO rguru_hitters VALUES({})".format(','.join(['%s']*len(stat_line))), stat_line])
        else:
            q.append(["DELETE FROM rguru_pitchers WHERE id = %s AND date = %s", (player_id, date)])
            q.append(["INSERT INTO rguru_pitchers VALUES({})".format(','.join(['%s']*len(stat_line))), stat_line])
    elif sport == 'football':
        q.append(["DELETE FROM rguru_stats WHERE id = %s AND week = %s", (player_id, date)])
        q.append(["INSERT INTO rguru_stats VALUES({})".format(','.join(['%s']*len(stat_line))), stat_line])

    for query in q:
        cursor.query(*query)

    cursor.finish()
