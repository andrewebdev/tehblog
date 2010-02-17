# -*- coding: utf-8 -*-

# © Copyright 2009 Andre Engelbrecht. All Rights Reserved.
# This script is licensed under the BSD Open Source Licence
# Please see the text file LICENCE for more information
# If this script is distributed, it must be accompanied by the Licence

from datetime import datetime

from django.db import models

class EntryManager(models.Manager):
    def public(self):
        return self.get_query_set().filter(status=2)

    def related_by_categories(self, entry, count=None):
        """
        This method will return all entries related to ``entry`` by category
        if ``count`` is specified, then we restrict the number of entries returned

        """
        entries = self.get_query_set().exclude(slug=entry.slug).filter(
            categories=entry.categories.all()
        ).distinct()
        return entries[:count]
