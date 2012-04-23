from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'results.views.home'),
    url(r'^login$', 'results.views.login'),
    url(r'^upload$', 'results.views.upload'),
    url(r'^run$', 'results.views.run_all'),
    url(r'^products/brand$', 'stores.views.product_by_brand'),
    url(r'^products/date$', 'stores.views.product_by_date'),
    url(r'^brands/brand$', 'brands.views.brand_by_brand'),
    url(r'^brands/date$', 'brands.views.brand_by_date'),
    url(r'^weibo_auth$', 'mblogs.views.weibo_auth'),
    url(r'^weibo_callback$', 'mblogs.views.weibo_callback'),
    url(r'^weibo_refresh$', 'mblogs.views.weibo_refresh'),
    url(r'^tqq_auth$', 'mblogs.views.tqq_auth'),
    url(r'^tqq_callback$', 'mblogs.views.tqq_callback'),
)
