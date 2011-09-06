# PrepareQuotes
# Take quotes from pickle and parse them into an array of (movie, quotes) pairs,
# where quotes are (actor, quote) pairs

import re, pickle, os.path

# Code to convert from windows to mac file since pickle complains
if not os.path.exists('../data/title_to_quotes_mac.pickle'):
  file = open('../data/title_to_quotes.pickle','r')
  movies = file.read().replace('\r\n','\n')
  f = open('../data/title_to_quotes_mac.pickle','w')
  f.write(movies)
  f.close()

title_to_quotes=pickle.load(open('../data/title_to_quotes_mac.pickle','r'))

remove_actions = re.compile('(\[[a-zA-Z0-9:.,\'\"\s!]+\])')
match_left = re.compile('([a-zA-Z0-9:.,\'\"!\s]*)\w*([\s]*\[[a-zA-Z0-9:.,!\s]+)')
match_right = re.compile('([a-zA-Z0-9:.,\'\"!\s]+\])\w*([a-zA-Z0-9:.,\'\"!\s]*)')
whitespace = re.compile('([\s]+)')

def clean_quote(quote):
  new_quote = remove_actions.sub('', quote)
  if match_left.match(new_quote) :
    return match_left.match(new_quote).group(1) + " "
  elif match_right.match(new_quote) :
    return match_right.match(new_quote).group(2) + " "
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
      parts = quote[i].split(':')
      if len(parts) > 1 :
        if len(last_quote) > 0 and len(last_quote.strip()) > 0 :
          aq.append((last_actor, whitespace_quote(last_quote)))
        last_actor, last_quote = '', ''
        last_actor = parts[0]
        last_quote = clean_quote(parts[1])
      else :
        last_quote += clean_quote(parts[0])
    if len(last_quote) > 0 and len(last_quote.strip()) > 0 :
      aq.append((last_actor, whitespace_quote(last_quote)))
  mquotes.append((movie, set(aq)))

pickle.dump(mquotes, open('../data/title_to_quotes_parsed.pickle','w'))