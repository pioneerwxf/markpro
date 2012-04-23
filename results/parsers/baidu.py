import urllib ,urllib2 
import re
from pyquery import PyQuery as pq
            
class BaiduRank(object):
    
    def __init__(self, rank_key, site_url):
        self.key = rank_key
        self.url = site_url
        self.rank = 0
        self.gotcha = False
        self.run()
    
    def run(self):
        while not self.gotcha:
            url= "http://www.baidu.com/s?pn=%s&usm=3&" % (self.rank)
            values = {
                "wd"  : self.key.encode('gbk','ignore'),
            }
            data = urllib.urlencode(values)
            search_url = url + data
            d = pq(urllib2.urlopen(search_url).read().decode('gbk','ignore'))
            for x in d(".t"):
                self.rank += 1
                if pq(x.find("a")).attr("href") == self.url:
                    self.gotcha = True
                    break
            if self.rank >= 500:
                break

class BaiduHot(object):
    
    def __init__(self, hot_key):
        self.key = hot_key
        self.run()
    
    def run(self):
        url= "http://www.baidu.com/s?usm=3&"
        values = {
            "wd"  : self.key.encode('gbk','ignore'),
        }
        data = urllib.urlencode(values)
        search_url = url + data
        d = pq(urllib2.urlopen(search_url).read().decode('gbk','ignore'))
        self.hot = int(''.join(d(".nums").text()[7:-1].split(',')))
