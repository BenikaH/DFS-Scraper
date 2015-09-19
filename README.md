# DFS-Scraper

##Description
This program will scrape the data from RotoGuru.com DraftKings and FanDuel tables and add it to a MySQL database. It fetches data like the salary and points by each player of a given date and also shows some of the basic stats.  It is fully functional for MLB and NFL with NBA not being too far behind. 

##Requirements
* Python 2.6
* BeatifulSoup
* MySQLDB
* requests

##To Start: 
1. Create tables using the schema in the SQL folder
2. Edit the db.ini file with your DB credentials
3. Run roto_fetcher.py from command and edit arguments -s, -b, -e: 
    * Set -s (--sport) for sport wanted (mandatory) (Only baseball supported for now)
    * Set -b (--begin) as YYYYMMDD int for starting date
    * Set -e (--end) same as start date for end date
      - Setting -b without -e will fetch a single date
      - Omitting -b and -e will fetch the last DB entry and current date as start and end 
    * Set -l (--logging) to F to disable logging (defaults to T)
      - Logging is a simple feature manually written to write errors to text file, font think I need full logging capabilities (i.e. from python logging module) for time being
            
##Notes: 
Now compatible with NFL football. To use, run with '-s football' and specify date in weeks as int 1-17 instead of date.  
(9/19) Now compatible with basketball. Use '-s basketball' and dates similar to baseball.  Will word for dates from opening day of 2014-2015 season (Oct 28 2014) to the end of the regular season (Apr 15 2015).
