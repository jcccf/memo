import nltk, string, pickle, sqlite3
from Progress import *
from BingParser import *
from QuoteFunctions import *
from DbFunctions import *
from optparse import OptionParser

# Options
parser = OptionParser()
parser.add_option("-n", "--name", type="string", dest="name", default="star_wars_a_new_hope", help="Filename (in data/scripts dir, without extension)")
parser.add_option("-s", "--search_name", type="string", dest="search_name", default="", help="Title of Movie that will be used in Search")
# parser.add_option("-t", "--type", type="string", dest="type", default="quotes", help="Quote Type (full or sentence)")
# parser.add_option("-u", "--max", type="int", dest="max", default=7, help="Max Word Length of a Quote")
# parser.add_option("-d", "--min", type="int", dest="min", default=5, help="Min Word Length of a Quote")
parser.add_option("-a", "--appid", type="int", dest="appid", default=0, help="AppID Number to Use")
(options, args) = parser.parse_args()

# MIN_LENGTH = options.min
# MAX_LENGTH = options.max
NAME = options.name
# QUOTE_TYPE = options.type
APP_ID = options.appid
SEARCH_NAME = options.search_name
if len(SEARCH_NAME) == 0:
  SEARCH_NAME = NAME.replace('_',' ')

# Load Everything Relevant
DATA_FILE = '../data/scripts/%s.pickle' % NAME
PROGRESS_FILE = '../data/scripts/%s.progress.pickle' % NAME
DB_FILE = '../data/scripts/db/%s.sqlite' % NAME
script=pickle.load(open(DATA_FILE,'r'))
progress = Progress(PROGRESS_FILE)
db_prepare_movie(DB_FILE)

# Connect to SQLite Database
conn = sqlite3.connect(DB_FILE)
conn.text_factory = str
c = conn.cursor()

def sql_ins(conv_id, movie_name, actor, quote, quote_type, query_type, result, urls):
  c.execute('INSERT INTO quotes (conv_id, movie, actor, quote, source, quote_type, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (conv_id, movie_name, actor, quote, 'bing', quote_type, query_type, result, urls))

def bingIt(movie_name, script, app_id=0):
  conv_id = 0
  for conversation in script:
    conv_id += 1
    for actor, quote in conversation:
      if progress.is_completed((actor,quote)):
        continue
    
      # Search for Full Utterances
      quote_q = quote.replace('\"','')
      r1 = get_bing("\"%s\"" % quote_q, app_id)
      r2 = get_bing("\"%s\" \"%s\"" % (movie_name, quote_q), app_id)
      if r1 == None or r2 == None:
        progress.save()
        raise Exception("Progress Saved! Bing Failed!")
      sql_ins(conv_id, movie_name, actor, quote, 'full', 'plain', r1[0], str(r1[1]))
      sql_ins(conv_id, movie_name, actor, quote, 'full', 'movie_title', r2[0], str(r2[1]))
      
      # Search for Sentences
      sentences = split_into_sentences(quote)
      if len(sentences) == 1:
        sql_ins(conv_id, movie_name, actor, quote, 'sentence', 'plain', r1[0], str(r1[1]))
        sql_ins(conv_id, movie_name, actor, quote, 'sentence', 'movie_title', r2[0], str(r2[1]))
      else:
        for sentence in sentences:
          sentence = sentence.replace('\"', '')
          r1 = get_bing("\"%s\"" % sentence, app_id)
          r2 = get_bing("\"%s\" \"%s\"" % (movie_name, sentence), app_id)
          if r1 == None or r2 == None:
            progress.save()
            raise Exception("Progress Saved! Bing Failed!") 
          sql_ins(conv_id, movie_name, actor, sentence, 'sentence', 'plain', r1[0], str(r1[1]))
          sql_ins(conv_id, movie_name, actor, sentence, 'sentence', 'movie_title', r2[0], str(r2[1]))

      conn.commit()
      progress.complete((actor,quote))

print 'Doing %s/%s' % (NAME, SEARCH_NAME)
bingIt(SEARCH_NAME, script, APP_ID)

c.close()