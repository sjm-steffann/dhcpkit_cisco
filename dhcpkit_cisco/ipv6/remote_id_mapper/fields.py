from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property

from dhcpkit.utils import normalise_hex
from dhcpkit_cisco.ipv6.remote_id_mapper import forms


class SlotField(models.PositiveSmallIntegerField):
    @cached_property
    def validators(self):
        # Add custom range validators
        range_validators = [
            validators.MinValueValidator(0),
            validators.MaxValueValidator(2 ** 8 - 1),
        ]
        return super().validators + range_validators


class ModuleField(models.PositiveSmallIntegerField):
    @cached_property
    def validators(self):
        # Add custom range validators
        range_validators = [
            validators.MinValueValidator(0),
            validators.MaxValueValidator(2 ** 2 - 1),
        ]
        return super().validators + range_validators


class PortField(models.PositiveSmallIntegerField):
    @cached_property
    def validators(self):
        # Add custom range validators
        range_validators = [
            validators.MinValueValidator(0),
            validators.MaxValueValidator(2 ** 6 - 1),
        ]
        return super().validators + range_validators


class VlanField(models.PositiveSmallIntegerField):
    @cached_property
    def validators(self):
        # Add custom range validators
        range_validators = [
            validators.MinValueValidator(0),
            validators.MaxValueValidator(2 ** 12 - 1),
        ]
        return super().validators + range_validators


class EnterpriseNumberField(models.PositiveIntegerField):
    @cached_property
    def validators(self):
        # Add custom range validators
        range_validators = [
            validators.MinValueValidator(0),
            validators.MaxValueValidator(2 ** 32 - 1),
        ]
        return super().validators + range_validators


class HexField(models.CharField):
    def get_db_prep_value(self, value, connection, prepared=False):
        value = super().get_db_prep_value(value, connection, prepared)
        if value is not None:
            value = normalise_hex(value)
        return value

    def to_python(self, value):
        # If it's a string, it should be hex-encoded data
        if value is not None:
            try:
                value = normalise_hex(value)
            except ValueError:
                raise ValidationError("Value is not a valid hex-string")
        return value


class RemoteIdField(HexField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.RemoteIdField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
