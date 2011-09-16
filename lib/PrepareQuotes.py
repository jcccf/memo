# PrepareQuotes
# Take quotes from pickle and parse them into an array of (movie, quotes) pairs,
# where quotes are (actor, quote) pairs

import re, pickle, os.path
from unidecode import unidecode
from QuoteFunctions import *
from FileFunctions import *

# FILENAME = 'quotes_parsed'
FILENAME = 'negquotes_parsed'
original_file = '../data/negativelinesdict.pickle'

parsed_file = '../data/%s.pickle' % FILENAME
parsed_file_single = '../data/%s_single.pickle' % FILENAME
parsed_file_sentences = '../data/%s_sentences.pickle' % FILENAME
parsed_file_single_sentences = '../data/%s_single_sentenes.pickle' % FILENAME

# original_file = '../data/negativelinesdict.pickle'
# parsed_file = '../data/negativelinesdict_parsed.pickle'
# parsed_file_single = '../data/negativelinesdict_parsed_single.pickle'

title_to_quotes=pickle_load_mac(original_file)

mquotes, msinglequotes = [], []
mquotesfull, msinglequotesfull = [], []

for movie, quotes in title_to_quotes.iteritems():
  print "Parsing movie %s..." % movie
  aq, asq, fq, fsq = [], [], [], []
  for quote in quotes:
    if type(quote) == list:
      last_actor, last_quote = '', ''
      for i in range(0, len(quote)):
        quote[i] = unidecode(quote[i])
        parts = authorrest.match(quote[i])
        if parts:
          if len(last_quote.strip()) > 0 :
            subquotes = split_into_sentences(last_quote)
            for subquote in subquotes:
              aq.append((last_actor, subquote))
              if len(quote) == 1:
                asq.append((last_actor, subquote))
            fq.append((last_actor, whitespace_quote(last_quote)))
            if len(quote) == 1:
              fsq.append((last_actor, whitespace_quote(last_quote)))
          last_actor, last_quote = '', ''
          last_actor = whitespace_quote(parts.group(1))
          last_quote = clean_quote(parts.group(2))
        else:
          last_quote += clean_quote(quote[i])
      if len(last_quote.strip()) > 0:
        subquotes = split_into_sentences(last_quote)
        for subquote in subquotes:
          aq.append((last_actor, subquote))
          if len(quote) == 1:
            asq.append((last_actor, subquote))
        fq.append((last_actor, whitespace_quote(last_quote)))
        if len(quote) == 1:
          fsq.append((last_actor, whitespace_quote(last_quote)))
    elif type(quote) == str:
      quote = unidecode(quote)
      parts = authorrest.match(quote)
      if parts:
        subquotes = split_into_sentences(clean_quote(parts.group(2)))
        for subquote in subquotes:
          aq.append((whitespace_quote(parts.group(1)), subquote))
        fq.append((whitespace_quote(parts.group(1)), whitespace_quote(parts.group(2))))
      else:
        subquotes = split_into_sentences(clean_quote(quote))
        print subquotes
        for subquote in subquotes:
          aq.append(('', subquote))
        fq.append(('', whitespace_quote(quote)))
  mquotes.append((movie, set(aq)))
  msinglequotes.append((movie, set(asq)))
  mquotesfull.append((movie, set(fq)))
  msinglequotesfull.append((movie, set(fsq)))

pickle.dump(mquotes, open(parsed_file_sentences,'w'))
pickle.dump(msinglequotes, open(parsed_file_single_sentences,'w'))
pickle.dump(mquotesfull, open(parsed_file,'w'))
pickle.dump(msinglequotesfull, open(parsed_file_single,'w'))