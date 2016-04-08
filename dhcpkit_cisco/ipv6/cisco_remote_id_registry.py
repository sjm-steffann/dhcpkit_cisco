"""
The Cisco Remote-ID registry
"""
from dhcpkit.registry import Registry


class CiscoRemoteIdRegistry(Registry):
    """
    Registry for Cisco Remote-IDs
    """
    entry_point = 'dhcpkit_cisco.ipv6.remote_ids'


# Instantiate the Cisco Remote-ID registry
cisco_remote_id_registry = CiscoRemoteIdRegistry()
