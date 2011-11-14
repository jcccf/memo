from lxml.html import parse
import re, time, random, urllib, urllib2, json

app_ids = ['D922B026428E58D0B1B38C3CB94E227B999D6F3B','5DA1F9DA8B46C5656204D4110B13130F8F0391E1','26D582D305C6F76D6BABEEA234F43E4C2997E043']

def get_bing(query_string, app_id=0):
  sleep_time = 0.5 * random.random()
  print "Sleeping for %f..." % sleep_time
  time.sleep(sleep_time)
  
  if len(query_string) > 500:
    print "This quote was too long: %s" % query_string
    return (0, [])
  
  query = urllib.quote_plus(query_string)
  opener = urllib2.build_opener()
  try:
    fil = opener.open('http://api.search.live.net/json.aspx?appid=%s&query=%s&sources=web' % (app_ids[app_id], query))
  except urllib2.URLError as detail:
    print "Caught URLError: ", detail
    return None
    
  root = json.loads(fil.read())

  try:
    num_results = root['SearchResponse']['Web']['Total']
    top_urls = [(result['Title'], result['Url']) for result in root['SearchResponse']['Web']['Results']]
    return (num_results, top_urls)
  except KeyError as detail:
    print root
    if root['SearchResponse']['Query']:
      return (0, [])
    else:
      print 'Error', detail
      return None
      
class Bing:
  
  app_ids = ['D922B026428E58D0B1B38C3CB94E227B999D6F3B','5DA1F9DA8B46C5656204D4110B13130F8F0391E1','26D582D305C6F76D6BABEEA234F43E4C2997E043']
  
  def __init__(self, i=0):
    self.app_id = Bing.app_ids[i]

  def get(self, query_string):
    query_string = query_string.replace('/', '')
    
    sleep_time = 0.5 * random.random()
    print "Sleeping for %f..." % sleep_time
    time.sleep(sleep_time)
    
    if len(query_string) > 500:
      print "This quote was too long: %s" % query_string
      return (0, [])
    
    query = urllib.quote_plus(query_string)
    opener = urllib2.build_opener()
    try:
      fil = opener.open('http://api.search.live.net/json.aspx?appid=%s&query=%s&sources=web' % (self.app_id, query))
    except urllib2.URLError as detail:
      # print "Query: ", query
      # print "QueryString: ", query_string
      # print 'http://api.search.live.net/json.aspx?appid=%s&query=%s&sources=web' % (self.app_id, query)
      print "Caught URLError: ", detail
      return None
      
    root = json.loads(fil.read())
  
    try:
      num_results = root['SearchResponse']['Web']['Total']
      top_urls = [(result['Title'], result['Url']) for result in root['SearchResponse']['Web']['Results']]
      return (num_results, top_urls)
    except KeyError as detail:
      print root
      if root['SearchResponse']['Query']:
        return (0, [])
      else:
        print 'Error', detail
        return None