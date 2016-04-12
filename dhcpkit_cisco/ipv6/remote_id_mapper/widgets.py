from django.forms import widgets

from dhcpkit_cisco.ipv6.remote_id_mapper.utils import hex_as_ascii


class RemoteIdInput(widgets.MultiWidget):
    """
    Widget for binary data, presented in hexadecimal
    """

    def __init__(self, attrs=None):
        my_widgets = [
            widgets.CheckboxInput(attrs={'class': 'hex-ascii', 'style': 'vertical-align: baseline'}),
            widgets.TextInput(attrs={'size': '75'})
        ]
        super().__init__(my_widgets, attrs)

    class Media:
        js = ['remote_id_mapper/js/remote_id.js']

    def format_output(self, rendered_widgets):
        return '{} As ASCII<br/>{}'.format(*rendered_widgets)

    def decompress(self, value):
        if value is None:
            return True, ''

        return hex_as_ascii(value)
