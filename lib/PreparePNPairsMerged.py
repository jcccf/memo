from misc import *
from scipy.stats import binom_test
import unidecode

DBNAME = 'memo'

def get_pairs(pos_min_char=35, pos_min_results=10, neg_max_results=10, distance=50, matcher='match_character'):
  '''For each movie that exists, get all quote pairs and'''
  '''select some threshold c above which pos quotes have to be'''
  merge_db = MDb.MMySQLDb(DBNAME)
  movie_names = merge_db.q('SELECT DISTINCT(movie_name) FROM quotes')
  merge_db.close()
  movie_pairs = {}
  for movie_name, in movie_names:
    mdb = MDb.MMySQLDbQuotes(DBNAME, movie_name)
    movie_pairs[movie_name] = mdb.get_pos_neg_pairs(pos_min_char=pos_min_char, pos_min_results=pos_min_results, neg_max_results=neg_max_results, distance=distance, matcher=matcher)
  return movie_pairs

def num_pairs(movie_pairs):
  return sum([len(pairs) for m, pairs in movie_pairs.iteritems()])

def cross_validate(movie_pairs, filename):
  # Generate Dictionary
  vectorizer = MUtils.MagicVectorizer()
  for movie_name, pairs in movie_pairs.iteritems():
    for pos, neglist in pairs:
      vectorizer.add(MQuote.words(unidecode.unidecode(pos[4])))
      for neg in neglist:
        vectorizer.add(MQuote.words(unidecode.unidecode(neg[4])))
  vectorizer.dictionary_tofile('%s_dictionary.txt' % filename)
  # Generate Feature Vectors
  with open('%s_tfidf.txt' % filename, 'w') as f:
    for movie_name, pairs in movie_pairs.iteritems():
      for pos, neglist in pairs:
        f.write('%s %s\n' % ('1', vectorizer.vectorize(MQuote.words(unidecode.unidecode(pos[4])), text=True, tfidf=True)))
        for neg in neglist:
          f.write('%s %s\n' % ('-1', vectorizer.vectorize(MQuote.words(unidecode.unidecode(neg[4])), text=True, tfidf=True)))
  return MSVMLight.get_cross_val_accuracy('%s_tfidf.txt' % filename)

def binomial_significance(num_correct, num_wrong, significance=0.05):
  b = binom_test(num_correct, num_correct+num_wrong, 0.5)
  return (b, b < significance)

# print "Varying Distance and MinChar"
# sfinal = ""
# irange = [10, 20, 30, 40, 50, 100]
# jrange = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
# sfinal = ''.join([", %d" % j for j in jrange])
# for i in irange:
#   jvals = []
#   for j in jrange:
#     print i, j
#     movie_pairs = get_pairs(pos_min_char=j, pos_min_results=0, neg_max_results=999999999, distance=i)
#     jvals.append(sum([len(pairs) for m, pairs in movie_pairs.iteritems()]))
#   sfinal += "\n%d" % i + ''.join([", %d" % j for j in jvals])  
# print sfinal

# See Accuracy for Word Length
for i in [1,3,5,7,9,11]:
  p = get_pairs(pos_min_char=35, pos_min_results=0, neg_max_results=99999999, distance=200, matcher='match_character_and_quote_length%d'%i)
  print num_pairs(p)
  c = cross_validate(p, '../data/svm_results/xlen%d'%i)
  print c
  print binomial_significance(c[1], c[2])