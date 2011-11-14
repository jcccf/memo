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
DISTANCE = 20 # How far away from the positive quote to search (in both directions)
PAIRS_PER_QUOTE = 1 # None for all

#
# FUNCTION DEFINITIONS
#

def print_pairs(movie_pairs):
  '''Print out all positive and negative pairs'''
  for movie_name, pairs in movie_pairs.iteritems():
    print movie_name
    for pos, neglist in pairs:
      print '\t%s: %s / %s' % (pos[3], unidecode.unidecode(pos[4]), pos[5])
      for neg in neglist:
        print '\t\t%s / %s' % (unidecode.unidecode(neg[4]), neg[5])

def get_pairs(min_results, distance, pairs_per_quote):
  '''For each movie that exists, get all quote pairs and'''
  '''select some threshold c above which pos quotes have to be'''
  pos_quotes = MFile.pickle_load_mac('../data/pn2/poslinesdict2.newdata.pickle')
  pos_quotes = MQuote.clean_positive_quotes(pos_quotes)
  # print pos_quotes
  movie_pairs = {}
  for script_filename in MFile.glob_filenames('../data/scripts/db/*.bing.sqlite'):
    movie_name = MQuote.clean_movie_title(script_filename.split('.',1)[0])
    if movie_name in pos_quotes:    
      mdbq = MDb.MDbQuotes('../data/scripts/db/%s' % script_filename)
      mdbq.set_positive_quotes(pos_quotes[movie_name], min_results=min_results)
      movie_pairs[movie_name] = mdbq.get_pos_neg_pairs(distance=distance, found_limit=pairs_per_quote, matcher='match_character_and_constant_quote_length')
  return movie_pairs

#
# ACTUAL CODE
#

# print "Varying Distance"
# #for i in [10]:
# for i in [10, 20, 30, 40, 50, 100]:
#   jvals = []
#   for j in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50]:
#   #for j in [10]:
#     movie_pairs = get_pairs(j, i, PAIRS_PER_QUOTE)
#     jvals.append(sum([len(pairs) for m, pairs in movie_pairs.iteritems()]))
#   stringy = "%d" % i
#   for j in jvals:
#     stringy += ", %d" % j
#   print stringy

movie_pairs = get_pairs(MIN_RESULTS, DISTANCE, PAIRS_PER_QUOTE)
print sum([len(pairs) for m, pairs in movie_pairs.iteritems()])

# # Letter Frequency
# vectorizer = MUtils.MagicVectorizer()
# for movie_name, pairs in movie_pairs.iteritems():
#   for pos, neglist in pairs:
#     vectorizer.add(MQuote.letters(unidecode.unidecode(pos[4])))
#     for neg in neglist:
#       vectorizer.add(MQuote.letters(unidecode.unidecode(neg[4])))
# vectorizer.dictionary_tofile('examples_letters_dictionary.txt')
# 
# # Generate Feature Vectors
# with open('examples_letterfreq.txt', 'w') as f:
#   for movie_name, pairs in movie_pairs.iteritems():
#     for pos, neglist in pairs:
#       f.write('%s %s\n' % ('1', vectorizer.vectorize(MQuote.letters(unidecode.unidecode(pos[4])), text=True, tfidf=True)))
#       for neg in neglist:
#         f.write('%s %s\n' % ('-1', vectorizer.vectorize(MQuote.letters(unidecode.unidecode(neg[4])), text=True, tfidf=True)))
# 
# print MSVMLight.get_cross_val_accuracy('examples_letterfreq.txt')
# 
# hyperplanes = [MSVMLight.get_separating_hyperplane('examples_letterfreq.txt.%d.tr.mod' % i)[0] for i in range(0,10)]
# avg_hyperplane = vectorizer.decode_tuples(sorted(MUtils.average_tuples(hyperplanes), key=lambda x: x[1]))
# MUtils.print_tuples(avg_hyperplane, '../data/svm_results/letters_const_length_20.txt')

# Generate Dictionary
vectorizer = MUtils.MagicVectorizer()
for movie_name, pairs in movie_pairs.iteritems():
  for pos, neglist in pairs:
    vectorizer.add(MQuote.words(unidecode.unidecode(pos[4])))
    for neg in neglist:
      vectorizer.add(MQuote.words(unidecode.unidecode(neg[4])))
vectorizer.dictionary_tofile('examples_dictionary.txt')

# Generate Feature Vectors
with open('examples_tfidf.txt', 'w') as f:
  for movie_name, pairs in movie_pairs.iteritems():
    for pos, neglist in pairs:
      f.write('%s %s\n' % ('1', vectorizer.vectorize(MQuote.words(unidecode.unidecode(pos[4])), text=True, tfidf=True)))
      for neg in neglist:
        f.write('%s %s\n' % ('-1', vectorizer.vectorize(MQuote.words(unidecode.unidecode(neg[4])), text=True, tfidf=True)))

print MSVMLight.get_cross_val_accuracy('examples_tfidf.txt')

hyperplanes = [MSVMLight.get_separating_hyperplane('examples_tfidf.txt.%d.tr.mod' % i)[0] for i in range(0,10)]
avg_hyperplane = vectorizer.decode_tuples(sorted(MUtils.average_tuples(hyperplanes), key=lambda x: x[1]))
MUtils.print_tuples(avg_hyperplane, '../data/svm_results/same_character_20.txt')