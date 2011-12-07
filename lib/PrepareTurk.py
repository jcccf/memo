import unidecode, re, string, pickle, nltk
from misc import *

def strip_for_cmp(n):
  n = unidecode.unidecode(n).replace('\n','').lower()
  n = re.sub(r'\s*\([0-9]+\)', '', n)
  n = re.sub('[%s]' % re.escape(string.punctuation), '', n)
  n = n.replace('the ', '')
  return n

names = []
with open('../data/names/imdb_top_250.txt', 'r') as f:
  for l in f:
    names.append(strip_for_cmp(l))

# Load Shorties and Longies
lpairs = pickle.load(open('../data/svm_pairs/pairs_bing_long_1.pickle', 'r'))
spairs = pickle.load(open('../data/svm_pairs/pairs_bing_short_1.pickle', 'r'))

stemp = {}
for movie, pairs in spairs.iteritems():
  stemp[movie] = []
  for pos, neglist in pairs:
    if len(neglist) >= 5:
      stemp[movie].append((pos, neglist))
spairs = stemp

# Get Intersection of Sufficient Quotes
valid_movies = []
for movie_name in spairs.keys():
  if len(spairs[movie_name]) >= 1 and movie_name in lpairs and len(lpairs[movie_name]) >= 2:
    valid_movies.append(movie_name)
print '# of intersecting movies:', len(valid_movies)

# print valid_movies

# Get IMDB Top 250 Matches
imdb_matches = []
for movie in valid_movies:
  if strip_for_cmp(movie) in names:
    imdb_matches.append(movie)
print '# of top imdb matches:', len(imdb_matches)

# Import into MySQL
db = MDb.MMySQLDb('memo_turk', host='localhost', username='cf_memo')
db.q('TRUNCATE TABLE movies')
db.q('TRUNCATE TABLE quote_pairs')
db.q('TRUNCATE TABLE quote_short_term')
POS_INDEX = 7 # IMDB_QUOTE instead of regular script quote
NEG_INDEX = 4
for movie in valid_movies:
  # insert into movies
  is_imdb_top = 1 if movie in imdb_matches else 0
  db.qt('INSERT INTO movies (movie_name, movie_title, is_imdb_top) VALUES(%s, %s, %s)', (movie, movie.title(), is_imdb_top))
  
  # insert into quote_pairs
  i = 0
  for pos, neglist in lpairs[movie]:
    if i < 2:
      db.qt('INSERT INTO quote_pairs (group_id, movie_name, movie_title, quote_1, quote_2) VALUES(%s, %s, %s, %s, %s)', (1, movie, movie.title(), unidecode.unidecode(pos[POS_INDEX]), unidecode.unidecode(neglist[0][NEG_INDEX])))
      i += 1  
  
  # insert into quote_short_term
  pos, neglist = spairs[movie][0]
  db.qt('INSERT INTO quote_short_term (movie_name, movie_title, quote_type, quote) VALUES(%s, %s, %s, %s)', (movie, movie.title(), 'positive', unidecode.unidecode(pos[POS_INDEX])))
  db.qt('INSERT INTO quote_short_term (movie_name, movie_title, quote_type, quote) VALUES(%s, %s, %s, %s)', (movie, movie.title(), 'negative', unidecode.unidecode(neglist[0][NEG_INDEX])))
  for i in range(1,5):
    db.qt('INSERT INTO quote_short_term (movie_name, movie_title, quote_type, quote) VALUES(%s, %s, %s, %s)', (movie, movie.title(), 'negative_rest', unidecode.unidecode(neglist[i][NEG_INDEX])))
