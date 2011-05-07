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

## ContentModifiers and related examples
class ContentMod(object):
    """
    Special class to register render functions that will manipulate
    blog content in some way. These functions are accessed by the
    ``embed()`` filter below.
    """
    _modifiers = []

    @classmethod
    def register(cls, func_name, func):
        cls._modifiers.append({'name': func_name, 'func': func})

    def modifiers(self, exclude=[]):
        to_return = []
        for func in self._modifiers:
            if func['name'] not in exclude:
                to_return.append(func['func'])
        return to_return

    def __getitem__(self, what):
        for func in self._modifiers:
            if func['name'] == what: return func['func']
        return super(ContentMod, self).__getattr__(what)
    
@register.filter(name='modify')
def modify(content, mods=None):
    """
    This filter will call func() with content being passed to it as a
    string.

    ``mods`` is a comma seperated list of modifiers that we want the
    content to be passed through.
    
    There are three ways in which this filter can be used.

    1. if ``mods`` is not supplied, then by default we will run the
    content through _all_ modifiers
    
    2. if ``mods`` is supplied, then we will only run the content through
    modifiers specified in the list.

    3. if ``mods`` starts with "!" we will use all modifiers, _except_
    for any modifiers in the list immediately following the "!"

    Examples:
        {{ content|modify }}
        {{ content|modify:"youtube,gallery" }}
        {{ content|modify:"!snip,youtube" }}

    """
    cm = ContentMod()
    if mods:
        if mods[0] == "!":
            # Exclusion List
            mods = mods[1:].split(',')
            for func in cm.modifiers(exclude=mods):
                content = func(content)
        else:
            # Inclusion List
            mods = mods.split(',')
            for mod in mods:
                content = cm[mod](content)
    else:
        for func in cm.modifiers():
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

def snip(content):
    """
    This is a special modifier, that will look for a marker in
    ``content`` and if found, it will truncate the content at that
    point.

    This way the editor can decide where he wants content to be truncated,
    for use in the various list views.

    The marker we will look for in the content is {{{snip}}}
    """
    return content[:content.find('{{{snip}}}')] + "..."

def hide_snip(content):
    return content.replace('{{{snip}}}', '')

ContentMod.register('youtube', youtube)
ContentMod.register('snip', snip)
ContentMod.register('hide_snip', hide_snip)
