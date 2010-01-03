# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from datetime import datetime

from django.test import TestCase
from django.test.client import Client
from django.core.handlers.wsgi import WSGIRequest
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from tehblog.models import *

class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.
    
    Usage:
    
    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})
    
    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client
    
    Once you have a request object you can pass it to any view function, 
    just as if that view had been hooked up using a URLconf.
    
    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'REMOTE_ADDR': '127.0.0.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)

class TehBlogTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory().request()

        self.user = User.objects.create_user('user', 'user@example.com', 'userpass')

        # Categories setup
        self.category_news = Category.objects.create(
                title='News',
                slug='news',
                description='Latest News'
        )

        self.category_general = Category.objects.create(
                title='General',
                slug='general',
                description='General or random other topics'
        )

        # Entry setup
        self.entry_news = Entry.objects.create(
                title='Test News Entry',
                slug='test-news-entry',
                content='Some demo content',
                author=self.user,
                status=Entry.PUBLIC,
        )
        self.entry_news.categories.add(self.category_news)
        self.entry_news.categories.add(self.category_general)

        self.entry_demo = Entry.objects.create(
                title='Demo Entry',
                slug='demo-entry',
                content='A demo entry belonging to multiple categories',
                author=self.user,
        )
        self.entry_demo.categories.add(self.category_news)
        self.entry_demo.categories.add(self.category_general)

class CategoryTestCase(TehBlogTestCase):
    def testCategory(self):
        self.assertEquals(len(Category.objects.all()), 2)

    def testCategoryURL(self):
        """
        Testing urls and reverse lookups
        Note that we slice away the front of the urls, since this could be
        changed depending on the project urls.py

        """
        self.assertEquals(
                self.category_general.get_absolute_url()[-19:],
                'categories/general/'
        )
        # Test reverse lookups
        self.assertEquals(
                reverse('tehblog_category_entries', args=['news'])[-16:],
                'categories/news/'
        )

class EntryTestCase(TehBlogTestCase):
    def testEntry(self):
        self.assertEquals(len(Entry.objects.all()), 2)
        self.assertEquals(len(Entry.objects.public()), 1)

    def testEntryURLS(self):
        """
        Test the urls and reverse lookups for a entry.
        We have to slice away the front part of the url, since this will be
        different based on the specific project urls.py

        """
        today = datetime.now()
        day = today.strftime("%d")
        month = today.strftime("%m")
        year = today.strftime("%Y")
        test_url = '%s/%s/%s/%s/' % (year, month, day, self.entry_news.slug)

        self.assertEquals(
                self.entry_news.get_absolute_url()[-len(test_url):],
                test_url
        )
        # Test reverse lookups
        self.assertEquals(reverse(
            'tehblog_entry_view',
            args=[year, month, day, self.entry_news.slug]
        )[-len(test_url):], test_url)

    def testEntryUpdate(self):
        self.entry_demo.status = Entry.PUBLIC
        self.entry_demo.save()
        # After saved, public objects should now be 2
        self.assertEquals(len(Entry.objects.public()), 2)

    def testRelatedByEntries(self):
        entries = Entry.objects.related_by_categories(self.entry_demo)
        self.assertEquals(len(entries), 1)
        # The entry returned should not be the one passed in the query
        self.assertEquals(entries[0].slug, "test-news-entry")

        # Add one more blog category and entry that will be unique
        test_category = Category.objects.create(
                title='Extra',
                slug='extra',
                description='Extra category'
        )
        test_entry = Entry.objects.create(
                title='Extra Entry',
                slug='extra-entry',
                content='A Extra Entry',
                author=self.user,
                status=Entry.PUBLIC,
        )
        test_entry.categories.add(test_category)
        
        # ok, now test the related entries again
        entries = Entry.objects.related_by_categories(test_entry)
        self.assertEquals(len(entries), 0)
