import nltk, string, pickle, sqlite3, time
from misc import *
from parsers import *
from optparse import OptionParser

# Options
parser = OptionParser()
parser.add_option("-n", "--name", type="string", dest="name", default="poslinesdict2.newmatch.111511", help="Filename without extension")
parser.add_option("-a", "--appid", type="int", dest="appid", default=0, help="AppID Number to Use")
parser.add_option("-e", "--engine", type="string", dest="engine_name", default="bing", help="Name of Search Engine to use")
parser.add_option("-s", "--separate", action="store_true", default=False, dest="separate")
(options, args) = parser.parse_args()

NAME = options.name
APP_ID = options.appid
ENGINE_NAME = options.engine_name
SEPARATE = options.separate

# Load Everything Relevant
DATA_FILE = '../data/pn2/%s.pickle' % NAME
PROGRESS_FILE = '../data/pn2/%s.%s.pickle_prog' % (NAME, ENGINE_NAME)
DB_FILE = '../data/pn2/db/%s.%s.sqlite' % (NAME, ENGINE_NAME)
MFile.pickle_load_mac(DATA_FILE)
movie_quotes=pickle.load(open(DATA_FILE+'.mac','r'))
progress = MProgress.Progress(PROGRESS_FILE)
MDb.db_prepare_movie(DB_FILE)

# Connect to SQLite Database
conn = sqlite3.connect(DB_FILE)
conn.text_factory = str
c = conn.cursor()

def insert_quote(parser, progress, c, conv_id, movie_name, actor, quote):
  # Search for Full Utterances
  quote_q = quote.replace('\"','')
  r1 = parser.get("\"%s\"" % quote_q)
  r2 = parser.get("\"%s\" \"%s\"" % (movie_name, quote_q))
  if r1 == None or r2 == None:
    progress.save()
    c.close()
    raise Exception("Progress Saved! Failed!")
  MDb.sql_ins(c, conv_id, movie_name, actor, quote, 'full', 'plain', r1[0], str(r1[1]))
  MDb.sql_ins(c, conv_id, movie_name, actor, quote, 'full', 'movie_title', r2[0], str(r2[1]))

  # Search for Sentences
  sentences = MQuote.split_into_sentences(quote)
  if len(sentences) == 1:
    MDb.sql_ins(c, conv_id, movie_name, actor, quote, 'sentence', 'plain', r1[0], str(r1[1]))
    MDb.sql_ins(c, conv_id, movie_name, actor, quote, 'sentence', 'movie_title', r2[0], str(r2[1]))
  else:
    for sentence in sentences:
      sentence = sentence.replace('\"', '')
      r1 = parser.get("\"%s\"" % sentence)
      r2 = parser.get("\"%s\" \"%s\"" % (movie_name, sentence))
      if r1 == None or r2 == None:
        progress.save()
        c.close()
        raise Exception("Progress Saved! Failed!") 
      MDb.sql_ins(c, conv_id, movie_name, actor, sentence, 'sentence', 'plain', r1[0], str(r1[1]))
      MDb.sql_ins(c, conv_id, movie_name, actor, sentence, 'sentence', 'movie_title', r2[0], str(r2[1]))

def doIt(movie_quotes, app_id=0):
  if ENGINE_NAME == 'blekko':
    parser = Blekko.Blekko(app_id)
  elif ENGINE_NAME == 'bing':
    parser = Bing.Bing(app_id)
  else:
    raise Exception("Invalid Search Engine Given")

  for movie_name, quotes in movie_quotes.iteritems():
    movie_name = MQuote.clean_movie_title(movie_name)
    print movie_name
    if SEPARATE:
      conv_id = 1
      for conv in quotes:
        for qline in conv:
          actor, quote = MQuote.actor_quote(qline)
          if progress.is_completed((movie_name,quote)):
            continue 
          insert_quote(parser, progress, c, conv_id, movie_name, actor, quote)
          # Commit to DB
          conn.commit()
          progress.complete((movie_name,quote))
        conv_id += 1
    else:      
      for actor,_,quote in quotes:      
        if progress.is_completed((movie_name,quote)):
          continue
        insert_quote(parser, progress, c, -1, movie_name, actor, quote)
        conn.commit()
        progress.complete((movie_name,quote))
    

print 'Getting Counts for %s on %s...' % (NAME, ENGINE_NAME)
# Keep Retrying
i = 0
while i == 0:
  try:
    doIt(movie_quotes, APP_ID)
    i += 1
  except Exception as detail:
    print "Caught Exception: ", detail
    print "Sleeping for 15 minutes..."
    time.sleep(900)
c.close()