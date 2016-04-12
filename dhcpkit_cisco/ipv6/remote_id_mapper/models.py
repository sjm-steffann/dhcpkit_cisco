from django.core.exceptions import ValidationError
from django.db import models

from dhcpkit_cisco.ipv6.remote_id_mapper.fields import SlotField, ModuleField, PortField, VlanField, \
    EnterpriseNumberField, HexField, RemoteIdField


class Switch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    duid = HexField('DUID', max_length=256, help_text="Use 'show ipv6 dhcp' to find the switch's DUID")

    # 00030001002584B1905E
    class Meta:
        verbose_name = '   Switch'
        verbose_name_plural = '   Switches'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def number_of_slots(self):
        return Slot.objects.filter(switch=self).count()

    def number_of_ports(self):
        return Port.objects.filter(module__slot__switch=self).count()


class Slot(models.Model):
    switch = models.ForeignKey(Switch)
    slot_nr = SlotField()

    has_modules = models.BooleanField(default=False,
                                      help_text="Check this box if this slot has multiple (internal) modules. "
                                                "If unchecked one dummy-module will automatically be created, "
                                                "which you can ignore.")

    class Meta:
        verbose_name = '  Slot'
        verbose_name_plural = '  Slots'
        unique_together = (('switch', 'slot_nr'),)
        ordering = ('switch__name', 'slot_nr')

    def __str__(self):
        return '{} Slot {}'.format(self.switch.name, self.slot_nr)

    def number_of_ports(self):
        return Port.objects.filter(module__slot=self).count()

    def clean(self):
        super().clean()

        if not self.has_modules:
            if self.module_set.count() > 1:
                # This slot *has* modules!
                raise ValidationError({'has_modules': "This slot has multiple modules, cannot clear has-modules flag"})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.has_modules:
            # Check if data matches constraint
            my_modules = list(self.module_set.all())
            if len(my_modules) == 0:
                # No module: auto-create one for convenience
                new_module = Module(slot=self, module_nr=0)
                new_module.save()
            elif len(my_modules) == 1:
                # Make sure module_number is 0
                my_module = my_modules[0]
                if my_module.module_nr != 0:
                    my_module.module_nr = 0
                    my_module.save()


class Module(models.Model):
    slot = models.ForeignKey(Slot)
    module_nr = ModuleField(default=0)

    class Meta:
        verbose_name = ' Module'
        verbose_name_plural = ' Modules'
        unique_together = (('slot', 'module_nr'),)
        ordering = ('slot__switch__name', 'slot__slot_nr', 'module_nr')

    def __str__(self):
        # Use the slot name for dummy modules
        if not self.slot.has_modules and self.module_nr == 0:
            return str(self.slot)
        else:
            return '{} Module {}'.format(self.slot, self.module_nr)

    def number_of_ports(self):
        return Port.objects.filter(module=self).count()

    def clean(self):
        super().clean()

        if not self.slot.has_modules:
            # Slots without modules always must have a dummy module 0
            if self.module_nr != 0:
                raise ValidationError({'module_nr': ['Slots without modules can only have a dummy module with nr 0']})


class Port(models.Model):
    module = models.ForeignKey(Module)
    port_nr = PortField()
    vlan = VlanField('VLAN', default=0, help_text="VLAN 0 is a wildcard that matches any VLAN")

    new_enterprise_number = EnterpriseNumberField()
    new_remote_id = RemoteIdField(max_length=512)

    class Meta:
        verbose_name = 'Port'
        verbose_name_plural = 'Ports'
        unique_together = (('module', 'port_nr', 'vlan'),)
        ordering = ('module__slot__switch__name', 'module__slot__slot_nr', 'module__module_nr', 'port_nr', 'vlan')

    def __str__(self):
        modules = list(self.module.slot.module_set.all())
        if not self.module.slot.has_modules and len(modules) == 1:
            # No modules involved
            descr = '{} Port {}/{}'.format(self.module.slot.switch.name, self.module.slot.slot_nr, self.port_nr)
        else:
            # Port numbering shows module
            descr = '{} Port {}/{}/{}'.format(self.module.slot.switch.name, self.module.slot.slot_nr,
                                              self.module.module_nr, self.port_nr)

        if self.vlan:
            descr += ' (VLAN {})'.format(self.vlan)

        return descr
