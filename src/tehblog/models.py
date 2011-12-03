# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from tagging.fields import TagField
from ostinato.statemachine import StateMachine
from ostinato.statemachine.models import StateMachineField, DefaultStateMachine

from tehblog.managers import EntryManager


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,
        help_text="A unique, url-friendly slug based on the title")
    description = models.TextField(
        help_text="A short description of the category")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('tehblog_category_list', [self.slug])


class Entry(models.Model, StateMachine):
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True,
        help_text="A unique, url-friendly slug based on the title")
    extract = models.TextField(
        null=True, blank=True,
        help_text="A small extract from the content")
    content = models.TextField()
    tags = TagField(help_text='Separate tags with spaces,'
                              'put quotes around multiple-word tags.')
    categories = models.ManyToManyField(Category)

    # Publication Fields
    author = models.ForeignKey(User)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    allow_comments = models.BooleanField(default=True)

    # Managers and Statemachine related fields
    objects = EntryManager()

    sm = StateMachineField(DefaultStateMachine)
    _statemachine = generic.GenericRelation(DefaultStateMachine)

    class Meta:
        ordering = ('-publish_date', '-created_date')
        get_latest_by = 'publish_date'
        verbose_name = "Entry"
        verbose_name_plural = "Entries"

    def __unicode__(self):
        return "%s" % self.title

    def state(self):
        return self.sm.state
        
    @models.permalink
    def get_url(self, *args):
        return args

    def get_absolute_url(self):
        if self.publish_date:
            return self.get_url(*('tehblog_entry_view', None, {
                'year': self.publish_date.year,
                'month': self.publish_date.strftime("%m"),
                'day': self.publish_date.strftime("%d"),
                'slug': self.slug,
            }))
        else:
            # Should we raise a 404 or message that entry is not published?
            return ''
