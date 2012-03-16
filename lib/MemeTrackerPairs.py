from misc import *
import pickle

#
# HELPER METHODS
#

def get_clusters_and_words(filename, output_filename):
  clusters, last_cluster, cluster_name = {}, [] , ""
  with open(filename, 'r') as f:
    for i,l in enumerate(f):
      if i < 6:
        continue
      # if i >= 1000000:
      #   break
      parts = l.split('\t')
      if len(parts) > 3 and len(parts[0]) != 0: # A Cluster
        # print l
        # print parts[0]
        if len(last_cluster) > 0:
          clusters[cluster_name] = last_cluster
        last_cluster = []
        cluster_name = parts[2]
      elif len(parts) > 3 and len(parts[1]) != 0: # A Phrase
        #print l
        #print parts[1]
        last_cluster.append((int(parts[1]),int(parts[2]),parts[3]))
  if len(last_cluster) > 0:
    clusters[cluster_name] = last_cluster
  pickle.dump(clusters, open(output_filename, 'w'))

def short_fn(frequency, unique_urls, phrase):
  if unique_urls >= 100 and 4 < MQuote.word_count(phrase) < 8:
    '''Decides whether something is a positive example'''
    return True
  else:
    return False

def long_fn(frequency, unique_urls, phrase):
  '''Decides whether something is a "long" phrase'''
  if MQuote.word_count(phrase) >= 10:
    return True
  else:
    return False
    
def comp_fn(frequency, unique_urls, phrase, frequency2, unique_urls2, phrase2):
  '''This function decides whether a candidate phrase (2) is a negative example for a given positive one'''
  if unique_urls2 <= 10 and (-1 <= MQuote.word_count(phrase) - MQuote.word_count(phrase2) <= 1) and not phrase2 in phrase and not phrase in phrase2:
    return True
  else:
    return False

def get_phrase_pairs(phrase_file, out_file = 'pairs.txt', short_function=short_fn, long_function=long_fn, comp_function=comp_fn):
  clusters = pickle.load(open(phrase_file, 'r'))
  pairs = {} # Stores all the pairs later in terms of (memorable phrase -> set of unmemorable phrases)
  for cluster_phrase, phrases in clusters.iteritems():
    # Get prospective short and long phrases
    shorts, longs = [], []
    for phrase in phrases:
      if short_function(*phrase):
        shorts.append(phrase)
      elif long_function(*phrase):
        longs.append(phrase)
    # Look for matches between short and long phrases
    for short in shorts:
      for longue in longs:
        if short[2] in longue[2]:
          # Find all other phrases in longue
          others = []
          for phrase in phrases:
            if phrase[2] in longue[2] and comp_function(*(short + phrase)):
              others.append(phrase)
          # Add all found pairs to the pairs hash
          if len(others) > 0:
            if not short in pairs:
              pairs[short] = set()
            for other in others:
              pairs[short].add(other)
          #print short[2], longue[2], others
  # Write out to file
  with open(out_file, 'w') as f:
    for pos, neglist in pairs.iteritems():
      f.write('%d\t%s\n' % (pos[1], pos[2]))
      for neg in neglist:
        f.write('\t%d\t%s\n' % (neg[1], neg[2]))
  
  # Count # of Positives, and Total # of Pairs
  print len(pairs)
  count = 0
  for pos, neglist in pairs.iteritems():
    count += len(neglist)
  print count

#
# THINGS TO RUN
#

# You can also modify the short_fn, long_fn, and comp_fn methods above to adjust the parameters.

MEME_FILE = '/Volumes/My Passport/Downloads/memetracker/clust-qt08080902w3mfq5.txt' # Original from the website
CLUS_FILE = 'data/memetracker/clusters.pickle' # Intermediate file
PAIR_FILE = 'pairs.txt' # Output pairs

# 1. GENERATE A SMALLER FILE USING ORIGINAL MEMETRACKER DATASET  
get_clusters_and_words(MEME_FILE, CLUS_FILE)

# 2. GENERATE PAIRS
get_phrase_pairs(CLUS_FILE, PAIR_FILE)