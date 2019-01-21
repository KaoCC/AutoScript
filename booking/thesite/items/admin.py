from django.contrib import admin

from .models import Item, ItemInstance

admin.site.register(Item)
admin.site.register(ItemInstance)
