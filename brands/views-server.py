# coding=utf-8

# Python
from json import JSONDecoder
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
from results.models import Result
from results import tasks
from settings import ADMINS, USERS

# Utils
from utils.decorators import group_check

@group_check('user')
@render_to('brands/brand.html')
def brand_by_brand(request):
    current = 'brand'
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
    
    brands = Brand.objects.all()
    for brand in brands:
        brand.rank = -1
        results = brand.results.filter(update_time__range=(start, end))
        if results:
            x = 0
            num = 0
            for r in results:
                num += 1
                x += int(r.result['pop_rank'])
            x /= num
            brand.rank = x
        
        brand.ranks = []
        brand.hots = []
        brand.blog_s = []
        brand.mblog_s = []
        
        #for rank and hot
        for rank_key in brand.rank_keys.all():
            results = rank_key.results.filter(update_time__range=(start, end))
            if results:
                x = Result(rankkey = rank_key, update_time = start, result = {'baidu_rank' : 0, 'google_rank' : 0})
                b_num = 0
                g_num = 0
                for r in results:
                    if r.result['baidu_rank'] != -1:
                        x.result['baidu_rank'] += r.result['baidu_rank']
                        b_num += 1
                    if r.result['google_rank'] != -1:
                        x.result['google_rank'] += r.result['google_rank']
                        g_num += 1
                if b_num == 0:
                    x.result['baidu_rank'] = -1
                else:
                    x.result['baidu_rank'] /= b_num
                if g_num == 0:
                    x.result['google_rank'] = -1
                else:
                    x.result['google_rank'] /= g_num
                brand.ranks.append(x)

        for hot_key in brand.hot_keys.all():
            results = hot_key.results.filter(update_time__range=(start, end))
            if results:
                x = Result(hotkey = hot_key, update_time = start, result = {'baidu_hot' : 0, 'google_hot' : 0})
                b_num = 0
                g_num = 0
                for r in results:
                    if r.result['baidu_hot'] != -1:
                        x.result['baidu_hot'] += r.result['baidu_hot']
                        b_num += 1
                    if r.result['google_hot'] != -1:
                        x.result['google_hot'] += r.result['google_hot']
                        g_num += 1
                if b_num == 0:
                    x.result['baidu_hot'] = -1
                else:
                    x.result['baidu_hot'] /= b_num
                if g_num == 0:
                    x.result['google_hot'] = -1
                else:
                    x.result['google_hot'] /= g_num
                brand.hots.append(x)
        # for miniblogs
        for mblog in brand.mblogs.all():
            results = mblog.results.filter(update_time__range=(start, end))
            if results:
                x = Result(mblog = mblog, update_time = start, result = { 'followers' : 0, 'friends' : 0, 'statuses' : 0})
                num = 0
                for r in results:
                    num += 1
                    x.result['followers'] += int(r.result['followers'])
                    x.result['friends'] += int(r.result['friends'])
                    x.result['statuses'] += int(r.result['statuses'])
                x.result['followers'] /= num
                x.result['friends'] /= num
                x.result['statuses'] /= num
                brand.mblog_s.append(x)
        #for Blogs information
        for blog in brand.blogs.all():
            results = blog.results.filter(update_time__range=(start, end))
            if results:
                x = Result(blog = blog, update_time = start, result = { 'grade' : 0, 'score' : 0, 'pv' : 0, 'fans': 0})
                num = 0
                for r in results:
                    num += 1
                    x.result['grade'] += int(r.result['grade'])
                    x.result['score'] += int(r.result['score'])
                    x.result['pv'] += int(r.result['pv'])
                    x.result['fans'] += int(r.result['fans'])
                x.result['grade'] /= num
                x.result['score'] /= num
                x.result['pv'] /= num
                x.result['fans'] /= num
                brand.blog_s.append(x)
    
    title = [u'品牌', u'排名(谷/百)', u'热度(谷/百)', u'微博(粉/关/博)', u'博客(等/粉/分/pv)', u'网站排名']
    
    f = Workbook()
    s = f.add_sheet('Data')
    if start == real_end:
        s.write(0, 0, start.strftime("%Y-%m-%d"))
    else:
        s.write(0, 0, start.strftime("%Y-%m-%d") + "-" + real_end.strftime("%Y-%m-%d"))
    for col, t in enumerate(title):
        s.write(1, col, t)
    for row, brand in enumerate(brands):
        s.write(row+2, 0, brand.brand_name)
        str = ''
        for rank in brand.ranks:
            str += '%s(%s/%s)\n' % (rank.rankkey.keyword, rank.result["google_rank"], rank.result["baidu_rank"])
        s.write(row+2, 1, str)
        str = ''
        for hot in brand.hots:
            str += '%s(%s/%s)\n' % (hot.hotkey.keyword, hot.result["google_hot"], hot.result["baidu_hot"])
        s.write(row+2, 2, str)
        str = ''
        for mblog in brand.mblog_s:
            str += '%s(%s/%s/%s)\n' % (mblog.mblog.type, mblog.result["followers"], mblog.result["friends"], mblog.result["statuses"])
        s.write(row+2, 3, str)
        str = ''
        for blog in brand.blog_s:
            str += '%s(%s/%s/%s/%s)\n' % (blog.blog.type, blog.result["grade"], blog.result["fans"], blog.result["score"], blog.result["pv"])
        s.write(row+2, 4, str)
        s.write(row+2, 5, brand.rank)
    f.save('/usr/local/share/wsgi/markpro/media/download/brands_by_brand.xls')
    f.save(TemporaryFile())
    
    return { 'brands' : brands, 'current' : current, 'child' : child, 'start' : start, 'end': real_end}
    
@render_to('brands/date.html')
def brand_by_date(request):
    current = 'brand'
    child = 'date'
    # judge the brand and date
    if request.POST.has_key('bid'):
        brand = Brand.objects.get(pk=request.POST['bid'])
    else:
        brand = Brand.objects.all()[0]
    
    # judge the pagination
    if request.GET.has_key('page'):
        page = int(request.GET['page'])
    else:
	    page = 1
	
    brands = Brand.objects.all()
    datas = []
    exist_date = []
    
    for rk in brand.rank_keys.all():
        for r in rk.results.order_by('-update_time'):
            if r.update_time.date() in exist_date:
                datas[exist_date.index(r.update_time.date())]["ranks"][ r.rankkey.keyword ] = r.result
            else:
                exist_date.append( r.update_time.date() )
                datas.append( { "date" : r.update_time.date(), "ranks" : { r.rankkey.keyword : r.result } } )
    
    for hk in brand.hot_keys.all():
        for r in hk.results.all():
            if datas[exist_date.index(r.update_time.date())].has_key("hots"):
                datas[exist_date.index(r.update_time.date())]["hots"][ r.hotkey.keyword ] = r.result
            else:
                datas[exist_date.index(r.update_time.date())]["hots"] = { r.hotkey.keyword : r.result }
    
    for b in brand.blogs.all():
        for r in b.results.all():
            if datas[exist_date.index(r.update_time.date())].has_key("blogs"):
                datas[exist_date.index(r.update_time.date())]["blogs"][ r.blog.type ] = r.result
            else:
                datas[exist_date.index(r.update_time.date())]["blogs"] = { r.blog.type : r.result }
    
    for mb in brand.mblogs.all():
        for r in mb.results.all():
            if datas[exist_date.index(r.update_time.date())].has_key("mblogs"):
                datas[exist_date.index(r.update_time.date())]["mblogs"][ r.mblog.type ] = r.result
            else:
                datas[exist_date.index(r.update_time.date())]["mblogs"] = { r.mblog.type : r.result }
    
    for r in brand.results.all():
        datas[exist_date.index(r.update_time.date())]["rank"] = r.result['pop_rank']
    #datas.sort()
    paginator=Paginator(datas,50)
    data_list = paginator.page(page)
    page_range=paginator.page_range
    #datas.sort(key = lambda p: p.date)    
    title = [u'日期', u'排名(谷/百)', u'热度(谷/百)', u'微博(粉/关/博)', u'博客(等/粉/分/pv)', u'网站排名']
    
    f = Workbook()
    s = f.add_sheet('Data')
    
    for col, t in enumerate(title):
        s.write(0, col, t)
    for row, data in enumerate(datas):
        s.write(row+1, 0, data["date"].strftime("%Y-%m-%d"))
        str = ''
        for k,v in data["ranks"].items():
            str += '%s(%s/%s)\n' % (k, v["google_rank"], v["baidu_rank"])
        s.write(row+1, 1, str)
        str = ''
        for k,v in data["hots"].items():
            str += '%s(%s/%s)\n' % (k, v["google_hot"], v["baidu_hot"])
        s.write(row+1, 2, str)
        if "mblogs" in data.keys():
            str = ''
            for k,v in data["mblogs"].items():
                str += '%s(%s/%s/%s)\n' % (k, v["followers"], v["friends"], v["statuses"])
            s.write(row+1, 3, str)
        if "blogs" in data.keys():
            str = ''
            for k,v in data["blogs"].items():
                str += '%s(%s/%s/%s/%s)\n' % (k, v["grade"], v["fans"], v["score"], v["pv"])
        s.write(row+1, 4, str)
        if "rank" in data.keys():
		    str = ''
		    str = data["rank"]
        s.write(row+1, 5, str)
    f.save('/usr/local/share/wsgi/markpro/media/download/brands_by_date.xls')
    f.save(TemporaryFile())
    
    return {'current' : current, 'child' : child, 'page_range' : page_range, 'datas' : data_list, 'brand' : brand, 'brands' : brands }
