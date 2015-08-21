from lib import scraper, make_db_stats, query_db
import datetime
import argparse

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

    # Get int weeks for football
    if sport == 'football':
        end_date = 17
        return range(start_date + 1, end_date + 1)
    else:
        # Get yesterdays date (dont want games in progress)
        end_date = datetime.date.today() - datetime.timedelta(days=1)

    if start_date >= end_date:
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


def football_dates(beg, end):
    """
    Gets the football dates.  Because the football dates are read as weeks, need
    a different approach than basketball and baseball.
    """
    acceptable_vals = [None] + range(1,18)
    if beg not in acceptable_vals and end not in acceptable_vals:
        print "Date is not formatted properly"
        raise SystemExit

    if end is None:
        return [beg]
    else:
        return range(beg, end+1)

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


def get_args():
    opt = argparse.ArgumentParser(prog='DFS-Scraper')

    opt.add_argument("-b", "--begin",
                     type=int,
                     help="""Start date of data fetching.
                             Format: YYYYMMDD""")

    opt.add_argument("-e", "--end",
                     type=int,
                     help="""Start date of data fetching.
                             Format: YYYYMMDD""")

    opt.add_argument("-s", "--sport",
                     type=str,
                     required=True,
                     choices=['baseball', 'football'],
                     help="""Sport to fetch stats for.""")

    opt.add_argument("-l", "--logging",
                     type=str,
                     choices=['T', 'F'],
                     default='T',
                     help="""Set logging to be on or off.""")

    return opt.parse_args()


def write_to_log(date, errors):
    """
    This takes a pretty primative approach to logging the errors but I think
    it should be more than enough for now.
    """
    with open('log.txt', 'a') as f:
        f.write(str(date)+'\n')
        for line in errors:
            f.write(line)


def main(sport, date_list, logging=True):
    """
    Updates all of the data for the given dates in the given sport.
    """

    sport_class = {'baseball': make_db_stats.Baseball,
                   'basketball': make_db_stats.Basketball,
                   'football': make_db_stats.Football}

    for date in date_list:
        errors = []
        print date

        # List to hold the scraped data from RotoGuru
        try:
            scraped_data = [player for site_list in
                            [scraper.get_roto_info(date, site, sport) for site in ['fd', 'dk']]
                            for player in site_list]
        except Exception, e:
            errors.append("    Failed to scrape website data\n")
            errors.append("    {}\n".format(e))
            errors.append("\n")
            continue

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
                errors.append("    Failed to make class\n")
                errors.append("    for player data: {}\n".format(player_data))
                errors.append("    {}\n".format(e))
                errors.append("\n")
                continue

        # stat_list = [obj.gen_db_stats() for obj in player_objs.values()]
        stat_list = []
        for obj in player_objs.values():
            try:
                stat_list.append(obj.gen_db_stats())

            except Exception, e:
                errors.append("    Failed to generate stats\n")
                errors.append("    for player data: {}\n".format(obj.__dict__))
                errors.append("    {}\n".format(e))
                errors.append("\n")
                continue

        for player in stat_list:
            try:
                query_db.write_lines(player, sport)

            except Exception, e:
                errors.append("    Failed to write to DB\n")
                errors.append("    for player data: {}\n".format(player))
                errors.append("    {}\n".format(e))
                errors.append("\n")
                continue

        if errors and logging is True:
            write_to_log(date, errors)


if __name__ == '__main__':
    args = get_args()

    if args.sport != 'football':
        if args.begin and args.end:
            dates = date_range([args.begin, args.end])
        elif args.begin and not args.end:
            dates = date_range([args.begin, args.begin])
        else:
            dates = auto_dates(args.sport)
    else:
        if args.begin:
            dates = football_dates(args.begin, args.end)
        else:
            dates = auto_dates(args.sport)

    if args.logging == 'F':
        logging = False
    else:
        logging = True

    main(args.sport, dates, logging)