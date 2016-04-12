from django.contrib import admin

from dhcpkit_cisco.ipv6.remote_id_mapper.models import Switch, Slot, Port, Module
from dhcpkit_cisco.ipv6.remote_id_mapper.utils import display_hex


@admin.register(Switch)
class SwitchAdmin(admin.ModelAdmin):
    list_display = ('name', 'duid_hex', 'number_of_slots', 'number_of_ports')

    fieldsets = [
        ('Switch definition', {
            'fields': ('name', 'duid'),
        }),
    ]

    def duid_hex(self, port):
        return display_hex(port.duid)

    duid_hex.short_description = 'DUID'


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'number_of_ports')
    list_filter = ('switch',)

    fieldsets = [
        ('Slot definition', {
            'fields': ('switch', 'slot_nr'),
        }),
        ('Slot type', {
            'fields': ('has_modules',),
        }),
    ]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'number_of_ports')
    list_filter = ('slot__switch',)

    fieldsets = [
        ('Module definition', {
            'fields': ('slot', 'module_nr'),
        }),
    ]


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'admin_vlan', 'new_enterprise_number', 'new_remote_id_hex')
    list_filter = ('module__slot__switch', 'vlan')

    fieldsets = [
        ('Port definition', {
            'fields': ('module', 'port_nr', 'vlan'),
        }),
        ('New Remote-ID', {
            'fields': ('new_enterprise_number', 'new_remote_id'),
        }),
    ]

    def new_remote_id_hex(self, port):
        return display_hex(port.new_remote_id)

    new_remote_id_hex.short_description = 'New Remote-ID'

    def admin_vlan(self, port):
        if port.vlan == 0:
            return '*'
        return port.vlan

    admin_vlan.short_description = 'VLAN'
    admin_vlan.admin_order_field = 'vlan'
