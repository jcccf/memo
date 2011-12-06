import nltk, string, re

# Some Regexes
remove_actions = re.compile('(\[.+\])')
remove_actions_2 = re.compile('(\(.+\))')
match_left = re.compile('([^\[\(]*)([\s]*[\[|\(]{1}[^\[]*)')
match_right = re.compile('([^\]]*[\]|\)]{1}[\s]*)([^\]\)]*)')
whitespace = re.compile('([\s]+)')
authorrest = re.compile('([a-zA-Z0-9\\\(\)\-\"\'\/.,\#;\s]+):(.+)')
sentences = re.compile('([^.!?\s][^.!?]*(?:[.!?](?![\'\"]?\s|$)[^.!?]*)*[.!?]?[\'\"]?(?=\s|$))')

# Get Words between MIN and MAX_LENGTH
def filter_by_length(movie_quotes, min_len=5, max_len=7):
  filtered = []
  for movie, quotes in movie_quotes:
    for actor, quote in quotes:
      words = filter(lambda s: s not in string.punctuation, nltk.word_tokenize(quote))
      if min_len <= len(words) <= max_len:
        filtered.append((movie,actor,quote))
  print "%d quotes between %d and %d..." % (len(filtered), min_len, max_len)
  return filtered
  
def letters(sentence):
  return [c for c in sentence.lower() if c in "abcdefghijklmnopqrstuvwxyz"]

def filter_stopwords(words):
  from nltk.corpus import stopwords
  stopset = set(stopwords.words('english'))
  return [w for w in words if len(w) > 3 and w not in stopset]

def words(sentence):
  return filter(lambda s: s not in string.punctuation, nltk.word_tokenize(sentence.lower()))

def words_without_stopwords(sentence):
  return filter_stopwords(words(sentence))
  
def word_count(sentence):
  return len(filter(lambda s: s not in string.punctuation, nltk.word_tokenize(sentence)))
  
def filter_by_length_flat(quotes, index, min_len=5, max_len=7):
  filtered = []
  for q in quotes:
    words = filter(lambda s: s not in string.punctuation, nltk.word_tokenize(q[index]))
    if min_len <= len(words) <= max_len:
      filtered.append(q)
  return filtered

# Split a quote into sentences
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

# Clean a quote and remove all actions (things in brackets)
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

def remove_brackets(quote):
  return remove_actions_2.sub('', remove_actions.sub('',quote)).strip()

# Remove extra whitespace in quotes (ex. multiple spaces)
def whitespace_quote(quote):
  return whitespace.sub(' ', quote).strip()
  
# Remove all things in brackets, as well as remove parts before/after
# unbalanced brackets, and then remove extra whitespaces, then trim
def wash_quote(quote):
  quote = remove_bracketed_text(quote)
  return whitespace_quote(remove_brackets(quote.replace('*','')))
  
def remove_bracketed_text(quote):
  x = 0
  out = ''
  for c in quote:
    if c == '(':
      x += 1
    elif c == ')':
      if x == 0:
        out = ''
        x += 1
      x -= 1
    elif x == 0: # and implicitly c != ')'
      out += c
  return out
  
def clean_movie_title(title):
  title = title.replace('_', ' ')
  if ", the" in title:
    title = "the " + title.replace(", the", "")
  if ", a" in title:
    title = "a " + title.replace(", a", "")
  title = filter(lambda s: s not in string.punctuation, title)
  return title
  
def clean_positive_quotes(pos):
  pos2 = {}
  for k, v in pos.iteritems():
    vm = [x[1] for x in v]
    pos2[clean_movie_title(k)] = vm
  return pos2
  
def actor_quote(quote):
  if ':' in quote:
    actor, rest = quote.split(':', 1)
    return (actor.strip(), wash_quote(rest))
  else:
    return ('', wash_quote(quote))