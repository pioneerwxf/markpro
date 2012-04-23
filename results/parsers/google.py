import re
from urlparse import urlparse
from xgoogle.search import GoogleSearch, SearchError

def mk_nice_domain(domain):
    """
    convert domain into a nicer one (eg. www3.google.com into google.com)
    """
    domain = re.sub("^www(\d+)?\.", "", domain)
    # add more here
    return domain

class GoogleRank(object):
    
    def __init__(self, rank_key, site_url):
        self.key = rank_key.encode('utf-8')
        self.url = site_url
        self.rank = 0
        self.gotcha = False
        self.run()
    
    def run(self):
        try:
            gs = GoogleSearch(self.key)
            while not self.gotcha:
                results = gs.get_results()
                for res in results:
                    self.rank += 1
                    if res.url == self.url:
                        self.gotcha = True
                        break
                if gs.page >= 30:
                    break
        except SearchError:
            pass
        

class GoogleHot():
    
    def __init__(self, hot_key):
        self.key = hot_key.encode('utf-8')
        self.run()
    
    def run(self):
        try:
            gs = GoogleSearch(self.key)
            self.hot = gs.num_results
        except SearchError:
            self.hot = -1
