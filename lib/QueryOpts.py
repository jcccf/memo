import nltk, string, pickle, sqlite3
from misc import *
from parsers import *
from optparse import OptionParser

# Options
parser = OptionParser()
parser.add_option("-n", "--name", type="string", dest="name", default="quotes_parsed_single", help="Filename (in data dir, without extension)")
parser.add_option("-t", "--type", type="string", dest="type", default="", help="Quote Type (just an identifier)")
parser.add_option("-u", "--max", type="int", dest="max", default=99, help="Max Word Length of a Quote")
parser.add_option("-d", "--min", type="int", dest="min", default=1, help="Min Word Length of a Quote")
parser.add_option("-a", "--appid", type="int", dest="appid", default=0, help="AppID Number to Use")
parser.add_option("-e", "--engine", type="string", dest="engine_name", default="blekko", help="Name of Search Engine to use")
(options, args) = parser.parse_args()

MIN_LENGTH = options.min
MAX_LENGTH = options.max
NAME = options.name
QUOTE_TYPE = options.type
if len(QUOTE_TYPE) == 0:
  QUOTE_TYPE = NAME
APP_ID = options.appid
ENGINE_NAME = options.engine_name

# Load Everything Relevant
DATA_FILE = '../data/pn/%s.pickle' % NAME
PROGRESS_FILE = '../data/pn/%s.%s.pickle_prog' % (NAME, ENGINE_NAME)
DB_FILE = '../data/pn/db/%s.%s.sqlite' % (NAME, ENGINE_NAME)
movie_quotes=pickle.load(open(DATA_FILE,'r'))
filtered = MQuote.filter_by_length(movie_quotes, MIN_LENGTH, MAX_LENGTH)
progress = MProgress.Progress(PROGRESS_FILE)
MDb.db_prepare_movie(DB_FILE)

# Connect to SQLite Database
conn = sqlite3.connect(DB_FILE)
conn.text_factory = str
c = conn.cursor()

def doIt(filtered, quote_type, app_id=0):
  if ENGINE_NAME == 'blekko':
    parser = Blekko.Blekko(app_id)
  else:
    raise Exception("Invalid Search Engine Given")
  
  last_movie = ''
  for movie_name, actor, quote in filtered:
    
    if last_movie != movie_name:
      print movie_name
      last_movie = movie_name
    
    if progress.is_completed((movie_name,actor,quote)):
      continue
    # Search for Full Utterances
    quote_q = quote.replace('\"','')
    r1 = parser.get("\"%s\"" % quote_q)
    r2 = parser.get("\"%s\" \"%s\"" % (movie_name, quote_q))
    if r1 == None or r2 == None:
      progress.save()
      raise Exception("Progress Saved! Failed!")
    MDb.sql_ins(c, -1, movie_name, actor, quote, 'full', 'plain', r1[0], str(r1[1]))
    MDb.sql_ins(c, -1, movie_name, actor, quote, 'full', 'movie_title', r2[0], str(r2[1]))
    
    # Search for Sentences
    sentences = MQuote.split_into_sentences(quote)
    if len(sentences) == 1:
      MDb.sql_ins(c, -1, movie_name, actor, quote, 'sentence', 'plain', r1[0], str(r1[1]))
      MDb.sql_ins(c, -1, movie_name, actor, quote, 'sentence', 'movie_title', r2[0], str(r2[1]))
    else:
      for sentence in sentences:
        sentence = sentence.replace('\"', '')
        r1 = parser.get("\"%s\"" % sentence)
        r2 = parser.get("\"%s\" \"%s\"" % (movie_name, sentence))
        if r1 == None or r2 == None:
          progress.save()
          raise Exception("Progress Saved! Failed!") 
        MDb.sql_ins(c, -1, movie_name, actor, sentence, 'sentence', 'plain', r1[0], str(r1[1]))
        MDb.sql_ins(c, -1, movie_name, actor, sentence, 'sentence', 'movie_title', r2[0], str(r2[1]))
    
    # Commit to DB
    conn.commit()
    progress.complete((movie_name,actor,quote))

print 'Getting Counts for %s on %s...' % (NAME, ENGINE_NAME)
doIt(filtered, QUOTE_TYPE, APP_ID)

c.close()