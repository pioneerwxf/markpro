from json import JSONDecoder
from urllib2 import urlopen
from mblogs.models import Token
from settings import TQQ_KEY, TQQ_SECRET
import oauth2 as oauth

class QQWeibo(object):
    
    def __init__(self, uid):
        self.uid = uid
        self.run()
    
    def run(self):
        t = Token.objects.filter(type = 'tqq')[0]
        consumer = oauth.Consumer(key=TQQ_KEY, secret=TQQ_SECRET)
        token = oauth.Token(key=t.token['oauth_token'], secret=t.token['oauth_token_secret'])
        client = oauth.Client(consumer, token)
        url = "http://open.t.qq.com/api/user/other_info?format=json&name=%s" % (self.uid)
        resp, content = client.request(url, "GET")
        info = JSONDecoder().decode(content)['data']
        self.followers = info['fansnum']
        self.friends = info['idolnum']
        self.statuses = info['tweetnum']