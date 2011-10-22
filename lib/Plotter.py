import sqlite3, pickle, unidecode
import matplotlib.pyplot as plt
import matplotlib
from plot import *
from misc import *

NAMES_FILE = 'names_top_20'
SCRIPTDB_DIRECTORY = '../data/scripts/db'
IMAGES_DIRECTORY = '../data/scripts/db/images'

def normalize(b, scale=100):
  b_max = float(max(b)) / scale
  return [x/b_max for x in b]

def plot_and_list(folder, movie_name, a):
  n, bins, _ = DistributionPlot.histogram_plot('%s/%s/%s.eps' % (IMAGES_DIRECTORY, folder, movie_name), a, bins=2000, normed=0)
  bins = ['%10.0f' % x for x in bins]
  with open('%s/%s/%s.txt' % (IMAGES_DIRECTORY, folder, movie_name), 'w') as f:
    for bin, freq in zip(bins,n):
      f.write('%s %d\n' % (bin,freq))  

# Filter by number of words?

def dist_movie(movie_name, movie_name2, random_name):
  db = MDb.MDb('%s/%s.bing.sqlite' % (SCRIPTDB_DIRECTORY, movie_name))
  
  db_r = MDb.MDb('%s/%s.bing.sqlite' % (SCRIPTDB_DIRECTORY, random_name))
  randoms = db_r.qt('SELECT result FROM quotes WHERE movie=? AND (query_type=\'movie_title\' OR query_type=\'movie_title_2\')', [movie_name2])
  randoms = [r[0] for r in randoms]
  random_count = float(sum(randoms))/len(randoms)
  random_range = (random_count * 0.85, random_count * 1.15)

  # Get # of results, store plain in a, conjuncted with movie title in b
  results = db.q('SELECT q2.result, q1.quote FROM quotes AS q1, quotes AS q2  WHERE q1.movie = q2.movie AND q1.quote = q2.quote AND q1.query_type=\'plain\' AND q2.query_type=\'movie_title\' AND q1.quote_type=\'full\' AND q2.quote_type=\'full\'')
  b, quotes = [[x[i] for x in results if x[0] < random_range[0] or x[0] > random_range[1]] for i in (0,1)]
  #print quotes

  #plot_and_list('plain', movie_name, a)
  plot_and_list('movie_name', movie_name, b)  

  db.close()
  db_r.close()
  
  #a = [y for y in a if y > 10]
  # b = [y for y in b if y > 10]
  return (b, quotes)
  
def plot_all_movies(name, xs, quotes_s, labels, ylim=(0,1000), xlabel='# of results returned', ylabel='# of queries that return that # of results'):
  n, bins, _ = DistributionPlot.histogram_plot('%s/%s_%s.eps' % (IMAGES_DIRECTORY, NAMES_FILE, name), xs, bins=200, normed=0, color=BasicPlot.colors(len(xs)), label=labels, ylim=ylim, xlabel=xlabel, ylabel=ylabel)
  xs_norm = [normalize(x) for x in xs]
  n, bins, _ = DistributionPlot.histogram_plot('%s/%s_%s_normx.eps' % (IMAGES_DIRECTORY, NAMES_FILE, name), xs_norm, bins=200, normed=0, color=BasicPlot.colors(len(xs)), label=labels, ylim=ylim, xlabel=xlabel, ylabel=ylabel)
  n, bins, _ = DistributionPlot.histogram_plot('%s/%s_%s_normxy.eps' % (IMAGES_DIRECTORY, NAMES_FILE, name), xs_norm, bins=200, normed=1, color=BasicPlot.colors(len(xs)), label=labels, ylim=(0,1), xlabel=xlabel, ylabel=ylabel)
  bins_sorted = sorted(bins, reverse=True)
  with open('%s/%s_%s_norm.txt' % (IMAGES_DIRECTORY, NAMES_FILE, name), 'w') as f:
    for xes, quotes, label in zip(xs_norm, quotes_s, labels):
      f.write(label+'\n')
      i = 0
      f.write('\t\t%f\n' % bins_sorted[i])
      xq = sorted(zip(xes,quotes), key=lambda z:z[0], reverse=True)
      for x, q in xq:
        while i < len(bins_sorted)-1 and x <= bins_sorted[i+1]:
          f.write('\t\t%f\n' % bins_sorted[i+1])
          i += 1
        f.write('\t\t\t\t'+unidecode.unidecode(q)+'\n')
      
i = 0
b_s, quotes_s, labels = [], [], []
with open('../data/scripts/%s.txt' % NAMES_FILE, 'r') as f:
  for l in f:
    movie_name, movie_n2 = l.replace('\n','').split('\t\t')
    b, quotes = dist_movie(movie_name, movie_n2, NAMES_FILE)
    # a_s.append(a)
    b_s.append(b)
    quotes_s.append(quotes)
    labels.append(movie_name)
    i += 1

plot_all_movies('reg', b_s, quotes_s, labels)
b_s, quotes_s = [[[x[i] for x in zip(b,quotes) if MQuote.word_count(x[1]) > 1] for b, quotes in zip(b_s,quotes_s)] for i in (0,1)]
plot_all_movies('w1-', b_s, quotes_s, labels)
b_s, quotes_s = [[[x[i] for x in zip(b,quotes) if 5 <= MQuote.word_count(x[1]) <= 7] for b, quotes in zip(b_s,quotes_s)] for i in (0,1)]
plot_all_movies('w57', b_s, quotes_s, labels)