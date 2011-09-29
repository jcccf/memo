from collections import defaultdict
import sqlite3
from misc import *
from parsers.Bing import *
BASE = '../data/chameleon/'

app_id = 1
MOVIES = BASE+'movie_titles_metadata.txt'
LINES = BASE+'movie_lines.txt'
CONVS = BASE+'movie_conversations.txt'

convs = defaultdict(dict)
convid = 0
with open(CONVS,'r') as f:
  for l in f:
    a, b, mid, conva = l.split(' +++$+++ ')
    conva = eval(conva)
    for c in conva:
      convs[mid][c] = convid
    convid += 1

convid_g = 0
convid_hash = {}
def get_convid(mid,l_num):
  global convid_g
  if convs.has_key(mid) and convs[mid].has_key(l_num):
    if not convid_hash.has_key(convs[mid][l_num]):
      convid_hash[convs[mid][l_num]] = convid_g
      convid_g += 1
    return convid_hash[convs[mid][l_num]]
  else:
    convid_g += 1
    return (convid_g-1)

movies = {}
with open(MOVIES,'r') as f:
  for l in f:
    mid, name, _ = l.split(' +++$+++ ', 2)
    movies[mid] = name

movie_lines = defaultdict(list)
with open(LINES,'r') as f:
  for l in f:
    l_num, _, mid, actor, quote = l.split(' +++$+++ ')
    movie_lines[mid].append((l_num, actor, quote))
    
for mid, quotes in movie_lines.iteritems():
  movie_lines[mid] = sorted(quotes, key=lambda x:x[0])
  
for mid, quotes in movie_lines.iteritems():
  movie_lines[mid] = [(l_num, get_convid(mid, l_num), actor, quote) for (l_num, actor, quote) in quotes]

# Now Do DB Stuff

MDb.db_prepare_movie('../data/chameleon.sqlite')
progress = MProgress.Progress('../data/chameleon.pickle_prog')
conn = sqlite3.connect('../data/chameleon.sqlite')
conn.text_factory = str
c = conn.cursor()

for mid, quotes in movie_lines.iteritems():
  movie_name = movies[mid]

  print "Starting %s..." % movie_name
  
  # Query each quote with and without the movie
  # Store Results
  for _, conv_id, actor, quote in quotes:
    if progress.is_completed((mid,actor,quote)):
      continue
    # Search for Full Utterances
    quote_q = quote.replace('\"','')
    r1 = get_bing("\"%s\"" % quote_q, app_id)
    r2 = get_bing("\"%s\" \"%s\"" % (movie_name, quote_q), app_id)
    if r1 == None or r2 == None:
      progress.save()
      raise Exception("Progress Saved! Bing Failed!")
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
        r1 = get_bing("\"%s\"" % sentence, app_id)
        r2 = get_bing("\"%s\" \"%s\"" % (movie_name, sentence), app_id)
        if r1 == None or r2 == None:
          progress.save()
          raise Exception("Progress Saved! Bing Failed!") 
        MDb.sql_ins(c, conv_id, movie_name, actor, sentence, 'sentence', 'plain', r1[0], str(r1[1]))
        MDb.sql_ins(c, conv_id, movie_name, actor, sentence, 'sentence', 'movie_title', r2[0], str(r2[1]))
    
    # Commit to DB
    conn.commit()
    progress.complete((mid,actor,quote))
  
  print "Completed %s..." % movie_name

c.close()


#print movie_lines