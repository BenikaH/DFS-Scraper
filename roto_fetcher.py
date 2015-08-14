from lib import scraper, make_db_stats, query_db
import datetime

"""
Notes:

"""


def auto_dates(sport):
    """
    Will get the dates from the current date to the last entry.
    :return:
    """
    # Get latest entry in the db
    start_date = query_db.get_last_entry(sport)

    # Get yesterdays date (dont want games in progress)
    end_date = datetime.date.today() - datetime.timedelta(days=1)

    if start_date > end_date:
        return []

    return date_range([start_date, end_date])


def date_range(range_list):
    """
    Takes a list of [start date, end date] and makes a list of the range (inclusive)
    :param range_list:
        [yyyymmdd, yyyymmdd]
    :return:
        a list of datetime.date objects
    """
    start_date = datetime.date(*format_date(range_list[0]))
    end_date = datetime.date(*format_date(range_list[1]))

    delta = end_date - start_date

    return [end_date - datetime.timedelta(days=n) for n in range(delta.days+1)]


def format_date(date_str):
    """
    Takes the date in various formats and gets it to a uniform format
    :param date_str:
        'yyyymmdd', yyyymmdd(int), 'yyyy-mm-dd' (other delimiters = _ /)
    :return:
        list of ints: [yyyy,mm,dd]
    """
    formatted_date = str(date_str)

    for char in '/-_':
        formatted_date = formatted_date.replace(char, '')

    if len(formatted_date) != 8 or formatted_date.isdigit() is False:
        print "Date '{}' is not formatted properly".format(formatted_date)
        raise SystemExit
    else:
        # split the 8 digit date into [yyyy,mm,dd]
        return [int(formatted_date[x:y]) for x, y in zip([0, 4, 6], [4, 6, 8])]


def main(sport, dates='auto'):
    """
    Updates all of the data for the given dates in the given sport.
    :param sport:
    :param dates:
    :return:
    """
    if dates == 'auto':
        date_list = auto_dates(sport)
    else:
        if type(dates) is list:
            date_list = date_range(dates)
        else:
            date_list = date_range([dates, dates])

    sport_class = {'baseball': make_db_stats.Baseball,
                   'basketball': make_db_stats.Basketball}

    for date in date_list:
        print date

        # List to hold the scraped data from RotoGuru
        scraped_data = [player for site_list in
                        [scraper.get_roto_info(date, site, sport) for site in ['fd', 'dk']]
                        for player in site_list]

        player_objs = {}
        for player_data in scraped_data:
            try:
                player_id = player_data[-1]
                if player_id not in player_objs:
                    player_objs[player_id] = sport_class[sport](date, player_data)
                else:
                    site = player_data[-2]
                    player_objs[player_id].update_points(player_data[2], site)
                    player_objs[player_id].update_position(player_data[0], site)
                    player_objs[player_id].update_salary(player_data[3], site)

            except Exception, e:
                # Add logging info
                pass

        stat_list = [obj.gen_db_stats() for obj in player_objs.values()]

        for player in stat_list:
            try:
                query_db.write_lines(player, sport)

            except Exception, e:
                # Add logging info
                pass

if __name__ == '__main__':
    main('baseball', '20150813')