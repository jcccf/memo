from misc import *
import unidecode
from collections import defaultdict

#
# TODO
#
# # Do Random QueryMovieOpts for all movies


#
# PARAMETERS
#
MIN_RESULTS = 10 # Minimum results a positive quote must have
DISTANCE = 10 # How far away from the positive quote to search (in both directions)
PAIRS_PER_QUOTE = 1 # None for all

# Load Positive Quotes
pos_quotes = MFile.pickle_load_mac('../data/pn2/poslinesdict2.newdata.pickle')
pos_quotes = MQuote.clean_positive_quotes(pos_quotes)
# print pos_quotes

# For each movie that exists, get all quote pairs and
# select some threshold c above which pos quotes have to be
movie_pairs = {}
for script_filename in MFile.glob_filenames('../data/scripts/db/*.bing.sqlite'):
  movie_name = MQuote.clean_movie_title(script_filename.split('.',1)[0])
  if movie_name in pos_quotes:    
    mdbq = MDb.MDbQuotes('../data/scripts/db/%s' % script_filename)
    mdbq.set_positive_quotes(pos_quotes[movie_name], min_results=MIN_RESULTS)
    movie_pairs[movie_name] = mdbq.get_pos_neg_pairs(distance=DISTANCE, found_limit=PAIRS_PER_QUOTE)

print sum([len(pairs) for m, pairs in movie_pairs.iteritems()])

# Generate Dictionary
vectorizer = MUtils.MagicVectorizer()
for movie_name, pairs in movie_pairs.iteritems():
  for pos, neglist in pairs:
    vectorizer.add(MQuote.words(unidecode.unidecode(pos[4])))
    for neg in neglist:
      vectorizer.add(MQuote.words(unidecode.unidecode(neg[4])))

# Generate Feature Vectors
with open('examples_tfidf.txt', 'w') as f:
  for movie_name, pairs in movie_pairs.iteritems():
    for pos, neglist in pairs:
      f.write('%s %s\n' % ('1', vectorizer.vectorize(MQuote.words(unidecode.unidecode(pos[4])), text=True, tfidf=True)))
      for neg in neglist:
        f.write('%s %s\n' % ('-1', vectorizer.vectorize(MQuote.words(unidecode.unidecode(neg[4])), text=True, tfidf=True)))

print MSVMLight.get_cross_val_accuracy('examples_tfidf.txt')

# # Print out all pairs
# for movie_name, pairs in movie_pairs.iteritems():
#   print movie_name
#   for pos, neglist in pairs:
#     print '\t%s: %s / %s' % (pos[3], unidecode.unidecode(pos[4]), pos[5])
#     for neg in neglist:
#       print '\t\t%s / %s' % (unidecode.unidecode(neg[4]), neg[5])