import unidecode, re, string, pickle, nltk
from misc import *

mqs = MFile.pickle_load_mac('../data/fortest.pickle')

db = MDb.MMySQLDb('memo_turk', host='localhost', username='cf_memo')
for movie, quote in mqs.iteritems():
  res = db.qt('SELECT COUNT(*) from quote_pairs WHERE movie_name = %s AND quote_1 = %s', (movie, quote[0]))
  if res[0][0] > 0:
    db.qt('UPDATE quote_pairs SET cleaned = 1 WHERE movie_name = %s AND quote_1 = %s', (movie, quote[0]))
    db.qt('UPDATE movies SET cleaned = 1 WHERE movie_name = %s', (movie))
  else:
    pass
    # print "Inserting %s, %s, %s" % (movie, quote[0], quote[1])
    #     db.qt('INSERT INTO movies (movie_name, movie_title, is_imdb_top) VALUES(%s, %s, %s)', (movie, movie.title(), 0))
    #     db.qt('INSERT INTO quote_pairs (group_id, movie_name, movie_title, quote_1, quote_2, cleaned) VALUES(%s, %s, %s, %s, %s)', (1, movie, movie.title(), unidecode.unidecode(quote[0]), unidecode.unidecode(quote[0]), 1))