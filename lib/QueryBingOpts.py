import nltk, string, pickle, sqlite3
from Progress import *
from BingParser import *
from QuoteFunctions import *
from DbFunctions import *
from optparse import OptionParser

# Options
parser = OptionParser()
parser.add_option("-n", "--name", type="string", dest="name", default="quotes_parsed_single", help="Filename (in data dir, without extension)")
parser.add_option("-t", "--type", type="string", dest="type", default="imdb_singles", help="Quote Type (just an identifier)")
parser.add_option("-u", "--max", type="int", dest="max", default=7, help="Max Word Length of a Quote")
parser.add_option("-d", "--min", type="int", dest="min", default=5, help="Min Word Length of a Quote")
parser.add_option("-a", "--appid", type="int", dest="appid", default=0, help="AppID Number to Use")
(options, args) = parser.parse_args()

MIN_LENGTH = options.min
MAX_LENGTH = options.max
NAME = options.name
QUOTE_TYPE = options.type
APP_ID = options.appid

# Load Everything Relevant
DATA_FILE = '../data/%s.pickle' % NAME
PROGRESS_FILE = '../data/%s.progress.pickle' % NAME
DB_FILE = '../data/db_%s.sqlite' % NAME
movie_quotes=pickle.load(open(DATA_FILE,'r'))
filtered = filter_by_length(movie_quotes, MIN_LENGTH, MAX_LENGTH)
progress = Progress(PROGRESS_FILE)
db_prepare(DB_FILE)

# Connect to SQLite Database
conn = sqlite3.connect(DB_FILE)
conn.text_factory = str
c = conn.cursor()

def bingIt(filtered, quote_type, app_id=0):
  last_movie = ''
  for movie, actor, quote in filtered:
    if progress.is_completed((movie,actor,quote)):
      continue
    
    if last_movie is not movie:
      print movie
      last_movie = movie  
    
    quote_q = quote.replace('\"','')
    r1 = get_bing("\"%s\"" % quote_q, app_id)
    r2 = get_bing("\"%s\" \"%s\"" % (movie, quote_q), app_id)  
   
    if r1 == None or r2 == None:
      progress.save()
      raise Exception("Progress Saved! Bing Failed!") 
      
    c.execute('INSERT INTO quotes (movie, actor, quote, source, quote_type, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', (movie, actor, quote, 'bing', quote_type,'plain', r1[0], str(r1[1])))
    c.execute('INSERT INTO quotes (movie, actor, quote, source, quote_type, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', (movie, actor, quote, 'bing', quote_type,'movie_title', r2[0], str(r2[1])))
    
    conn.commit()
    progress.complete((movie,actor,quote))

print 'Doing %s (%s)' % (QUOTE_TYPE, NAME)
bingIt(filtered, QUOTE_TYPE, APP_ID)

c.close()