from lxml.html import parse
import re, time, random, urllib, urllib2, json

BING_APP_ID = 'D922B026428E58D0B1B38C3CB94E227B999D6F3B'

def get_bing(query_string):
  sleep_time = 1 * random.random()
  print "Sleeping for %f..." % sleep_time
  time.sleep(sleep_time)
  
  if len(query_string) > 200:
    print "This quote was too long: %s" % query_string
    return (0, [])
  
  query = urllib.quote_plus(query_string)
  opener = urllib2.build_opener()
  fil = opener.open('http://api.search.live.net/json.aspx?appid=%s&query=%s&sources=web' % (BING_APP_ID, query))
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