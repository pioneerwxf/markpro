import re
import urllib2

class AlexaRank(object):
    def __init__(self, site_url):
        self.url = site_url
        self.pop_rank = -1
        self.reach_rank = -1
        self.run()

    def run(self):
        data = urllib2.urlopen('http://data.alexa.com/data?cli=10&dat=snbamz&url=%s' % (self.url)).read()
    
        reach_rank = re.findall("REACH[^\d]*(\d+)", data)
        if reach_rank: self.reach_rank = reach_rank[0]
        else: self.reach_rank = -1
    
        popularity_rank = re.findall("POPULARITY[^\d]*(\d+)", data)
        if popularity_rank: self.pop_rank = popularity_rank[0]
        else: self.pop_rank = -1