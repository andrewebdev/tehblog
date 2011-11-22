# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from datetime import datetime

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from tehblog.models import *


class BlogCategoryModelTestCase(TestCase):

    def setUp(self):
        self.category1 = Category.objects.create(title='Category 1',
            slug='category-1')
        self.category2 = Category.objects.create(title='Category 2',
            slug='category-2')

    def test_model_exists(self):
        # tested via setUp()
        pass


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

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

class CategoryTestCase(BaseTestCase):
    def testCategoryURL(self):
        self.assertEquals(
                self.category_general.get_absolute_url()[-19:],
                'categories/general/'
        )
        # Test reverse lookups
        self.assertEquals(
                reverse('tehblog_category_list', args=['news'])[-16:],
                'categories/news/'
        )

class EntryTestCase(BaseTestCase):
    def testStateChange(self):
        self.assertEquals(len(Entry.objects.public()), 0)
        self.entry_news.sm_take_action('Publish')
        self.entry_news.save()
        self.assertEquals(len(Entry.objects.public()), 1)

    def testEntryView(self):
        """
        Test the urls and reverse lookups for a entry.
        We have to slice away the front part of the url, since this will be
        different based on the specific project urls.py

        """
        # First we need to publish our item
        self.entry_news.sm_take_action('Publish')
        self.entry_news.save()

        # Test the url
        today = datetime.now()
        url_args = [today.strftime("%Y"), today.strftime("%m"),
                     today.strftime("%d"), self.entry_news.slug]
        test_url = '%s/%s/%s/%s/' % (url_args[0], url_args[1], url_args[2],
                                     url_args[3])
        entry_url = self.entry_news.get_absolute_url()

        self.assertEquals(entry_url[-len(test_url):], test_url)

        # Test reverse lookups
        self.assertEquals(reverse('tehblog_entry_view',
                                  args=url_args)[-len(test_url):], test_url)

        # Make a request to the view and check the context
        c = Client()
        response = c.get(entry_url)
        self.failUnless(response.status_code == 200,
                       "Failed with status_code %s" % response.status_code)
        self.assertEquals(response.context['entry'], self.entry_news)

    def testDateViews(self):
        c = Client()
        today = datetime.now()
        date_args = [today.strftime("%Y"), today.strftime("%m"),
                     today.strftime("%d")]

        # Test the Archive View
        response = c.get(reverse('tehblog_archive_index'))
        self.failUnless(response.status_code == 200, response.content)
        self.failUnless(not response.context['object_list'])

        # Lets first publish the items so that they have publish dates
        self.entry_news.sm_take_action('Publish')
        self.entry_news.save()
        self.entry_demo.sm_take_action('Publish')
        self.entry_demo.save()

        # Test the rest of the Date Views
        response = c.get(reverse('tehblog_archive_index'))
        self.failUnless(response.status_code == 200, response.content)
        self.failUnless(len(response.context['object_list']) == 2)

        response = c.get(reverse('tehblog_archive_year', args=[date_args[0]]))
        self.failUnless(response.status_code == 200, response.content)
        self.failUnless(len(response.context['object_list']) == 2)

        response = c.get(reverse('tehblog_archive_month', args=date_args[:2]))
        self.failUnless(response.status_code == 200, response.content)
        self.failUnless(len(response.context['object_list']) == 2)

        response = c.get(reverse('tehblog_archive_day', args=date_args))
        self.failUnless(response.status_code == 200, response.content)
        self.failUnless(len(response.context['object_list']) == 2)

    def testRelatedByEntries(self):
        entries = Entry.objects.related_by_categories(self.entry_demo)
        self.assertEquals(len(entries), 0)
        self.entry_news.sm_take_action('Publish')
        self.entry_news.save()
        entries = Entry.objects.related_by_categories(self.entry_demo)
        self.assertEquals(len(entries), 1)

        # Add one more blog category and entry that will be unique
        test_category = Category.objects.create(
                title='Extra',
                slug='extra',
                description='Extra category')
        test_entry = Entry.objects.create(
                title='Extra Entry',
                slug='extra-entry',
                content='A Extra Entry',
                author=self.user)
        test_entry.categories.add(test_category)
        
        # ok, now test the related entries again
        entries = Entry.objects.related_by_categories(test_entry)
        self.assertEquals(len(entries), 0)
