import nltk, string, pickle, sqlite3
from Progress import *
from BingParser import *
from QuoteFunctions import *
from DbFunctions import *
from optparse import OptionParser

# Options
parser = OptionParser()
parser.add_option("-n", "--name", type="string", dest="name", default="slogans_mac", help="Filename (in data dir, without extension)")
parser.add_option("-t", "--type", type="string", dest="type", default="slogan", help="Quote Type (just an identifier)")
(options, args) = parser.parse_args()

NAME = options.name
QUOTE_TYPE = options.type

# Load Everything Relevant
DATA_FILE = '../data/%s.pickle' % NAME
PROGRESS_FILE = '../data/%s.progress.pickle' % NAME
DB_FILE = '../data/db_%s.sqlite' % NAME
quotes=pickle.load(open(DATA_FILE,'r'))
progress = Progress(PROGRESS_FILE)
db_prepare(DB_FILE)

# Connect to SQLite Database
conn = sqlite3.connect(DB_FILE)
conn.text_factory = str
c = conn.cursor()

def bingIt(quotes, quote_type):
  for quote in quotes:
    if progress.is_completed(quote):
      continue
    
    quote_q = quote.replace('\"','')
    r1 = get_bing("\"%s\"" % quote_q)
   
    if r1 == None:
      progress.save()
      raise Exception("Progress Saved! Bing Failed!") 
      
    c.execute('INSERT INTO quotes (movie, actor, quote, source, quote_type, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', ('', '', quote, 'bing', quote_type,'plain', r1[0], str(r1[1])))
    
    conn.commit()
    progress.complete(quote)

print 'Doing %s (%s)' % (QUOTE_TYPE, NAME)
bingIt(quotes, QUOTE_TYPE)

c.close()