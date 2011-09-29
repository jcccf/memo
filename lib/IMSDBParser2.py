import re, time, random, urllib, urllib2, json, pickle
from QuoteFunctions import *

# NAME = 'star_wars_a_new_hope'
# URL = 'http://www.imsdb.com/scripts/Star-Wars-A-New-Hope.html'
# NAME = 'revenge_of_the_sith'
# URL = 'http://www.imsdb.com/scripts/Star-Wars-Revenge-of-the-Sith.html'
# NAME = 'empire_strikes_back'
# URL = 'http://www.imsdb.com/scripts/Star-Wars-The-Empire-Strikes-Back.html'
# NAME = 'phantom_menace'
# URL = 'http://www.imsdb.com/scripts/Star-Wars-The-Phantom-Menace.html'
NAME = 'incredibles' # THIS ONE
URL = 'http://www.imsdb.com/scripts/Incredibles,-The.html'
# NAME = 'it_happened_one_night'
# URL = 'http://www.imsdb.com/scripts/It-Happened-One-Night.html'
# NAME = 'into_the_wild'
# URL = 'http://www.imsdb.com/scripts/Into-the-Wild.html'
# NAME = 'a_few_good_men'
# URL = 'http://www.imsdb.com/scripts/A-Few-Good-Men.html'
# NAME = 'a_serious_man'
# URL = 'http://www.imsdb.com/scripts/A-Serious-Man.html'
# NAME = None
# URL = 'http://www.imsdb.com/scripts/Above-the-Law.html'

if not NAME:
  NAME = URL.split('/')[-1].split('.')[0].lower().replace('-','_')

opener = urllib2.build_opener()
try:
  fil = opener.open(URL)
except urllib2.URLError as detail:
  print "Caught URLError: ", detail

text = fil.read()

def num_quotes(convs):
  l = 0
  for c in convs:
    l += len(c)
  return l

def preformatted_text(text, initial_blank_line=False):
  text = text.split('<td class=scrtext>')
  if len(text) != 2:
    print "Error: Can't Find Start of Script"
    return None
  text = text[1].split('</table>', 1)
  if len(text) != 2:
    print "Error: Can't Find End of Script"
    return None
  text = text[0]
  
  # Remove HTML Tags
  text = re.compile('<.*?>').sub('', text)
  # Split into lines
  lines = text.split('\n')
  
  def is_capitalized(text):
    return text.isupper()
    
  def is_empty(text):
    return len(text.replace('*','').strip()) == 0
    
  def space_in_front(text):
    text = text.replace('*','')
    i = 0
    while text[i] == ' ' and i < len(text):
      i += 1
    return i
  
  convs, conv, quote, actor, mode, qsp = [], [], '', '', 'find_title', 0
  end_at_next_title, first_blank, check_action = False, True, False
  ibl = initial_blank_line
  for i in range(0, len(lines)):
    l = lines[i]
    if i+1 < len(lines):
      l_next = lines[i+1]
    else:
      l_next = ''
    
    if mode == 'find_title':
      # ACTOR \n Quote
      if is_capitalized(l):
        actor = wash_quote(l)
        first_blank = True
        mode = 'find_quote'
      # ACTOR: Quote
      elif len(l.split(':',1)) == 2:
        la, lq = l.split(':',1)
        if is_capitalized(la):
          actor = wash_quote(la)
          first_blank = True
          quote, qsp = wash_quote(lq), space_in_front(l)
          mode = 'end_quote'
      # End Conversation
      else:
        if len(conv) > 0:
          convs.append(conv)
          conv = []
        
    elif mode == 'find_quote':
      if is_empty(l):
        if ibl and first_blank:
            first_blank = False
        else:
          mode = 'find_title'
          # End Conversation
          if len(conv) > 0:
            convs.append(conv)
            conv = []
      elif is_capitalized(l):
        actor = wash_quote(l)
        first_blank = True
      elif len(wash_quote(l)) == 0:
        first_blank = True
        pass
      else:
        quote, qsp = wash_quote(l), space_in_front(l)
        mode = 'end_quote'
        
    elif mode == 'end_quote':
      if is_empty(l):
        # Allow the first blank line to happen
        if ibl and first_blank:
          first_blank = False
        # If the next line is an action, allow an additional blank line
        elif ibl and (not is_empty(l_next) and len(wash_quote(l_next)) == 0):
          first_blank = True
        else:
          conv.append((actor,quote))
          mode = 'find_title'
          # End Conversation
          if end_at_next_title:
            convs.append(conv)
            conv = []
            end_at_next_title = False
      # ACTOR \n Quote
      elif is_capitalized(l):
        conv.append((actor,quote))
        actor = wash_quote(l)
        first_blank = True
        mode = 'find_quote'
      # ACTOR: Quote
      elif len(l.split(':',1)) == 2:
        la, lq = l.split(':',1)
        if is_capitalized(la):
          conv.append((actor,quote))
          actor = wash_quote(la)
          first_blank = True
          quote, qsp = wash_quote(lq), space_in_front(l)
          mode = 'end_quote'
        elif abs(space_in_front(l) - qsp) < 2:
          quote += ' ' + wash_quote(l)
          qsp = space_in_front(l)
      elif len(wash_quote(l)) == 0:
        first_blank = True
      elif abs(space_in_front(l) - qsp) < 2:
        quote += ' ' + wash_quote(l)
        qsp = space_in_front(l)
      else:
        end_at_next_title = True
  
  print text
  
  return convs

# Assume no blank lines between actors and quotes
out = preformatted_text(text)
# Fall-back to allowing initial blank lines between actors and quotes
if num_quotes(out) < 100:
  out = preformatted_text(text, initial_blank_line=True)

if len(out) == 0:
  raise Exception("Failed to parse anything intelligible out")

with open('../data/scripts/%s.txt' % NAME, 'w') as f:
  for conv in out:
    f.write("\n---\n\n")
    for actor,quote in conv:
      f.write(actor + ":\n" + quote + "\n")

pickle.dump(out, open('../data/scripts/%s.pickle' % NAME, 'w'))