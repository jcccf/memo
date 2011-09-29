import re, time, random, urllib, urllib2, json

class Blekko:
  
  app_ids = ['2ef160a4']
  
  def __init__(self, i=0):
    self.app_id = Blekko.app_ids[i]
    
  def numeralize(self, num):
    if num[-1] == 'M':
      return int(float(num.replace('M','')) * 1000000)
    elif num[-1] == 'K':
      return int(float(num.replace('K','')) * 1000)
    elif num.isdigit():
      return int(num)
    else:
      raise ValueError("Failed to Numeralize")

  def get(self, query_string):
    sleep_time = 1.0 + 0.2 * random.random()
    print "Sleeping for %f..." % sleep_time
    time.sleep(sleep_time)
    
    if len(query_string) > 500:
      print "This quote was too long: %s" % query_string
      return (0, [])
    
    query = urllib.quote_plus(query_string.replace('/',' '))
    opener = urllib2.build_opener()
    try:
      fil = opener.open('http://blekko.com/ws/?&q=/json+%s&auth=%s' % (query,self.app_id))
    except urllib2.URLError as detail:
      print "Caught URLError: ", detail
      return None
    
    try:
      text = fil.read()
      root = json.loads(text)
    except ValueError as detail:
      print "Caught ValueError: ", detail
      print query_string
      print text
      return None
  
    try:
      top_urls = [(result['url_title'], result['url']) for result in root['RESULT']]
      num_results = self.numeralize(root['universal_total_results'])
      return (num_results, top_urls)
    except KeyError as detail:
      print "BLEKKO KEY ERROR!"
      print root
      return (0, [])
    except ValueError as detail:
      print "BLEKKO # RESULTS PARSING ERROR"
      print detail
      print root['universal_total_results']
      return (root['universal_total_results'], top_urls)
      
# b = Blekko(0)
# print b.get('"the force will be with you always" "star wars"')