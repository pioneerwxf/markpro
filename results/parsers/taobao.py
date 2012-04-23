from urlparse import parse_qs
from pyquery import PyQuery as pq
from urllib2 import urlopen, build_opener, HTTPCookieProcessor
from json import JSONDecoder

# Parser for taobao mall store

class TaobaoMallStore(object):
    
    def __init__(self, store_url):
        self.url = store_url
        self.run()
    
    def run(self):
        opener = build_opener(HTTPCookieProcessor())
        d = pq(opener.open(self.url).read())
        rates = d(".count")
        self.descrip = pq(rates[0]).html()
        self.service = pq(rates[1]).html()
        self.speed = pq(rates[2]).html()

# Parser for taobao mall products

class TaobaoMallProduct(object):
    
    def __init__(self, product_url):
        self.url = product_url
        self.run()
    
    def run(self):
        opener = build_opener(HTTPCookieProcessor())
        d = pq(opener.open(self.url).read())
        if d("#J_listBuyerOnView"):
            details = parse_qs(d("#J_listBuyerOnView").attr("detail:params").split(',')[0].split('?')[1])
            self.total = int(details['totalSQ'][0])
            self.month = int(details['sold_total_num'][0])
        else:
            self.total = 0
            self.month = 0
        
        reviews = JSONDecoder().decode(urlopen(d("#reviews").attr("data-reviewapi")).read().decode('gbk').split(' = ')[1])
        self.review = reviews['scoreInfo']['merchandisScore']

# Parser for normal taobao store

class TaobaoStore(object):
    
    def __init__(self, store_url):
        pass

# Parser for normal taobao products

class TaobaoProduct(object):
    
    def __init__(self, product_url):
        pass
