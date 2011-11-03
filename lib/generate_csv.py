import re, time, random, urllib, urllib2, json, pickle, unidecode
from misc import *

#scripts = MFile.glob_filenames('../data/scripts/*.pickle')
filenames_1 = '../data/scripts/names.txt'
filenames_2 = '../data/chameleon/names_cham_uniques.txt'
pos = MFile.pickle_load_mac('../data/pn2/poslinesdict2.newdata.pickle')

file_out = '../data/quotes_csv.txt'

print pos

f_out = open(file_out, 'w')

pos2 = MQuote.clean_positive_quotes(pos)

with open(filenames_1, 'r') as f:
  for l in f:
    filename, movie_name = l.replace('\n','').split('\t\t')
    movie_name = MQuote.clean_movie_title(movie_name)
    try:
      memo = pos2[movie_name]
      print memo
      #del pos[movie_name]
      line_no = 0
      convs = pickle.load(open('../data/scripts/%s.pickle' % filename, 'r'))
      for conv in convs:
        for actor, quote in conv:
          actor = actor.replace(' ', '_')
          is_memo = 0
          if quote in memo:
            is_memo = 1
          f_out.write('%s %d %d %s %s\n' % (filename, line_no, is_memo, unidecode.unidecode(actor), unidecode.unidecode(quote)))
          line_no += 1
    except Exception as detail:
      print detail
      
with open(filenames_2, 'r') as f:
  for l in f:
    filename, movie_name = l.replace('\n','').split('\t\t')
    movie_name = MQuote.clean_movie_title(movie_name)
    try:
      memo = pos2[movie_name]
      print memo
      #del pos[movie_name]
      line_no = 0
      convs = pickle.load(open('../data/scripts/%s.pickle' % filename, 'r'))
      for conv in convs:
        for actor, quote in conv:
          actor = actor.replace(' ', '_')
          is_memo = 0
          if quote in memo:
            is_memo = 1
          f_out.write('%s %d %d %s %s' % (movie_name, line_no, is_memo, unidecode.unidecode(actor), unidecode.unidecode(quote)))
          line_no += 1
    except Exception as detail:
      print detail
      
f.close()