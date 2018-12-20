from django.contrib import admin

from routers.models import Router, Neighbour, Slot, Card, InterfacePort


class RouterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class SlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'router', 'slot_number']


class CardAdmin(admin.ModelAdmin):
    list_display = ['id', 'slot', 'node_type', 'node_state', 'admin_state', 'config_state']
    list_filter = ['slot__router']


class InterfacePortAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'ip_address', 'status', 'protocol', 'card']
    list_filter = ['card__slot__router']


class NeighbourPortAdmin(admin.ModelAdmin):
    list_display = ['id', 'to_router', 'local_intf', 'hold_time', 'capability', 'external_port_id']
    list_filter = ['from_router']


admin.site.register(Router, RouterAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(InterfacePort, InterfacePortAdmin)
admin.site.register(Neighbour, NeighbourPortAdmin)
