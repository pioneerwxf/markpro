# coding=utf-8

# Python
from json import JSONDecoder, JSONEncoder
import datetime
from xlwt import *
from tempfile import *

# Plugins
from annoying.decorators import render_to

# Django
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger

# Project
from brands.models import Brand, HotKey, RankKey
from blogs.models import Blog
from mblogs.models import Mblog
from stores.models import Store, Product
from results import tasks
from settings import ADMINS, USERS

# Utils
from utils.decorators import group_check

@group_check('user')
@render_to('products/brand.html')
def product_by_brand(request):
    current = 'product'
    child = 'brand'
    if request.method == 'POST':
        sinfo = request.POST['begin_date']
        start = datetime.date(int(sinfo[:4]), int(sinfo[4:6]), int(sinfo[6:]))
        einfo = request.POST['end_date']
        real_end = datetime.date(int(einfo[:4]), int(einfo[4:6]), int(einfo[6:]))
        end = real_end + datetime.timedelta(days=1)
    else:
        start = datetime.datetime.now().date()
        real_end = start
        end = real_end + datetime.timedelta(days=1)
        
    lastest_day = start
    
    # judge the display type
    if request.GET.has_key('order'):
        order = request.GET['order']
    else:
     	order = 'sold_total'
    if request.GET.has_key('revs'):
        revs = not(eval(request.GET['revs'])) # invert string to bool
    else:
     	revs = True
    
    stores = Store.objects.all()
    
    if start == real_end:
        for store in stores:
            product_s = []
            for product in store.products.all():
                if len(product.results.all()):
                    result = product.results.order_by('-update_time')[0].result
                #result = product.results.all()[0].result
                product.review = result['review']
                product.sold_total = result['total']
                product.sold_month = result['month']
                product_s.append(product)
            store.product_s = product_s
    else:
        for store in stores:
            #store.product_s = []
            product_s = []
            for product in store.products.all():
                results = product.results.filter(update_time__range=(start, end)).order_by('update_time')
                if results:
                    product.review = (float(results[results.count()-1].result['review']) + float(results[0].result['review'])) / 2
                    product.sold_total = int(results[results.count()-1].result['total']) - int(results[0].result['total'])
                    product.sold_month = int(results[results.count()-1].result['month']) - int(results[0].result['month'])
                    #store.product_s.append(product)
                    product_s.append(product)
            store.product_s = product_s
    # begin the sort of product
    for store in stores:
        if order == 'sold_total':
            store.product_s.sort(key = lambda p: p.sold_total,reverse=revs)
        elif order == 'sold_month':
            store.product_s.sort(key = lambda p: p.sold_month,reverse=revs)
        elif order == 'review':
	        store.product_s.sort(key = lambda p: p.review,reverse=revs)
	
    title = [u'产品', u'累计销量', u'月销量', u'评价']
    
    f = Workbook()
    for store in stores:
        s = f.add_sheet(store.name)
        if start == real_end:
            s.write(0, 0, start.strftime("%Y-%m-%d"))
        else:
	        s.write(0, 0, start.strftime("%Y-%m-%d") + "-" + real_end.strftime("%Y-%m-%d"))
        for col, t in enumerate(title):
            s.write(1, col, t)
        for row, product in enumerate(store.product_s):
            s.write(row+2, 0, product.name)
            s.write(row+2, 1, product.sold_total)
            s.write(row+2, 2, product.sold_month)
            s.write(row+2, 3, product.review)
    f.save('/usr/local/share/wsgi/markpro/media/download/products_by_brand.xls')
    f.save(TemporaryFile())
    
    return {'current' : current, 'child' : child, 'stores' : stores, 'revs' : revs, 'start' : start, 'end' : real_end }

@render_to('products/date.html')
def product_by_date(request):
    current = 'product'
    child = 'date'
    # judge the product
    if request.POST.has_key('pid'):
        product_id = request.POST['pid']
    else:
        product_id = 1
    # judge the display type
    if request.GET.has_key('order'):
        order = request.GET['order']
    else:
     	order = 'update_time'
    if request.GET.has_key('revs'):
        revs = not(eval(request.GET['revs'])) # invert string to bool
    else:
     	revs = True

    # judge the pagination
    if request.GET.has_key('page'):
        page = int(request.GET['page'])
    else:
	    page = 1
    
    product = Product.objects.get(pk = product_id)
    store = Store.objects.get(pk = product.store.id)
    brand = Brand.objects.get(pk = store.brand.id)
    results = product.results.all().order_by('update_time')
    p_results = [] #make a new structure to restore the results
    for p_result in results:
        p_result.update_time = p_result.update_time
        p_result.total = p_result.result["total"]
        p_result.month = p_result.result["month"]
        p_result.review = p_result.result["review"]
        p_results.append(p_result) 
    if order == 'update_time':
        p_results.sort(key = lambda p: p.update_time,reverse=revs)
    elif order == 'total':
        p_results.sort(key = lambda p: p.total,reverse=revs)
    elif order == 'month':
        p_results.sort(key = lambda p: p.month,reverse=revs)
    elif order == 'review':
        p_results.sort(key = lambda p: p.review,reverse=revs)
    #results = product.results.all().order_by('update_time')
    #results.sort(key = lambda p: p.update_time)
    paginator=Paginator(p_results,50)
    result_list = paginator.page(page)
    page_range=paginator.page_range
    stores = Store.objects.all()
    for store in stores:
        store.product_s = store.products.all()
    
    title = [u'日期', u'累计销量', u'月销量', u'评价']
    
    f = Workbook()
    s = f.add_sheet('Data')
    s.write(0, 0, product.name)
    for col, t in enumerate(title):
        s.write(1, col, t)
    for row, result in enumerate(results):
        s.write(row+2, 0, result.update_time.strftime("%Y-%m-%d"))
        s.write(row+2, 1, result.result['total'])
        s.write(row+2, 2, result.result['month'])
        s.write(row+2, 3, result.result['review'])
    f.save('/usr/local/share/wsgi/markpro/media/download/products_by_date.xls')
    f.save(TemporaryFile())
    
    return {'current' : current, 'child' : child, 'page_range' : page_range, 'results' : result_list, 'revs' : revs, 'product' : product, 'stores' : stores, 'brand' : brand}
