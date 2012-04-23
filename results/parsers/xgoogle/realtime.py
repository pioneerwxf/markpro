#!/usr/bin/python
# encoding: utf-8
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# http://www.catonmat.net/blog/python-library-for-google-search/
#
# Code is licensed under MIT license.
#

import re
from datetime import datetime
import time
import urllib
from htmlentitydefs import name2codepoint
from BeautifulSoup import BeautifulSoup

from search import SearchError
from browser import Browser, BrowserError

class RealtimeSearchError(SearchError):
    """
    Base class for Google Realtime Search exceptions.
    """
    pass

class CaptchaError(SearchError):
    pass

class RealtimeResult:
    def __init__(self, screen_name, status, timestamp, id, keywords=None):
        self.screen_name = screen_name
        self.status = status
        self.timestamp = timestamp
        self.id = id
        self.keywords = keywords

    def __str__(self):
        return 'Realtime Result:\n\t%s\n\t%s\n\t%s' % (self.screen_name, self.status, self.timestamp)

class RealtimeSearch(object):
    BASE_URL = "http://www.google.%(tld)s"
    SEARCH_URL = "http://www.google.%(tld)s/search?hl=%(lang)s&q=%(query)s&btnG=Google+Search&tbs=mbl:1"
    DAY = 86400

    def __init__(self, query, random_agent=False, debug=False, lang="en", tld="com", older=None, interval=43200):
        self.query = query
        self.debug = debug
        self.browser = Browser(debug=debug)
        self.eor = False # end of results
        self._page = 0
        self._last_search_url = None
        self._lang = lang
        self._tld = tld
        self._interval = interval
        
        self.older = older
        
        if random_agent:
            self.browser.set_random_user_agent()

    @property
    def last_search_url(self):
        return self._last_search_url

    def _get_page(self):
        return self._page

    def _set_page(self, page):
        self._page = page

    page = property(_get_page, _set_page)

    def _set_older(self, older):
        self._older = older 
        
    def _get_older(self):
        return self._older
    
    older = property(_get_older, _set_older)

    def get_results(self):
        """ Gets a page of results """
        if self.eor:
            return []
        
        page = self._get_results_page()

        # Check captcha
        if self._check_captcha(page):
            raise CaptchaError, "Found Captcha"

        results = self._extract_results(page)
        self._page += 1
        
        # Get older link
        self.older = self._extract_older_link(page)
        if not self.older:
            raise RealtimeSearchError, "Could not compute older results' link"

        return results

    def _check_captcha(self, page):
        form = page.find('form', {'action':'Captcha'})
        return form != None

    def _maybe_raise(self, cls, *arg):
        if self.debug:
            raise cls(*arg)

    def _get_results_page(self):
        if not self.older:
            url = RealtimeSearch.SEARCH_URL
            safe_url = [url % { 'query': urllib.quote_plus(self.query),
                                'tld': self._tld,
                                'lang' : self._lang }]
            safe_url = "".join(safe_url)
            self.older = safe_url            
        else:
            safe_url = self.older

        self._last_search_url = safe_url
        try:
            page = self.browser.get_page(safe_url)
        except BrowserError, e:
            raise RealtimeSearchError, "Failed getting %s: %s" % (e.url, e.error)
        return BeautifulSoup(page)

    def _extract_results(self, soup):
        ret_res = []
        results_wrapper = soup.find('div', {'id':'ires'})
        if not results_wrapper:
            return ret_res
        results = results_wrapper.findAll('li', {'class': 'g s'})
        for result in results:
            eres = self._extract_result(result)
            if eres:
                ret_res.append(eres)
        return ret_res

    def _extract_result(self, result):
        try:
            screen_name, status, keywords = self._extract_status(result)
            timestamp = self._extract_status_timestamp(result)
            id = self._extract_status_id(result)
        except ValueError:
            return None

        if not screen_name or not status or not timestamp:
            return None
        return RealtimeResult(screen_name, status, timestamp, id, keywords)

    def _extract_status(self, result):
        div = result.find('div', {'class':None, 'style':None})
        div_text = div.findAll(text=True)
        screen_name = self._html_unescape(div_text.pop(0))
        status = self._html_unescape(''.join(div_text))
        ems = div.findAll('em')
        keywords = []
        for em in ems:
            keywords.append(self._html_unescape(''.join(em.findAll(text=True))))
        return screen_name, status, keywords

    def _extract_status_timestamp(self, result):
        span = result.find('span', {'class':'f rtdm'})
        delta = span.find('div', {'class':'rtdelta'})
        if delta:
            timestamp = time.time() - int(delta.find(text=True))
            timestamp = time.gmtime(timestamp)
        else:
            timestamp = span.find(text=True)
            # Timestamp example:
            # Mar 29, 2011 2:17:05 AM
            # %b  %d, %Y  %I:%M:%S %p
            timestamp = time.strptime(timestamp.strip(), '%b %d, %Y %I:%M:%S %p')

        return datetime.fromtimestamp(time.mktime(timestamp))

    def _extract_status_id(self, result):
        link = result.find('a', {'href':re.compile('/status/')})
        if not link:
            return None
        id = re.findall('status/([\d]*)', link['href'])
        if not id:
            return None
        return long(id[0])

    def _extract_older_link(self, soup):
        url = RealtimeSearch.BASE_URL 
        safe_url = url % {'tld':self._tld}

        # Try to get the older link
        links = soup.find('div', {'class':'s'})
        if links:
            links = links.findAll('a')            
            if links and links[0]['href']:
                return ''.join([safe_url, links[0]['href']])
                
        # Change the interval to get older tweets
        return self._change_interval(self.older)
    
    def _change_interval(self, current_url):
        regex = 'mbl_hs:(?P<hs>[\d]*),mbl_he:(?P<he>[\d]*),mbl_rs:(?P<rs>[\d]*),mbl_re:(?P<re>[\d]*),'
        matchobj = re.search(regex, current_url)
        
        if not matchobj:
            return None

        int_hs, int_he, int_rs, int_re = matchobj.group('hs', 'he', 'rs', 're')
        
        # Set new interval
#        int_re_n = int_rs
    
        int_re_n = str(int(int_re) - self._interval)
        int_rs_n = str(int(int_rs) - self._interval)
        
        int_hs_n = str(int(int_hs) - self._interval)
        int_he_n = str(int(int_he) - self._interval)
        
#        if int_rs_n < int_hs:
#            int_hs_n = str(int(int_hs) - RealtimeSearch.DAY)
#            int_he_n = str(int(int_he) - RealtimeSearch.DAY)
        
        # Replace the parameters in the url
        current_url = re.sub(int_hs, int_hs_n, current_url)
        current_url = re.sub(int_he, int_he_n, current_url)
        current_url = re.sub(int_rs, int_rs_n, current_url)
        current_url = re.sub(int_re, int_re_n, current_url)
        
        return current_url
        
    
    def _html_unescape(self, str):
        def entity_replacer(m):
            entity = m.group(1)
            if entity in name2codepoint:
                return unichr(name2codepoint[entity])
            else:
                return m.group(0)

        def ascii_replacer(m):
            cp = int(m.group(1))
            if cp <= 255:
                return unichr(cp)
            else:
                return m.group(0)

        s = re.sub(r'&#(\d+);', ascii_replacer, str, re.U)
        return re.sub(r'&([^;]+);', entity_replacer, s, re.U)
