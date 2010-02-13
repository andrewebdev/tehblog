# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from django.conf.urls.defaults import *
from django.views.generic import date_based

from tehblog.views import *
from tehblog.models import Entry

try:
    from tagging.views import tagged_object_list
except ImportError:
    NO_TAGS = True

tagged_objects_dict = {
    'queryset_or_model': Entry,
    'related_tags': True,
    'paginate_by': 10,
    'template_name': 'tehblog/list_view.html',
}

archive_index_dict = {
    'queryset': Entry.objects.public(),
    'date_field': 'publish_date',
    'num_latest': 10,
    'template_name': 'tehblog/list_view.html',
}

archive_year_dict = {
    'queryset': Entry.objects.public(),
    'date_field': 'publish_date',
    'make_object_list': True,
    'template_name': 'tehblog/list_view.html',
}

archive_month_dict = {
    'queryset': Entry.objects.public(),
    'date_field': 'publish_date',
    'template_name': 'tehblog/list_view.html',
    'month_format': '%m',
}

archive_day_dict = {
    'queryset': Entry.objects.public(),
    'date_field': 'publish_date',
    'template_name': 'tehblog/list_view.html',
    'month_format': '%m',
}

object_detail_dict = {
    'queryset': Entry.objects.public(),
    'date_field': 'publish_date',
    'month_format': '%m',
    'template_name': 'tehblog/entry_view.html',
    'template_object_name': 'entry',
}

urlpatterns = patterns('', 
    url(r'^$', date_based.archive_index, archive_index_dict,
        name="tehblog_landing"
    ),

    # Categories and Tags
    url(r'^categories/(?P<slug>[-\w]+)/$',
        category_entries,
        name="tehblog_category_entries"
    ),

    # Date based views
    url(r'^archive/$', date_based.archive_index, archive_index_dict,
        name="tehblog_archive_index"
    ),
    url(r'^(?P<year>\d{4})/$',
        date_based.archive_year,
        archive_year_dict,
        name="tehblog_year_view"
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        date_based.archive_month,
        archive_month_dict,
        name="tehblog_month_view"
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        date_based.archive_day,
        archive_day_dict,
        name="tehblog_day_view"
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        date_based.object_detail,
        object_detail_dict,
        name="tehblog_entry_view"
    ),
)

if not NO_TAGS:
    urlpatterns += patterns('',
        url(r'tag/(?P<tag>[^/]+)/$',
            tagged_object_list,
            tagged_objects_dict,
            name="tehblog_tag_entries"
        ),
    )
