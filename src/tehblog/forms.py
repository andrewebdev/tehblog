# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from django import forms

from tehblog.models import Entry

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        exclude = ('created_date', 'modified_date',)
