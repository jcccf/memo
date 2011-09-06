# QueryGoogle - use GoogleParser to find out information about the quotes
# obtained from QuotesParser

from GoogleParser import *
from BingParser import *
from Progress import *
import sqlite3, pickle, string

table = string.maketrans("","")
punct = string.punctuation.replace('\'','')
def remove_punctuation(quote):
  return quote.translate(table, punct)

movie_quotes=pickle.load(open('../data/title_to_quotes_parsed.pickle','r'))

progress = Progress('../data/title_to_quotes_google_progress.pickle')

conn = sqlite3.connect('../data/db.sqlite')
conn.text_factory = str
c = conn.cursor()

for movie, quotes in movie_quotes:
  if progress.is_completed(movie):
    continue

  print "Starting %s..." % movie
  
  # Query each quote with and without the movie
  # Store Results
  for actor, quote in quotes:
    if progress.is_completed((movie,quote)):
      continue
    
    quote_q = quote
    r1 = get_google("\"%s\"" % quote_q)
    r2 = get_google("\"%s\" \"%s\"" % (movie, quote_q))

    if r1 == None or r2 == None:
      progress.save()
      raise Exception("Progress Saved; Bing Failed!")

    c.execute('INSERT INTO quotes (movie, actor, quote, source, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?)', (movie, actor, quote, 'bing', 'plain', r1[0], str(r1[1])))
    c.execute('INSERT INTO quotes (movie, actor, quote, source, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?)', (movie, actor, quote, 'bing', 'with_movie', r2[0], str(r2[1])))
    
    conn.commit()
    progress.complete((movie,quote))
  
  progress.complete(movie)
  print "Completed %s..." % movie

c.close()