import requests
from bs4 import BeautifulSoup
from urlparse import urlparse

"""
This module will scrape the RotoGuru pages for the player stats.
It is functional for baseball, basketball and football.
get_roto_info function returns the data formatted to be used by
classes in make_db_stats.
"""

def fetch_player_data(url, sport, site):
    """
    grabs the player data from the given web page.
    :param url:
        url of the page
    :param sport:
        given because the page data is different by sport.
    :return:
        a list of all player data
    """
    html = requests.get(url)
    soup = BeautifulSoup(html.content)

    all_data = []

    for n, player_row in enumerate(soup.find_all('tr')):
        pos = player_row.find('b')
        if pos:
            football_pos = pos.text.strip()

        # Only way i've found to differentiate player tr rows from
        # others is by number of td tags they contain.
        if len(player_row.findParents('table')) == 0 and\
                player_row.find('td', {'colspan':False}) and\
                len(player_row.find_all('b')) == 0:
            player_id = urlparse(player_row.find('a')['href']).query
            # Get the td tag text and format it.
            player_data = [data.text.replace(u'\xa0', u'').strip() for data in player_row.find_all('td')]
            player_data.append(site)
            player_data.append(player_id)

            if sport == 'football':
                position_convert = {'Quarterbacks': 'QB', 'Running Backs': 'RB',
                                    'Wide Receivers': 'WR', 'Tight Ends': 'TE',
                                    'Kickers': 'K', 'Defenses': 'D'}
                position = position_convert.get(football_pos, None)
                player_data.insert(0, position)

                # The football data has different indexes than baseball and basketball
                # so switch indexes 2 - 4, and 3 - 5
                player_data[2], player_data[4] = player_data[4], player_data[2]
                player_data[3], player_data[5] = player_data[5], player_data[3]

            all_data.append(player_data)

    return all_data


def get_date(date, sport):
    """
    Returns formatted date
    :param date:
        datetime.date instance
    """
    # Return early because football date will be in weeks.
    if sport == 'football':
        return 'week={}'.format(str(date))

    # convert date obj to strings and make sure single digit days have leading 0
    day, month, year = str(date.day).zfill(2), str(date.month), str(date.year)

    if sport == 'baseball':
        format_date = 'date={}&year={}'.format(month+day, year)
    elif sport == 'basketball':
        format_date = 'mon={}&day={}'.format(month, day)
    else:
        return

    return format_date


def get_url(date, site, sport):
    """
    Gets the url needed for given params.
    :return:
        formatted URL
    """
    path_dict = {'football': 'fyday.pl?',
                 'baseball': 'byday.pl?',
                 'basketball': 'hyday.pl?'}

    main_path = 'http://rotoguru1.com/cgi-bin/'
    sub_path = path_dict[sport]

    format_date = get_date(date, sport)

    game = '&game={}'.format(site)

    return main_path + sub_path + format_date + game


def get_roto_info(date, site, sport):
    """
    Main function to call other functions necessary to get info.
    :param date:
        format = 2015_06_15 or int <= 17 for football
    :param site:
        'fd' or 'dk'
    :param sport:
        'baseball', 'football', or 'basketball'
    :return:
        A list of lists for each player stats for the day.
    """
    url = get_url(date, site, sport)

    return fetch_player_data(url, sport, site)


def save_html(html, fname):
    """
    This will save the html from the website to a file. This is
    useful when testing to not have to keep making requests to the site.
    """
    fname = fname.strip('.html')
    with open('html/{}.html'.format(fname), 'w') as f:
        f.write(html)


def load_sample_html(fname):
    """
    Loads the sample html from a file.
    """
    fname = fname.strip('.html')
    with open('html/{}.html'.format(fname), 'r') as f:
        return f.read()