from django.contrib import admin

from routers.models import Router, Neighbour, Slot, Card, Port

admin.site.register(Router)
admin.site.register(Slot)
admin.site.register(Card)
admin.site.register(Port)
admin.site.register(Neighbour)
