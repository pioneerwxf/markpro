# Python
from datetime import datetime, timedelta
from json import JSONDecoder, JSONEncoder
from urllib2 import urlopen
import mechanize

# Plugins
from annoying.decorators import render_to
from celery.task import task

# Project
from brands.models import Brand, HotKey, RankKey
from blogs.models import Blog
from mblogs.models import Mblog
from stores.models import Store, Product
from results.models import Result

# Utils
from parsers.baidu import BaiduRank, BaiduHot
from parsers.alexa import AlexaRank
from parsers.google import GoogleRank, GoogleHot
from parsers.sina import SinaBlog, SinaWeibo
from parsers.taobao import TaobaoMallStore, TaobaoMallProduct
from parsers.qq import QQWeibo
from settings import WEIBO_KEY,WEIBO_CALLBACK

@task(ignore_result = True)
def get_alexa_rank(brand_id):
    brand = Brand.objects.get(pk = brand_id)
    ranker = AlexaRank(brand.site_url)
    result = { 'pop_rank' : ranker.pop_rank, 'reach_rank' : ranker.reach_rank }
    Result.objects.create(brand = brand, result = result)

@task(ignore_result = True)
def get_rankkey_rank(rk_id):
    rk = RankKey.objects.get(pk = rk_id)
    result = {}
    baidu_ranker = BaiduRank(rk.keyword, rk.brand.site_url)
    if baidu_ranker.gotcha:
        result['baidu_rank'] = baidu_ranker.rank
    else:
        result['baidu_rank'] = -1
    google_ranker = GoogleRank(rk.keyword, rk.brand.site_url)
    if google_ranker.gotcha:
        result['google_rank'] = google_ranker.rank
    else:
        result['google_rank'] = -1
    Result.objects.create(rankkey = rk, result = result)

@task(ignore_result = True)
def get_hotkey_hot(hk_id):
    hk = HotKey.objects.get(pk = hk_id)
    baidu_hoter = BaiduHot(hk.keyword)
    google_hoter = GoogleHot(hk.keyword)
    result = { 'baidu_hot' : baidu_hoter.hot, 'google_hot' : google_hoter.hot }
    Result.objects.create(hotkey = hk, result = result)

@task(ignore_result = True)
def get_blog_info(blog_id):
    blog = Blog.objects.get(pk = blog_id)
    if blog.type == "sina":
        blogger = SinaBlog(blog.url)
        result = { 'grade' : blogger.grade, 'score' : blogger.score, 'pv' : blogger.pv, 'fans' : blogger.attention }
        Result.objects.create(blog = blog, result = result)

@task(ignore_result = True)   
def get_mblog_info(mblog_id):
    mblog = Mblog.objects.get(pk = mblog_id)
    if mblog.type == "sina":
        mblogger = SinaWeibo(mblog.uid)
        result = { 'followers' : mblogger.followers, 'friends' : mblogger.friends, 'statuses' : mblogger.statuses }
        Result.objects.create(mblog = mblog, result = result)
    elif mblog.type == "tqq":
        mblogger = QQWeibo(mblog.uid)
        result = { 'followers' : mblogger.followers, 'friends' : mblogger.friends, 'statuses' : mblogger.statuses }
        Result.objects.create(mblog = mblog, result = result)

@task(ignore_result = True)
def get_store_info(store_id):
    store = Store.objects.get(pk = store_id)
    if store.type == "tmall":
        storer = TaobaoMallStore(store.url)
        result = { 'descrip' : storer.descrip, 'service' : storer.service, 'speed' : storer.speed }
        Result.objects.create(store = store, result = result)

@task(ignore_result = True)
def get_product_info(product_id):
    product = Product.objects.get(pk = product_id)
    if product.store.type == "tmall":
        producter = TaobaoMallProduct(product.url)
        result = { 'total' : producter.total, 'month' : producter.month, 'review' : producter.review }
        Result.objects.create(product = product, result = result)

@task(ignore_result = True)
def refresh_token_by_auth(brand_id): #simulate the brower to login
    if brand_id == 1:
        red_url = "https://api.weibo.com/oauth2/authorize?client_id=%s&response_type=code&redirect_uri=%s" % (WEIBO_KEY, WEIBO_CALLBACK)
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.open(red_url)  
        br.select_form(name="authZForm")
        br["userId"]="pioneerwxf@gmail.com"
        br["passwd"]="dabao326327"
        print br.submit().read()  

@task(ignore_result = True)
def update_brand(brand_id):
    # refresh the weibo token
    refresh_token_by_auth.apply_async(args = [brand_id], countdown = 1)
    
    get_alexa_rank.apply_async(args = [brand_id], countdown = 1)
    
    brand = Brand.objects.get(pk = brand_id)
    
    # update rank
    for rk in brand.rank_keys.all():
        get_rankkey_rank.apply_async(args = [rk.id], countdown = 1)
    
    # update hot
    for hk in brand.hot_keys.all():
        get_hotkey_hot.apply_async(args = [hk.id], countdown = 1)
    
    # update blog
    for b in brand.blogs.all():
        get_blog_info.apply_async(args = [b.id], countdown = 1)
    
    # update mblog
    for mb in brand.mblogs.all():
        get_mblog_info.apply_async(args = [mb.id], countdown = 1)
    
    # update store and product
    for s in brand.stores.all():
        get_store_info.apply_async(args = [s.id], countdown = 1)
        for p in s.products.all():
            get_product_info.apply_async(args = [p.id], countdown = 1)
    
    now = datetime.now()
    update_brand.apply_async(args = [ brand_id ], eta = datetime.now()+timedelta(days=1))
