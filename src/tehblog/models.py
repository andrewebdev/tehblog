# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from tagging.fields import TagField
from tehblog.managers import EntryManager

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True,
        help_text="A unique, url-friendly slug based on the title"
    )
    description = models.TextField(help_text="A short description of the category")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('tehblog_category_entries', [self.slug])

class Entry(models.Model):
    DRAFT = 1
    PUBLIC = 2
    REVIEW = 3
    STATUS_CHOICES = (
        (DRAFT, 'Draft'),
        (PUBLIC, 'Public'),
        (REVIEW, 'Review'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True,
        help_text="A unique, url-friendly slug based on the title"
    )
    extract = models.TextField(
        null=True,
        blank=True,
        help_text="A small extract from the content"
    )
    content = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT)
    tags = TagField()
    categories = models.ManyToManyField(Category)

    # Meta Fields
    author = models.ForeignKey(User)
    created_date = models.DateTimeField(default=datetime.now)
    modified_date = models.DateTimeField(null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)

    # A custom manager
    objects = EntryManager()

    class Meta:
        ordering = ('-publish_date',)
        get_latest_by = 'publish_date'
        verbose_name = "Entry"
        verbose_name_plural = "Entries"

    def __unicode__(self):
        return "%s" % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('tehblog_entry_view', None, {
            'year': self.publish_date.year,
            'month': self.publish_date.month,
            'day': self.publish_date.strftime("%d"),
            'slug': self.slug,
        })

    def save(self, *args, **kwargs):
        self.modified_date = datetime.now()
        if self.publish_date == None and self.status == self.PUBLIC:
            self.publish_date = datetime.now()
        super(Entry, self).save(*args, **kwargs)
