# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from tehblog.models import Category, Entry
from tehblog.forms import EntryForm

## Blog Entry List views
def category_entries(request, slug,
                     template="tehblog/list_view.html"):
    category = get_object_or_404(Category, slug=slug)
    if request.user.is_staff:
        entries = Entry.objects.filter(categories=category)
    else:
        entries = Entry.objects.public().filter(categories=category)
    return render_to_response(
        template,
        {'entries': entries, 'category': category},
        context_instance=RequestContext(request)
    )

## Single Entry views and actions
def entry_view(request, year, month, slug,
               template="tehblog/entry_view.html"):
    entry = get_object_or_404(
        Entry,
        publish_date__year=year,
        publish_date__month=month,
        slug=slug,
        status=Entry.PUBLIC
    )
    return render_to_response(
        template,
        {'entry': entry},
        context_instance=RequestContext(request)
    )
