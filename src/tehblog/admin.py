# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from datetime import datetime

from django.contrib import admin

from ostinato.statemachine.models import InvalidAction
from ostinato.statemachine.forms import StateMachineModelForm
from tehblog.models import Entry, Category


### Admin Actions
def publish(modeladmin, request, queryset):
    # TODO: We need a more efficient method to do this, since it's not 'lazy'
    for item in queryset:
        try:
            item.sm_take_action('Publish')
            item.save()
        except InvalidAction:
            pass
publish.short_description = "Publish selected Entries"


def retract(modeladmin, request, queryset):
    # TODO: We need a more efficient method to do this, since it's not 'lazy'
    for item in queryset:
        if 'Reject' in item.sm_state_actions():
            item.sm_take_action('Reject')
            item.save()
        elif 'Retract' in item.sm_state_actions():
            item.sm_take_action('Retract')
            item.save()
retract.short_description = "Retract selected Entries"


def mark_for_review(modeladmin, request, queryset):
    # TODO: We need a more efficient method to do this, since it's not 'lazy'
    for item in queryset:
        try:
            item.sm_take_action('Submit')
            item.save()
        except InvalidAction:
            pass
mark_for_review.short_description = "Review selected Entries"


def allow_comments(modeladmin, request, queryset):
    queryset.update(allow_comments=True)
allow_comments.short_description = "Comments - Allow"


def disallow_comments(modeladmin, request, queryset):
    queryset.update(allow_comments=False)
disallow_comments.short_description = "Comments - Disallow"


### Admin Classes
class EntryAdminForm(StateMachineModelForm):

    class Meta:
        model = Entry

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        entry = super(EntryAdminForm, self).save(*args, **kwargs)
        action = self.cleaned_data['_sm_action']

        if action == 'publish' and not entry.publish_date:
            entry.publish_date = datetime.now()

        elif action == 'archive':
            entry.allow_comments = False

        if action:
            entry.sm.take_action(action)

        entry.save()

        return entry


class EntryAdmin(admin.ModelAdmin):
    form = EntryAdminForm

    prepopulated_fields = {'slug': ['title']}
    list_display = ['title', 'slug', 'state', 'author',
                    'created_date', 'modified_date', 'publish_date',
                    'allow_comments']
    list_filter = ['author', 'publish_date', 'allow_comments']
    search_fields = ['title', 'slug', 'extract', 'content']
    date_hierarchy = 'publish_date'
    actions = [publish, retract, mark_for_review, allow_comments,
               disallow_comments]


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}
    list_display = ['title', 'slug']


admin.site.register(Entry, EntryAdmin)
admin.site.register(Category, CategoryAdmin)
