# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from django.conf.urls.defaults import *
from django.views.generic import *

from tagging.views import tagged_object_list
from tehblog.models import Category, Entry

urlpatterns = patterns('', 
    # Categories and Tags
    url(r'^categories/(?P<slug>[-\w]+)/$',
        DetailView.as_view(
            slug_field='slug',
            template_name='tehblog/list_view.html',
            model=Category,
            context_object_name="category",
        ), name="tehblog_category_list"),

    # Date based views
    url(r'^$', ArchiveIndexView.as_view(
        queryset=Entry.objects.public(),
        date_field='publish_date',
        template_name="tehblog/list_view.html",
        context_object_name="entries",
        allow_empty=True,
    ), name="tehblog_archive_index"),

    url(r'^(?P<year>\d{4})/$', YearArchiveView.as_view(
        queryset=Entry.objects.public(),
        date_field='publish_date',
        make_object_list=True,
        template_name='tehblog/list_view.html',
        allow_empty=True,
    ), name="tehblog_archive_year"),
                       
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', MonthArchiveView.as_view(
        queryset=Entry.objects.public(),
        date_field='publish_date',
        month_format='%m',
        template_name='tehblog/list_view.html',
        allow_empty=True,
    ), name="tehblog_archive_month"),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        DayArchiveView.as_view(
            queryset=Entry.objects.public(),
            date_field='publish_date',
            month_format='%m',
            template_name='tehblog/list_view.html',
            allow_empty=True,
        ), name="tehblog_archive_day"),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        DateDetailView.as_view(
            queryset=Entry.objects.public(),
            date_field='publish_date',
            month_format='%m',
            template_name='tehblog/entry_view.html',
            context_object_name='entry',
        ), name="tehblog_entry_view"),

    url(r'tag/(?P<tag>[^/]+)/$', tagged_object_list, {
            'queryset_or_model': Entry,
            'related_tags': True,
            'paginate_by': 10,
            'template_name': 'tehblog/list_view.html',
        }, name="tehblog_tag_entries"),
)
