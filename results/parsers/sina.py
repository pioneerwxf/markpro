# coding: utf-8
from pyquery import PyQuery as pq
from json import JSONDecoder
from urllib2 import urlopen
from mblogs.models import Token

class SinaBlog(object):
    
    def __init__(self, blog_url):
        self.url = blog_url
        self.run()
    
    def run(self):
        d = pq(url = self.url)
        self.grade = 0
        grade_pics = d("#comp_901_grade").find('img')
        for grade_pic in grade_pics:
            self.grade *= 10
            self.grade += int(pq(grade_pic).attr("real_src")[-5])
        self.score = int(''.join(d("#comp_901_score").text().split(',')))
        self.pv = int(''.join(d("#comp_901_pv").text().split(',')))
        self.attention = int(''.join(d("#comp_901_attention").text().split(',')))
        
        articlelist_url = pq(d(".blognavInfo").find('a')[1]).attr("href")
        dl = pq(url = articlelist_url)
        self.num_blogs = int(dl("span.title").filter(lambda i : pq(this).text()[:4] == u"全部博文").text()[6:-1])

class SinaWeibo(object):
    
    def __init__(self, uid):
        self.uid = uid
        self.run()
    
    def run(self):
        #obtain them.
        t = Token.objects.filter(type = 'sina').order_by('-id')[0]
        url = "https://api.weibo.com/2/users/show.json?access_token=%s&uid=%s" % (t.token['access_token'], self.uid)
        info = JSONDecoder().decode(urlopen(url).read())
        self.followers = info['followers_count']
        self.friends = info['friends_count']
        self.statuses = info['statuses_count']