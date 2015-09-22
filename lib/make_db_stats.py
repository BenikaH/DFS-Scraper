
"""
Add something to check that player ID is in ID list.
"""

class Player(object):
    def __init__(self, date, game_record):
        """
        See specific sport subclasses for game_record format.
        """
        self.date = date
        self.name = game_record[1]
        self.fd_position = None
        self.fd_pts = None
        self.fd_salary = None
        self.dk_position = None
        self.dk_pts = None
        self.dk_salary = None
        self.team = game_record[4].upper()
        self.opp = self.format_opp(game_record[5])
        self.id = game_record[-1]

        site = game_record[-2]
        self.update_points(game_record[2], site)
        self.update_position(game_record[0], site)
        self.update_salary(game_record[3], site)

    def format_opp(self, opp_name):
        """
        Formats the opponent name and sets location of game.
        :param opp_name:
            'v kan' or '@ kan'
        :return:
            upper cased opp name and sets home/away game
        """
        loc, name = opp_name.split()

        # Get rid of double-header indicator if it exists
        name = name.split('(')[0]

        if loc == 'v' or loc == 'v.':
            self.home_game = 'Y'
        elif loc == '@':
            self.home_game = 'N'

        return name.upper()

    def format_position(self, position):
        """Defer to subclass"""
        return position

    def format_stats(self, stat_dict):
        """
        Attempts to format the stats for a player. No football stats are
        given so don't use for football.

        Method: Separate the numerical value from the stat name and update the
        dictionary.
        :stat_dict:
            A dictionary of stat_name keys with 0 for value.
        :return:
        Dictionary with updated stats.
        """
        try:
            player_stats = self.stats.split()
        except:
            print 'no player stats available.'
            return stat_dict

        for n, stat in enumerate(player_stats):
            numbers = '0123456789-'
            idx = 0
            stat_val = ''

            while stat[idx] in numbers:
                stat_val += stat[idx]
                idx += 1

            if stat_val == '':
                stat_val = '1'

            stat_name = stat.strip(stat_val)

            # Try to convert to int
            try:
                stat_val = int(stat_val)
            except:
                pass

            stat_dict[stat_name] = stat_val

        return stat_dict

    def gen_db_stats(self):
        """
        Generates a list of stats to be used in adding to the DB.
        :return:
        """
        stat_order = self.get_stat_order()
        stat_list = []

        dict_of_attrs = self.__dict__
        dict_of_attrs.update(self.stats)

        for name in stat_order:
            stat_list.append(dict_of_attrs[name])

        return stat_list

    def get_stat_order(self):
        """Used in subclasses"""
        pass

    def update_points(self, points, site):
        """Updates the points for given site"""
        if site == 'dk':
            self.dk_pts = float(points)
        elif site == 'fd':
            self.fd_pts = float(points)

    def update_position(self, position, site):
        """Updates the position of each site"""
        if site == 'dk':
            self.dk_position = self.format_position(position)
        elif site == 'fd':
            self.fd_position = self.format_position(position)

    def update_salary(self, dollars, site):
        """
        Updates the salaries for the given site.
        :param dollars:
            string like '$5,700'
        :return:
            int like 5700
        """
        if dollars == 'N/A':
            salary = 0
        else:
            salary = int(dollars.strip('$').replace(',', ''))

        if site == 'dk':
            self.dk_salary = salary
        elif site == 'fd':
            self.fd_salary = salary

class Baseball(Player):
    def __init__(self, date, game_record):
        """
        game_record format:
            [position, name, points, salary, team, opponent, game score, player game stats, site, player id]
        """
        self.score = game_record[6]
        self.stats = game_record[7]
        Player.__init__(self, date, game_record)

        self.format_name()
        self.format_team()
        self.format_stats()

    def format_name(self):
        """
        Sets starting info and removes it from name string.
        :return:
        """
        if '^' in self.name:
            self.start = 'Y'
            self.name, self.bat_order = self.name.split('^')

        else:
            self.start = 'N'
            self.bat_order = '0'

    def format_position(self, position):
        """
        Takes the numbered position format used by RG for Draft Kings stats
        :return:
        """
        # Need a way to differentiate pitchers from hitters.
        if position == 'P':
            self.pitcher = True
        else:
            self.pitcher = False

        # Pick up the players with no listed position.
        if position == '':
            if 'IP' in self.stats:
                self.pitcher = True
                new_position = 'P'
            else:
                new_position = 'N/A'
            return new_position

        # Only need to format numeric positions
        if not position.isdigit():
            return position

        position_convert = {'2': 'C', '3': '1B', '4': '2B', '5': '3B',
                            '6': 'SS', '7': 'OF', '8': 'OF', '9': 'OF'}

        pos_string = ''
        for pos in position:
            pos_string += ' {},'.format(position_convert[pos])

        return pos_string.strip(',').strip()

    def format_stats(self):
        """
        Loops through all the stats and creates a dict to easily load into DB.
        """
        batter_stats = {stat:0 for stat in ['H', 'AB', 'R', 'RBI', 'HR', '2B', '3B',
                                            'BB', 'HBP', 'SO', 'SF', 'S', 'SB', 'CS', 'E']}
        pitcher_stats = {stat:0 for stat in ['IP', 'HB', 'K', 'BB', 'H', 'R', 'ER', 'E',
                                             'Win', 'CG', 'Hold', 'Save', 'Loss']}

        stats = self.stats.split()

        stats_to_add = {}

        if self.pitcher:
            player_dict = pitcher_stats
            num_innings = stats.pop(0).strip('IP')
            stats_to_add['IP'] = float(num_innings)

        else:
            player_dict = batter_stats
            # Get hits and at bats for batters before parent method
            try:
                hits, atbats = stats.pop(0).split('/')
            except:
                hits, atbats = 0, 0

            stats_to_add['H'] = int(hits)
            stats_to_add['AB'] = int(atbats)

        # Pull out 2B and 3B stats before because the parent stat method doesn't pick them up properly
        for hit_type in ['2B', '3B']:
            for s in stats:
                if s[-2:] == hit_type:
                    if '-' in s:
                        stat_val = s.split('-')[0]
                    else:
                        stat_val = 1
                    stats_to_add[hit_type] = stat_val
                    stats.remove(s)

        self.stats = ' '.join(stats)
        self.stats = Player.format_stats(self, player_dict)
        self.stats.update(stats_to_add)

    def format_team(self):
        """
        Reformats the team name to be more consistent with BBM and FG team names.
        """
        team_convert = {'TAM': 'TB', 'KAN': 'KC', 'SFO': 'SF', 'SDG': 'SD'}

        if self.team in team_convert:
            self.team = team_convert[self.team]

        if self.opp in team_convert:
            self.opp = team_convert[self.opp]

    def get_stat_order(self):
        """
        Gets the order of stats to format them for adding to database.
        :return:
        """
        if self.pitcher:
            order = ['id', 'name', 'date', 'dk_position', 'dk_pts', 'dk_salary', 'fd_position', 'fd_pts', 'fd_salary',
                     'team', 'opp', 'score', 'home_game', 'bat_order', 'start', 'IP', 'K', 'BB', 'R', 'ER',
                     'H', 'HB', 'E', 'Win', 'Loss', 'Save', 'Hold', 'CG']
        else:
            order = ['id', 'name', 'date', 'dk_position', 'dk_pts', 'dk_salary', 'fd_position', 'fd_pts', 'fd_salary',
                     'team', 'opp', 'score', 'home_game', 'bat_order', 'start', 'H', 'AB', '2B', '3B', 'HR',
                     'BB', 'SO', 'RBI', 'SB', 'CS', 'S', 'SF', 'HBP', 'E']

        return order


class Basketball(Player):
    def __init__(self, date, game_record):
        Player.__init__(self, date, game_record)
        self.mins = int(game_record[6])
        self.stats = game_record[7]

        self.format_name()
        self.format_stats()

    def format_name(self):
        """
        Sets starting info and removes it from name string.
        :return:
        """
        if '^' in self.name:
            self.start = 'Y'
            self.name = self.name.strip('^')

        else:
            self.start = 'N'

        lname, fname = [x.strip() for x in self.name.split(',')]
        self.name = '{} {}'.format(fname, lname)

    def format_stats(self):
        """
        Formats the stats of basketball players.  Calls the parent method then
        formats a couple that are specific to basketball.
        :return:
        """
        stat_dict = {stat: 0 for stat in ['pt', 'rb', 'as', 'st', 'bl', 'tovr', 'trey',
                                         'fg', 'ft']}
        self.stats = Player.format_stats(self, stat_dict)

        #Need to format stats like ft and fg that are formatted like: att-made
        #Using two separate fields.
        for key in ['ft', 'fg']:
            try:
                att, made = self.stats[key].split('-')
            except:
                att, made = 0, 0
                pass

            # Make new keys
            att_key = '{}_att'.format(key)
            made_key = '{}_made'.format(key)

            self.stats[att_key], self.stats[made_key] = int(att), int(made)

            # Delete old keys & stats
            del self.stats[key]

    def get_stat_order(self):
        return ['id', 'name', 'date', 'dk_position', 'dk_pts', 'dk_salary', 'fd_position', 'fd_pts',
                'fd_salary', 'team', 'opp', 'home_game', 'mins', 'pt', 'rb', 'as', 'st', 'bl', 'tovr',
                'trey', 'fg_made', 'fg_att', 'ft_made', 'ft_att']


class Football(Player):
    def __init__(self, date, game_record):
        self.stats = {}
        Player.__init__(self, date, game_record)

    def get_stat_order(self):
        return ['id', 'name', 'date', 'dk_position', 'dk_pts', 'dk_salary', 'fd_position', 'fd_pts',
                'fd_salary', 'team', 'opp', 'home_game']