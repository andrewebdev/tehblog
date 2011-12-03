# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

import warnings
from datetime import datetime

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError

from tehblog.models import *

warnings.simplefilter('always')

class BaseTestCase(TestCase):

    urls = 'tehblog.urls'

    def setUp(self):
        self.user = User.objects.create_user('user', 'user@example.com')
        self.user.set_password('secret')
        self.user.save()

        # Categories
        self.category1 = Category.objects.create(
            title='Category 1', slug='category-1',
            description='Category 1 Description')
        self.category2 = Category.objects.create(
            title='Category 2', slug='category-2',
            description='Category 2 Description')

        # Entries
        self.entry1 = Entry.objects.create(title='Entry 1', slug='entry-1',
            content='Entry 1 Content', author=self.user)

        self.entry1.categories.add(self.category1)
        self.entry1.categories.add(self.category2)
        self.entry1.save()

        self.entry2 = Entry.objects.create(title='Entry 2', slug='entry-2',
            content='Entry 2 Content', author=self.user)

        self.entry2.categories.add(self.category1)
        self.entry2.save()


class BlogCategoryModelTestCase(BaseTestCase):

    def test_model_exists(self):
        # tested via setUp()
        pass

    def test_unicode(self):
        self.assertEqual('Category 1', self.category1.__unicode__())

    def test_verbose_name_plural(self):
        self.assertEqual('Categories', Category._meta.verbose_name_plural)

    def test_absolute_url(self):
        self.assertEqual('/categories/category-1/', self.category1.get_absolute_url())


class BlogEntryModelTestCase(BaseTestCase):

    def test_model_exists(self):
        # already tested in setUp()
        pass

    def test_unicode(self):
        self.assertEqual('Entry 1', self.entry1.__unicode__())

    def test_verbose_name_plural(self):
        self.assertEqual('Entries', Entry._meta.verbose_name_plural)

    def test_slug_already_exists(self):
        with self.assertRaises(IntegrityError):
            invalid = Entry.objects.create(title='Invalid', slug='entry-1',
                author=self.user)

    def test_absolute_url_when_not_published(self):
        self.assertEqual('', self.entry1.get_absolute_url())

    def test_absolute_url_when_published(self):
        today = datetime.today()
        self.entry1.publish_date = datetime.now()
        self.assertEqual('/%s/%s/%s/entry-1/' % (
            today.strftime('%Y'), today.strftime('%m'), today.strftime('%d'),
        ), self.entry1.get_absolute_url())
            

class EntryManagerTestCase(BaseTestCase):

    def test_no_public_entries(self):
        self.assertEqual(0, Entry.objects.public().count())

    def test_public_entries(self):
        self.entry1.sm.take_action('publish')
        self.assertEqual(1, Entry.objects.public().count())

    def test_related_by_categories_published_only(self):
        self.assertEqual(0,
            Entry.objects.related_by_categories(self.entry1).count())

    def test_related_by_categories(self):
        self.entry1.sm.take_action('publish')
        self.entry2.sm.take_action('publish')

        self.assertEqual(1,
            Entry.objects.related_by_categories(self.entry1).count())


# class CategoryViewTestCase(TestCase):

#     def test_view_exists(self):
#         self.assertTrue(False)

#     def test_view_get_object(self):
#         self.assertTrue(False)

#     def test_category_in_context(self):
#         self.assertTrue(False)

#     def test_entries_in_context(self):
#         self.assertTrue(False)


# class TagViewTestCase(TestCase):

#     def test_view_exists(self):
#         self.assertTrue(False)

#     def test_entry_list_in_context(self):
#         self.assertTrue(False)

#     def test_entry_in_context(self):
#         self.assertTrue(False)

