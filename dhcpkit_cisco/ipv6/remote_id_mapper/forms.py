import codecs

from django import forms
from django.core.exceptions import ValidationError

from dhcpkit.utils import normalise_hex
from dhcpkit_cisco.ipv6.remote_id_mapper.widgets import RemoteIdInput


class RemoteIdField(forms.MultiValueField):
    widget = RemoteIdInput

    def __init__(self, max_length, *args, **kwargs):
        fields = (
            forms.BooleanField(required=False),
            forms.CharField(max_length=max_length),
        )

        # Ignore widget override
        kwargs.pop('widget', None)

        super().__init__(fields=fields, require_all_fields=False, *args, **kwargs)

    def compress(self, data_list):
        as_ascii, value = data_list

        if value in self.empty_values:
            return ''

        if isinstance(value, str):
            value = value.strip()
            if as_ascii:
                try:
                    value = codecs.encode(value.encode('ascii'), 'hex').decode('ascii')
                except UnicodeEncodeError:
                    raise ValidationError("Value is not a valid ASCII value")
            else:
                try:
                    value = normalise_hex(value)
                except ValueError:
                    raise ValidationError("Value is not a valid hexadecimal value")

        return value
