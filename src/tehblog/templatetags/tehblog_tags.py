# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

import re

from django import template
from django.db.models import Count

from tagging.models import Tag, TaggedItem
from tehblog.models import Entry, Category 

register = template.Library()

@register.inclusion_tag('tehblog/tags/category_list.html')
def category_list(count=None):
    """
    Renders a list of categories. Only categories that contains published
    blog entries will be returned to the tag and rendered.
    The number of categories returned can be restricted with the ``count``
    argument

    """
    return {
        'category_list': Category.objects.all().filter(
            entry___sm_state='Published').distinct()[:count]
    }

@register.inclusion_tag('tehblog/tags/tag_list.html')
def tag_list(slice_count=None):
    """
    Requires django-tagging.
    Renders a list of Tags used for all published blog entries.

    ``slice_count`` is the number of items that the list in the
    template should be sliced to

    """
    slice_count = str(slice_count)
    try:
        tag_list = Tag.objects.usage_for_model(Entry, counts=True,
            filters={ '_sm_state': 'Published' })
    except:
        pass
    return locals()

@register.inclusion_tag('tehblog/tags/date_hierarchy.html')
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

@register.inclusion_tag('tehblog/tags/date_list.html')
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
    date_list = Entry.objects.public().dates('publish_date', 'month',
        order="DESC")[:count]
    return locals()

@register.inclusion_tag('tehblog/tags/related_entries.html')
def related_entries(entry, count=5):
    """
    Renders a list of related blog entries based on the Entry Tags.
    This tag will only work if django-tagging is installed.
    
    usage:
    {% related_entries entry %}

    """
    try:
        related_blog_entries = TaggedItem.objects.get_related(
            entry, Entry, num=count)
    except: return {}
    return {
        'related_entries': related_blog_entries,
    }

## Filters
@register.filter(name='entries_for_month')
def entries_for_month(date_value):
    """
    Returns the number of entries that was published on a specific
    date.

    """
    count = Entry.objects.public().filter(
        publish_date__year=date_value.year,
        publish_date__month=date_value.month,
    ).count()
    return count

class EmbedFilter(object):
    """
    Special class to register render functions for use with the embed
    filter.
    """
    _functions = []

    @classmethod
    def register(cls, func_name, func):
        cls._functions.append({'name': func_name, 'function': func})

    @classmethod
    def get_function(cls, func_name):
        if cls._functions:
            for f in cls._functions:
                if f['name'] == func_name: return f['function']
        return None

    @classmethod
    def get_functions(cls):
        to_return = []
        for func in cls._functions:
            to_return.append(func['function'])
        return to_return
    
@register.filter(name='embed')
def embed(content, function=None):
    """
    This filter will call func() with content being passed to it as a
    string.

    ``function`` - A string containing the name of the function that
    parses content. The funciton will typically perform a task like,
    looking for a specific regex pattern in ``content`` and replace
    that pattern with Html that renders the element.

    If ``function`` is not supplied, we will automatically apply all
    functions to the filter.
    """
    if function:
        func = EmbedFilter.get_function(function)
        if func: return func(content)
        else: return content
    else:
        for func in EmbedFilter.get_functions():
            content = func(content)
        return content

def youtube(content):
    """
    Looks for any youtube url patterns in content, and replaces it with
    the youtube video
    """
    regex = re.compile(r"(http://)?(www\.)?((youtu\.be/)|(youtube\.com/watch\?v=))(?P<id>[A-Za-z0-9\-=_]{11})")
    return regex.sub('''
        <iframe width="480" height="390"
            src="http://www.youtube.com/embed/\g<id>" frameborder="0"
            allowfullscreen></iframe>
    ''', content)

def pl_gallery(content):
    """
    Example function showing how a photologue gallery can be
    embedded based on it's slug.

    Note: This is just an example and is a pretty pointless function to
    use as is. But free to copy this and modify the result.

    """
    regex = re.compile(r"\{{3}gallery=(?P<slug>[-\w]+)\}{3}")
    return regex.sub('''PHOTOLOGUE GALLERY \g<slug> HERE''', content)

EmbedFilter.register('youtube', youtube)
