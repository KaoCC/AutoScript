from django.db import models

# Create your models here.


class Item(models.Model):

    name = models.CharField(max_length=300)
    # serial_number = models.CharField(max_length=300)
    # lend_from = models.DateField(null=True, blank=True)

    def __str__(self):
        """return item name"""
        return self.name


import uuid
from datetime import date

class ItemInstance(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, help_text = "Unique ID")
    serial_number = models.CharField(max_length=300)
    item = models.ForeignKey('Item', on_delete = models.SET_NULL, null=True)
    due_back = models.DateField(null=True, blank=True)

    # borrower


    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    
    def __str__(self):
        """String for representing the Model object."""
        return "{0} ({1} : {2})".format(self.id, self.serial_number, self.item.name)

