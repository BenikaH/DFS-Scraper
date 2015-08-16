import MySQLdb
from ConfigParser import ConfigParser
import os

class DB:
    def __init__(self):
        parser = ConfigParser()
        parser.read('{}/db.ini'.format(os.path.dirname(os.path.dirname(__file__))))
        user = parser.get('db', 'user')
        password = parser.get('db', 'password')
        db = parser.get('db', 'database')

        args = {'user': user, 'passwd': password, 'db': db}

        self.db = MySQLdb.connect(**args)
        self.cursor = self.db.cursor()

    def save(self):
        self.db.commit()

    def finish(self):
        self.db.commit()
        self.db.close()

    def query(self, query, values=None):
        res = self.cursor.execute(query, values)
        return self.cursor.fetchall()