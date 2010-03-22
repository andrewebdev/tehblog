# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from django.contrib import admin

from tehblog.models import Entry, Category

### Admin Actions
def publish(modeladmin, request, queryset):
    queryset.update(status=Entry.PUBLIC)
    # call every item's save() method so that dates are
    # also updated
    for item in queryset:
        item.save()
publish.short_description = "Publish selected Entries"

def retract(modeladmin, request, queryset):
    queryset.update(status=Entry.DRAFT)
retract.short_description = "Retract selected Entries"

def mark_for_review(modeladmin, request, queryset):
    queryset.update(status=Entry.REVIEW)
mark_for_review.short_description = "Review selected Entries"

def allow_comments(modeladmin, request, queryset):
    queryset.update(allow_comments=True)
allow_comments.short_description = "Comments - Allow"

def disallow_comments(modeladmin, request, queryset):
    queryset.update(allow_comments=False)
disallow_comments.short_description = "Comments - Disallow"

### Admin Classes
class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}
    list_display = ['title', 'slug', 'status', 'author', 'created_date',
                    'modified_date', 'publish_date', 'allow_comments']
    list_filter = ['status', 'author', 'publish_date', 'allow_comments']
    search_fields = ['title', 'slug', 'extract', 'content']
    date_hierarchy = 'publish_date'
    actions = [publish, retract, mark_for_review, allow_comments,
               disallow_comments]

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}
    list_display = ['title', 'slug']

admin.site.register(Entry, EntryAdmin)
admin.site.register(Category, CategoryAdmin)
