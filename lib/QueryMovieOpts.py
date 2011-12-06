import nltk, string, pickle, sqlite3, time, os.path
from misc import *
from parsers import *
from optparse import OptionParser

# Options
parser = OptionParser()
parser.add_option("-n", "--namefile", type="string", dest="name", default="../data/scripts/names.txt", help="Filename (in data/scripts dir, without extension)")
parser.add_option("-e", "--engine", type="string", dest="engine_name", default="bing", help="Name of Search Engine to use")
parser.add_option("-a", "--appid", type="int", dest="appid", default=0, help="AppID Number to Use")
parser.add_option("-r", "--random", action="store_true", default=False, dest="random")
(options, args) = parser.parse_args()

APP_ID = options.appid
ENGINE_NAME = options.engine_name
GET_RANDOMS = options.random
DUMMY_TEXT = 'lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed nec ligula diam, sit amet pharetra eros. Morbi a lacus id risus eleifend volutpat ut at nisl. Morbi vel tortor lacus. Sed luctus tempor neque, vehicula ultricies sapien laoreet eget.'
DUMMY_TEXT_2 = 'lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed nec ligula diam, sit amet pharetra eros. Morbi a lacus id risus eleifend volutpat ut at nisl. Morbi vel tortor lacus.'
DUMMY_TEXT_3 = 'lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed nec ligula diam, sit amet pharetra eros.'

# Load Script Filenames to Parse
if len(options.name) == 0:
  raise Exception("Provide a Names File!")
names, snames = [], []
with open(options.name, 'r') as f:
  for l in f:
    n, sn = l.replace('\n','').split('\t\t')
    names.append(n)
    snames.append(sn)

def doIt(name, movie_name='', app_id=0):
  print "Now processing %s..." % movie_name
  if len(movie_name) == 0:
    movie_name = name.replace('_',' ')
  # Load Everything Relevant
  data_file = '../data/scripts/%s.pickle' % name
  progress_file = '../data/scripts/%s.%s.pickle_prog' % (name, ENGINE_NAME)
  db_file = '../data/scripts/db/%s.%s.sqlite' % (name, ENGINE_NAME)
  script=pickle.load(open(data_file,'r'))
  progress = MProgress.Progress(progress_file)
  MDb.db_prepare_movie(db_file)
  
  # Connect to SQLite Database
  conn = sqlite3.connect(db_file)
  conn.text_factory = str
  c = conn.cursor()
  
  if ENGINE_NAME == 'blekko':
    parser = Blekko.Blekko(app_id)
  elif ENGINE_NAME == 'bing':
    parser = Bing.Bing(app_id)
  else:
    raise Exception("Invalid Search Engine Given")
  
  conv_id = 0
  for conversation in script:
    conv_id += 1
    for actor, quote in conversation:
      if progress.is_completed((actor,quote)):
        continue
    
      # Search for Full Utterances
      quote_q = quote.replace('\"','').replace('[','').replace('(', '').replace(']', '').replace(')', '')
      r1 = parser.get("\"%s\"" % quote_q)
      r2 = parser.get("\"%s\" \"%s\"" % (movie_name, quote_q))
      if r1 == None or r2 == None:
        progress.save()
        c.close()
        raise Exception("Progress Saved! Search Failed!")
      MDb.sql_ins(c, conv_id, movie_name, actor, quote, 'full', 'plain', r1[0], str(r1[1]), engine=ENGINE_NAME)
      MDb.sql_ins(c, conv_id, movie_name, actor, quote, 'full', 'movie_title', r2[0], str(r2[1]), engine=ENGINE_NAME)
      
      # Search for Sentences
      sentences = MQuote.split_into_sentences(quote)
      if len(sentences) == 1:
        MDb.sql_ins(c, conv_id, movie_name, actor, quote, 'sentence', 'plain', r1[0], str(r1[1]), engine=ENGINE_NAME)
        MDb.sql_ins(c, conv_id, movie_name, actor, quote, 'sentence', 'movie_title', r2[0], str(r2[1]), engine=ENGINE_NAME)
      else:
        for sentence in sentences:
          sentence = sentence.replace('\"', '')
          r1 = parser.get("\"%s\"" % sentence)
          r2 = parser.get("\"%s\" \"%s\"" % (movie_name, sentence))
          if r1 == None or r2 == None:
            progress.save()
            c.close()
            raise Exception("Progress Saved! Search Failed!") 
          MDb.sql_ins(c, conv_id, movie_name, actor, sentence, 'sentence', 'plain', r1[0], str(r1[1]), engine=ENGINE_NAME)
          MDb.sql_ins(c, conv_id, movie_name, actor, sentence, 'sentence', 'movie_title', r2[0], str(r2[1]), engine=ENGINE_NAME)

      conn.commit()
      progress.complete((actor,quote))
  c.close()

def doRandom(movie_filenames, movie_names, app_id=0):
  # Load Everything Relevant
  db_file = '../data/scripts/db/%s.%s.sqlite' % (os.path.basename(options.name).split('.')[0], ENGINE_NAME)
  progress_file = '../data/scripts/db/%s.%s.sqlite' % (os.path.basename(options.name).split('.')[0], ENGINE_NAME)
  progress = MProgress.Progress(progress_file)
  MDb.db_prepare_movie(db_file)

  # Connect to SQLite Database
  conn = sqlite3.connect(db_file)
  conn.text_factory = str
  c = conn.cursor()

  if ENGINE_NAME == 'blekko':
    parser = Blekko.Blekko(app_id)
  elif ENGINE_NAME == 'bing':
    parser = Bing.Bing(app_id)
  else:
    raise Exception("Invalid Search Engine Given")

  conv_id = 0
  for movie_filename, movie_name in zip(movie_filenames,movie_names):
    if progress.is_completed(movie_filename):
      continue

    # Search for Full Utterances
    quote_q = movie_name.replace('\"','')
    r1 = parser.get("\"%s\"" % quote_q)
    r2 = parser.get("\"%s\" \"%s\"" % (quote_q, DUMMY_TEXT))
    r3 = parser.get("\"%s\" \"%s\"" % (quote_q, DUMMY_TEXT_2))
    r4 = parser.get("\"%s\" \"%s\"" % (quote_q, DUMMY_TEXT_3))
    if r1 == None or r2 == None or r3 == None or r4 == None:
      progress.save()
      c.close()
      raise Exception("Progress Saved! Search Failed!")
    MDb.sql_ins(c, 0, movie_name, movie_filename, '', 'full', 'movie_title_only', r1[0], str(r1[1]), engine=ENGINE_NAME)
    MDb.sql_ins(c, 0, movie_name, movie_filename, DUMMY_TEXT, 'full', 'movie_title', r2[0], str(r2[1]), engine=ENGINE_NAME)
    MDb.sql_ins(c, 0, movie_name, movie_filename, DUMMY_TEXT_2, 'full', 'movie_title_2', r3[0], str(r3[1]), engine=ENGINE_NAME)
    MDb.sql_ins(c, 0, movie_name, movie_filename, DUMMY_TEXT_3, 'full', 'movie_title_3', r4[0], str(r4[1]), engine=ENGINE_NAME)
    conn.commit()
    progress.complete(movie_filename)
  
  c.close()


if GET_RANDOMS:
  print "Getting Random Counts for %s..." % options.name
  doRandom(names, snames, APP_ID)
else:
  print 'Getting Counts via %s...' % (ENGINE_NAME)
  # Keep Retrying
  i = 0
  while i < len(names):
    try:
      #doIt(SEARCH_NAME, script, APP_ID)
      doIt(names[i], snames[i], APP_ID)
      i += 1
    except Exception as detail:
      print "Caught Exception: ", detail
      print "Sleeping for 15 minutes..."
      time.sleep(900)