from django.contrib import admin
from location.models import *


models = [Location]
admin.site.register(models)
