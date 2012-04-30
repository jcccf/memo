import unidecode, re, string, pickle, nltk
from misc import *

mqs = MFile.pickle_load_mac('../data/fortest.pickle')

db = MDb.MMySQLDb('memo_turk', host='localhost', username='cf_memo')

# Reset Cleaned
db.q('UPDATE quote_pairs SET cleaned = 0')
db.q('UPDATE movies SET cleaned = 0')

for movie, quote in mqs.iteritems():
  movie = MQuote.clean_movie_title(movie)
  res = db.qt('SELECT COUNT(*) from quote_pairs WHERE movie_name = %s AND quote_1 = %s AND quote_2 = %s', (movie, quote[0], quote[1]))
  if res[0][0] > 0: # If this quote pair already exists
    db.qt('UPDATE quote_pairs SET cleaned = 1 WHERE movie_name = %s AND quote_1 = %s', (movie, quote[0]))
    db.qt('UPDATE movies SET cleaned = 1 WHERE movie_name = %s', (movie))
  else: # Else insert the new quote pair
    print "Inserting %s, %s, %s" % (movie, quote[0], quote[1])
    # Insert the movie too if it doesn't exist
    res = db.qt('SELECT COUNT(*) from movies WHERE movie_name = %s', (movie))
    if res[0][0] == 0:
      db.qt('INSERT INTO movies (movie_name, movie_title, is_imdb_top, cleaned) VALUES(%s, %s, %s, %s)', (movie, movie.title(), 0, 1))
    else:
      db.qt('UPDATE movies SET cleaned = 1 WHERE movie_name = %s', (movie))
    db.qt('INSERT INTO quote_pairs (group_id, movie_name, movie_title, quote_1, quote_2, cleaned) VALUES(%s, %s, %s, %s, %s, %s)', (1, movie, movie.title(), unidecode.unidecode(quote[0]), unidecode.unidecode(quote[1]), 1))