# PrepareQuotes
# Take quotes from pickle and parse them into an array of (movie, quotes) pairs,
# where quotes are (actor, quote) pairs

import re, pickle, os.path
from unidecode import unidecode

# Code to convert from windows to mac file since pickle complains
if not os.path.exists('../data/title_to_quotes_mac.pickle'):
  file = open('../data/title_to_quotes.pickle','r')
  movies = file.read().replace('\r\n','\n')
  f = open('../data/title_to_quotes_mac.pickle','w')
  f.write(movies)
  f.close()

title_to_quotes=pickle.load(open('../data/title_to_quotes_mac.pickle','r'))

# Some Regexes
remove_actions = re.compile('(\[.+\])')
match_left = re.compile('([^\[])*([\s]*\[[^\[]*)')
match_right = re.compile('([^\]]*\])([\s]*[^\]]*)*')
whitespace = re.compile('([\s]+)')
authorrest = re.compile('([a-zA-Z0-9\\\(\)\-\"\'\/.,\#;\s]+):(.+)')
sentences = re.compile('([^.!?\s][^.!?]*(?:[.!?](?![\'\"]?\s|$)[^.!?]*)*[.!?]?[\'\"]?(?=\s|$))')

def split_into_sentences(quote):
  # Split everything into sentences, but...
  subquotes = sentences.split(quote)
  subquotes = filter(lambda s:len(s.strip())>0, subquotes)
  # Now look for Mr. and Mrs. and join them back
  new_squotes = []
  i = 0
  last_quote = ''
  for subquote in subquotes:
    s1, s2, s3 = subquote.rpartition(' ')
    if s1 and ('Mr.' in s3 or 'Mrs.' in s3):
      last_quote += subquote + ' '
    else:
      last_quote += subquote
      new_squotes.append(last_quote)
      last_quote = ''
  new_squotes.append(last_quote)
  return filter(None, new_squotes)

def clean_quote(quote):
  new_quote = remove_actions.sub('', quote)
  if match_left.match(new_quote) :
    txt = match_left.match(new_quote).group(1)
    if txt:
      return txt + " "
    else:
      return " "
  elif match_right.match(new_quote) :
    txt = match_right.match(new_quote).group(2)
    if txt:
      return txt + " "
    else:
      return " "
  else :
    return new_quote + " "
    
def whitespace_quote(quote):
  return whitespace.sub(' ', quote).strip()

mquotes = []
for movie, quotes in title_to_quotes.iteritems():
  print "Parsing movie %s..." % movie
  aq = []
  for quote in quotes:
    last_actor, last_quote = '', ''
    for i in range(0, len(quote)):
      quote[i] = unidecode(quote[i])
      parts = authorrest.match(quote[i])
      if parts :
        if len(last_quote.strip()) > 0 :
          subquotes = split_into_sentences(last_quote)
          for subquote in subquotes:
            aq.append((last_actor, subquote))
        last_actor, last_quote = '', ''
        last_actor = whitespace_quote(parts.group(1))
        last_quote = clean_quote(parts.group(2))
      else :
        last_quote += clean_quote(quote[i])
    if len(last_quote.strip()) > 0 :
      subquotes = split_into_sentences(last_quote)
      for subquote in subquotes:
        aq.append((last_actor, subquote))
  mquotes.append((movie, set(aq)))

pickle.dump(mquotes, open('../data/title_to_quotes_parsed.pickle','w'))