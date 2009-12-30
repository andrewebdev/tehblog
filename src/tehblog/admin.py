# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from django.contrib import admin

from tehblog.models import Entry, Category

class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}
    list_display = ['title', 'slug', 'status', 'author', 'created_date',
                    'modified_date', 'publish_date']
    list_filter = ['status', 'author', 'publish_date']
    search_fields = ['title', 'slug', 'extract', 'content']
    date_hierarchy = 'publish_date'

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}
    list_display = ['title', 'slug']

admin.site.register(Entry, EntryAdmin)
admin.site.register(Category, CategoryAdmin)
