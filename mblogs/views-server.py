# Python
from json import JSONDecoder
from urllib2 import urlopen
import oauth2 as oauth
import urlparse
import urllib

# Django
from django.shortcuts import redirect
from django.http import HttpResponse

# Project
from mblogs.models import Token
from settings import WEIBO_KEY, WEIBO_SECRET, TQQ_KEY, TQQ_SECRET

# Utils
from utils.decorators import group_check

# Works only on local host

# Sina Weibo auth
@group_check('admin')
def weibo_auth(request):
    red_url = "https://api.weibo.com/oauth2/authorize?client_id=%s&response_type=code&redirect_uri=%s" % (WEIBO_KEY, "http://markpro.iso11.com/weibo_callback")
    return redirect(red_url)

def weibo_callback(request):
    code = request.GET['code']
    token_url = "https://api.weibo.com/oauth2/access_token?client_id=%s&client_secret=%s&grant_type=authorization_code&redirect_uri=%s&code=%s" % (WEIBO_KEY, WEIBO_SECRET, "http://markpro.iso11.com/weibo_callback", code)
    info = JSONDecoder().decode(urlopen(token_url, "").read())
    Token.objects.create(type="sina", token = info)
    return HttpResponse('done.')

# unused right now
def weibo_refresh(request):
    t = Token.objects.filter(type = 'sina').order_by('-id')[0]
    ref_url = 'https://api.weibo.com/oauth2/access_token?refresh_token=%s' % (t.token['refresh_token'])
    t.token = JSONDecoder().decode(urlopen(ref_url, "").read())
    t.save(force_update=True)

# QQ auth
@group_check('admin')
def tqq_auth(request):
    request_token_url = 'https://open.t.qq.com/cgi-bin/request_token?'
    authorize_url = 'https://open.t.qq.com/cgi-bin/authorize'
    
    consumer = oauth.Consumer(TQQ_KEY, TQQ_SECRET)
    client = oauth.Client(consumer)
    body = urllib.urlencode(dict(oauth_callback="http://markpro.iso11.com/tqq_callback"))
    resp, content = client.request(request_token_url, "POST", body=body)
    request_token = dict(urlparse.parse_qsl(content))
    request.session['rt_ot'] = request_token['oauth_token']
    request.session['rt_ots'] = request_token['oauth_token_secret']
    
    red_url = "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
    return redirect(red_url)

def tqq_callback(request):
    oauth_verifier = request.GET['oauth_verifier']
    access_token_url = 'https://open.t.qq.com/cgi-bin/access_token'
    
    consumer = oauth.Consumer(TQQ_KEY, TQQ_SECRET)
    token = oauth.Token(request.session['rt_ot'], request.session['rt_ots'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)
    
    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    Token.objects.create(type="tqq", token = access_token)
    return HttpResponse('done.')