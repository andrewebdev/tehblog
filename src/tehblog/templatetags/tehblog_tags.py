# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from django import template

from tehblog.models import Entry, Category 
from tagging.models import Tag, TaggedItem

register = template.Library()

@register.inclusion_tag('tehblog/category_list_tag.html')
def category_list(count=None):
    return {
        'category_list': Category.objects.all().exclude(
            entry__status__in=[1, 3],
        )[:count]
    }

@register.inclusion_tag('tehblog/tag_list_tag.html')
def tag_list(count=None):
    return {
        'tag_list': Tag.objects.usage_for_model(
            Entry,
            counts=True,
            filters={
                'status': 2, # only published entries should add to the tags
            },
        )[:count]
    }

@register.inclusion_tag('tehblog/date_hierarchy_tag.html')
def date_hierarchy():
    """
    This tag will show a dynamic date hierarchy, which can
    be used to search for entries in specific years, months or days.

    Note that this tag is dependant on the generic views specified in
    urls. If you decide to customize the urls and views in any way, then
    this template tag may not function as intended.

    usage:
    {% load tehblog_tags %}
    {% date_hierarchy %}

    """
    return {
        'hierarchy': Entry.objects.public().order_by('publish_date').values('publish_date')
    }

@register.inclusion_tag('tehblog/date_list_tag.html')
def date_list(count=None):
    """
    This is a simpler version of the date_hierarchy tag, and will show
    recent dates as a list showing the month and year.
    Output would typically be: "November 2009"

    You can also pass the ``count`` attribute to limit the results. To
    return a full list of dates, use ``None``

    Usage:
    {% load tehblog_tags %}
    {% date_list %}

    or:
    {% date_list 30 %}

    """
    return {
        'date_list': Entry.objects.public().dates(
            'publish_date', 'month', order="DESC"
        )[:count]
    }


@register.inclusion_tag('tehblog/related_entries_tag.html')
def related_entries(entry, count=5):
    """
    Renders two lists of related content. First list is related content by category,
    second list is related by tags
    
    usage:
    {% related_entries entry %}

    """
    related_blog_entries = TaggedItem.objects.get_related(entry, Entry,
                                                          num=count)
    return {
        'related_entries': related_blog_entries,
    }
