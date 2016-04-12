"""
Option handler to rewrite hardcoded Cisco Remote-IDs to something more useful
"""

import configparser

from dhcpkit.ipv6.extensions.remote_id import RemoteIdOption
from dhcpkit.ipv6.option_handlers import OptionHandler
from dhcpkit.ipv6.transaction_bundle import TransactionBundle
from dhcpkit_cisco import CISCO_ENTERPRISE_ID
from dhcpkit_cisco.ipv6.cisco_remote_id import CiscoEthernetRemoteId


class RewriteRemoteIdOptionHandler(OptionHandler):
    """
    Handler for rewriting  in responses
    """

    def __init__(self):
        super().__init__()

    def pre(self, bundle: TransactionBundle):
        """
        This handler modifies the incoming request and may substitute the remote-id option.
        """
        # Try to find the Remote-ID option and stop processing if not found
        remote_id_option = bundle.incoming_relay_messages[0].get_option_of_type(RemoteIdOption)
        if not remote_id_option or not isinstance(remote_id_option, RemoteIdOption):
            return

        # Ok, there is an option, but is it a Cisco one?
        if remote_id_option.enterprise_number != CISCO_ENTERPRISE_ID:
            return

        # Cisco! Read the Ethernet Remote-ID
        try:
            cisco_remote_id = CiscoEthernetRemoteId().parse(buffer=remote_id_option.remote_id,
                                                            length=len(remote_id_option.remote_id))
        except ValueError:
            # Apparently not...
            return

        print(cisco_remote_id)

    def handle(self, bundle: TransactionBundle):
        """
        This handler does no normal handling
        """
        pass

    @classmethod
    def from_config(cls, section: configparser.SectionProxy, option_handler_id: str = None) -> OptionHandler:
        """
        Create a handler of this class based on the configuration in the config section.

        :param section: The configuration section
        :param option_handler_id: Optional extra identifier
        :return: A handler object
        :rtype: OptionHandler
        """
        return cls()
