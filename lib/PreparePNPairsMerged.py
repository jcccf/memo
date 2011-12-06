from misc import *
from scipy.stats import binom_test
import unidecode, pickle

DBNAME = 'memo'

def get_pairs(imdb_memorability=True, pos_min_char=35, pos_min_wc=0, pos_min_results=10, pos_max_results=100000, neg_max_results=10, distance=50, matcher='match_character'):
  '''For each movie that exists, get all quote pairs and'''
  '''select some threshold c above which pos quotes have to be'''
  merge_db = MDb.MMySQLDb(DBNAME)
  movie_names = merge_db.q('SELECT DISTINCT(movie_name) FROM quotes')
  merge_db.close()
  movie_pairs = {}
  for movie_name, in movie_names:
    mdb = MDb.MMySQLDbQuotes(DBNAME, movie_name)
    movie_pairs[movie_name] = mdb.get_pos_neg_pairs(imdb_memorability=imdb_memorability, pos_min_char=pos_min_char, pos_min_wc=pos_min_wc, pos_min_results=pos_min_results, pos_max_results=pos_max_results, neg_max_results=neg_max_results, distance=distance, matcher=matcher)
  return movie_pairs

def num_pairs(movie_pairs):
  return sum([len(pairs) for m, pairs in movie_pairs.iteritems()])

def print_pairs(movie_pairs, filename):
  '''Print out all positive and negative pairs'''
  with open(filename, 'w') as f:
    for movie_name, pairs in movie_pairs.iteritems():
      print movie_name
      for pos, neglist in pairs:
        f.write('\t%s: %s / %s\n' % (pos[3], unidecode.unidecode(pos[4]), pos[5]))
        for neg in neglist:
          f.write('\t\t%s / %s\n' % (unidecode.unidecode(neg[4]), neg[5]))

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

# print "Varying Distance and Min WC"
# sfinal = ""
# irange = [10, 20, 30, 40, 50, 100]
# #jrange = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
# jrange = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
# sfinal = ''.join([", %d" % j for j in jrange])
# for i in irange:
#   jvals = []
#   for j in jrange:
#     print i, j
#     movie_pairs = get_pairs(pos_min_char=0, pos_min_wc=j, pos_min_results=10, neg_max_results=10, distance=i)
#     jvals.append(sum([len(pairs) for m, pairs in movie_pairs.iteritems()]))
#   sfinal += "\n%d" % i + ''.join([", %d" % j for j in jvals])  
# print sfinal

# pairs = get_pairs(pos_min_char=0, pos_min_wc=10, pos_min_results=0, neg_max_results=999999999, distance=50)
# pickle.dump(pairs, open('../data/svm_pairs/pairs_imdb.pickle', 'w'))
# pairs = pickle.load(open('../data/svm_pairs/pairs.pickle', 'r'))
# print cross_validate(pairs, '../data/svm_results/testy')

# pairs = get_pairs(imdb_memorability=False, pos_min_char=0, pos_min_wc=6, pos_min_results=101, pos_max_results=100000, neg_max_results=10, distance=50)
# pickle.dump(pairs, open('../data/svm_pairs/pairs_bing_51_5.pickle', 'w'))
# 
# pairs = get_pairs(imdb_memorability=False, pos_min_char=0, pos_min_wc=6, pos_min_results=21, pos_max_results=100000, neg_max_results=10, distance=50)
# pickle.dump(pairs, open('../data/svm_pairs/pairs_bing_21_5.pickle', 'w'))


## TODO
## 0. train separately with/without stopwords
## 1. use same dictionary
## 2. train on bing, test on memo, vice versa

def train_test(train_set, validation_set, filename):
  
  # Eliminate duplicates in train_set and validation_set
  pairset = {}
  for movie_name, pairs in validation_set.iteritems():
    for pos, neglist in pairs:
      pairset[pos] = True
  train_set_new = {}
  for movie_name, pairs in train_set.iteritems():
    newpairs = [p for p in pairs if p[0] not in pairset]
    train_set_new[movie_name] = newpairs
  train_set = train_set_new
  
  # Generate Dictionary
  vectorizer = MUtils.MagicVectorizer()
  for movie_pairs in [train_set, validation_set]:
    for movie_name, pairs in movie_pairs.iteritems():
      for pos, neglist in pairs:
        vectorizer.add(MQuote.words(unidecode.unidecode(pos[4])))
        for neg in neglist:
          vectorizer.add(MQuote.words(unidecode.unidecode(neg[4])))
  vectorizer.dictionary_tofile('%s_dictionary.txt' % filename)
  # Generate Feature Vectors
  for movie_pairs, name in [(train_set, 'train'), (validation_set, 'val')]:
    with open('%s_%s_tfidf.txt' % (filename, name), 'w') as f:
      for movie_name, pairs in movie_pairs.iteritems():
        for pos, neglist in pairs:
          f.write('%s %s\n' % ('1', vectorizer.vectorize(MQuote.words(unidecode.unidecode(pos[4])), text=True, tfidf=True)))
          for neg in neglist:
            f.write('%s %s\n' % ('-1', vectorizer.vectorize(MQuote.words(unidecode.unidecode(neg[4])), text=True, tfidf=True)))
  
  MSVMLight.learn('%s_%s_tfidf.txt' % (filename, 'train'), '%s_%s_tfidf.txt' % (filename, 'mod'))
  return MSVMLight.classify('%s_%s_tfidf.txt' % (filename, 'val'), '%s_%s_tfidf.txt' % (filename, 'mod'), '%s_%s_tfidf.txt' % (filename, 'class'))

imdb_pairs = pickle.load(open('../data/svm_pairs/pairs_imdb.pickle', 'r'))
bing_pairs = pickle.load(open('../data/svm_pairs/pairs_bing.pickle', 'r'))
# print train_test(bing_pairs, imdb_pairs, 'imdb_bing')

print cross_validate(imdb_pairs, '../data/svm_results/testy')

# # See Accuracy for Word Length
# for i in [1,3,5,7,9,11]:
#   p = get_pairs(pos_min_char=35, pos_min_results=11, neg_max_results=10, distance=50, matcher='match_character_and_quote_length%d'%i)
#   print num_pairs(p)
#   c = cross_validate(p, '../data/svm_results/xlen%d'%i)
#   print c, binomial_significance(c[1], c[2])