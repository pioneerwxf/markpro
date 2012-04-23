# Python
from json import JSONDecoder, JSONEncoder
from datetime import datetime

# Plugins
from annoying.decorators import render_to

# Django
from django.shortcuts import redirect
from django.http import HttpResponse

# Project
from brands.models import Brand, HotKey, RankKey
from blogs.models import Blog
from mblogs.models import Mblog
from stores.models import Store, Product
from results import tasks
from settings import ADMINS, USERS

# Utils
from utils.decorators import group_check

@group_check('admin')
@render_to('upload.html')
def upload(request):
    if request.method == 'POST':
        if request.POST['brands']:
            brands = JSONDecoder().decode(request.POST['brands'])
        for brand in brands:
            new_brand = Brand.objects.create(brand_name = brand['brand_name'], site_url = brand['site_url'])
            for k in brand['rank_keys']:
                RankKey.objects.create(keyword = k, brand = new_brand)
            for k in brand['hot_keys']:
                HotKey.objects.create(keyword = k, brand = new_brand)
            for b in brand['blogs']:
                Blog.objects.create(type = b['type'], url = b['url'], brand = new_brand)
            for mb in brand['mblogs']:
                Mblog.objects.create(type = mb['type'], uid = mb['uid'], brand = new_brand)
            for s in brand['stores']:
                new_store = Store.objects.create(name = s['name'], type = s['type'], url = s['url'], brand = new_brand)
                for p in s['products']:
                    Product.objects.create(name = p['name'], url = p['url'], store = new_store)
            tasks.update_brand.apply_async(args = [new_brand.id], countdown = 1)
        return HttpResponse('succeed!')
    return {}

def run_all(request):
    brands = Brand.objects.all()
    for brand in brands:
        tasks.update_brand.apply_async(args = [brand.id], countdown = 1)
    return HttpResponse('running!')

@group_check('user')
@render_to('index.html')
def home(request):
    
    current = 'index'
    child = 'all_brand'
    latest_day = datetime.now().date()
    
    
    brands = Brand.objects.all()
    for brand in brands:
        if brand.results.all():
            result = brand.results.all().order_by('-update_time')[0].result
            brand.site_rank = result['pop_rank']
        
        brand.ranks = []
        brand.hots = []
        brand.blog_s = []
        brand.mblog_s = []
        brand.store_s = []
        
        for rank_key in brand.rank_keys.all():
            if rank_key.results.all():
                result = rank_key.results.all().order_by('-update_time')[0].result
                rank_key.baidu_rank = result['baidu_rank']
                rank_key.google_rank = result['google_rank']
                brand.ranks.append(rank_key)
            
            
        for hot_key in brand.hot_keys.all():
            if hot_key.results.all():
                result = hot_key.results.all().order_by('-update_time')[0].result
                hot_key.baidu_hot = result['baidu_hot']
                hot_key.google_hot = result['google_hot']
                brand.hots.append(hot_key)
        
        #for Blogs information
        for blog in brand.blogs.all():
            if blog.results.all():
                result = blog.results.all().order_by('-update_time')[0].result
                blog.grade = result['grade']
                blog.fans = result['fans']
                blog.score = result['score']
                blog.pv = result['pv']
                brand.blog_s.append(blog)
        
        for mblog in brand.mblogs.all():
            if mblog.results.all():
                result = mblog.results.all().order_by('-update_time')[0].result
                mblog.followers = result['followers']
                mblog.friends = result['friends']
                mblog.statuses = result['statuses']
                brand.mblog_s.append(mblog)
            
        #for all the store
        for store in brand.stores.all():
            if store.results.all():
                result = store.results.all().order_by('-update_time')[0].result
                store.descrip = result['descrip']
                store.service = result['service']
                store.speed = result['speed']
            store.product_num = store.products.count()
            store.total = 0
            store.month = 0
            for product in store.products.all():
                if product.results.all():
                    result = product.results.all().order_by('-update_time')[0].result
                    p_total = result["total"]
                    p_month = result["month"]
                    p_review = result["review"]
                    store.total = p_total+store.total
                    store.month = p_month+store.month
            brand.store_s.append(store)
        
    return { 'brands' : brands, 'current' : current, 'child' : child, 'date' : latest_day}

@render_to('login.html')
def login(request):
    if request.method == 'POST':
        if request.POST['username'] in ADMINS:
            if request.POST['password'] == ADMINS[request.POST['username']]:
                request.session['logined'] = True
                request.session['groups'] = ['admin', 'user']
                return redirect('/upload')
        elif request.POST['username'] in USERS:
            if request.POST['password'] == USERS[request.POST['username']]:
                request.session['logined'] = True
                request.session['groups'] = ['user']
                return redirect('/')
        return {}
    else:
        return {}
