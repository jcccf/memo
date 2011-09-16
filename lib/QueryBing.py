# QueryGoogle - use GoogleParser to find out information about the quotes
# obtained from QuotesParser

from BingParser import *
import sqlite3, pickle, string

table = string.maketrans("","")
punct = string.punctuation.replace('\'','')
def remove_punctuation(quote):
  return quote.translate(table, punct)

movie_quotes=pickle.load(open('../data/title_to_quotes_parsed.pickle','r'))

continue_from = 'kalifornia'

conn = sqlite3.connect('../data/db.sqlite')
conn.text_factory = str
c = conn.cursor()

for movie, quotes in movie_quotes:
  if continue_from and movie != continue_from:
    continue
  continue_from = None
  
  print "Starting %s..." % movie
  
  # Query each quote with and without the movie
  # Store Results
  for actor, quote in quotes:
    quote_q = quote.replace('\"','')
    # r1 = get_google("\"%s\"" % quote_q)
    # r2 = get_google("\"%s\" \"%s\"" % (movie, quote_q))
    r1 = get_bing("\"%s\"" % quote_q)
    r2 = get_bing("\"%s\" \"%s\"" % (movie, quote_q))    

    if r1 == None or r2 == None:
      raise Exception("Bing Failed!")

    c.execute('INSERT INTO quotes (movie, actor, quote, source, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?)', (movie, actor, quote, 'bing', 'plain', r1[0], str(r1[1])))
    c.execute('INSERT INTO quotes (movie, actor, quote, source, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?)', (movie, actor, quote, 'bing', 'with_movie', r2[0], str(r2[1])))
  conn.commit()
  print "Completed %s..." % movie

c.close()