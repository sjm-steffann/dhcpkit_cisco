from struct import unpack_from, pack

from dhcpkit.ipv6.duids import DUID
from dhcpkit.protocol_element import ProtocolElement

CISCO_ETHERNET_REMOTE_ID = 2


# noinspection PyAbstractClass
class CiscoRemoteId(ProtocolElement):
    """
    Base class for Cisco Remote-IDs
    """

    # This needs to be overwritten in subclasses
    remote_id_type = 0

    @classmethod
    def determine_class(cls, buffer: bytes, offset: int = 0) -> type:
        """
        Return the appropriate subclass from the registry, or UnknownDUID if no subclass is registered.

        :param buffer: The buffer to read data from
        :param offset: The offset in the buffer where to start reading
        :return: The best known class for this duid data
        """
        from dhcpkit_cisco.ipv6.cisco_remote_id_registry import cisco_remote_id_registry

        # First get the type field, why is this little-endian?
        remote_id_type = unpack_from('<H', buffer, offset=offset)[0]
        return cisco_remote_id_registry.get(remote_id_type, CiscoUnknownRemoteId)

    def parse_remote_id_header(self, buffer: bytes, offset: int = 0, length: int = None) -> int:
        """
        Parse the Remote-ID type and perform some basic validation.

        :param buffer: The buffer to read data from
        :param offset: The offset in the buffer where to start reading
        :param length: The amount of data we are allowed to read from the buffer
        :return: The number of bytes used from the buffer
        """
        if not length:
            raise ValueError('Cisco Remote-ID length must be explicitly provided when parsing')

        # First get the type field, why is this little-endian?
        remote_id_type = unpack_from('<H', buffer, offset=offset)[0]
        my_offset = 2

        if remote_id_type != self.remote_id_type:
            raise ValueError('The provided buffer does not contain {} data'.format(self.__class__.__name__))

        return my_offset


class CiscoUnknownRemoteId(CiscoRemoteId):
    """
    Container for raw DUID content for cases where we don't know how to decode the DUID.
    """

    def __init__(self, remote_id_type: int = 0, remote_id_data: bytes = b''):
        self.remote_id_type = remote_id_type
        self.remote_id_data = remote_id_data

    def load_from(self, buffer: bytes, offset: int = 0, length: int = None) -> int:
        """
        Load the internal state of this object from the given buffer. The buffer may contain more data after the
        structured element is parsed. This data is ignored.

        :param buffer: The buffer to read data from
        :param offset: The offset in the buffer where to start reading
        :param length: The amount of data we are allowed to read from the buffer
        :return: The number of bytes used from the buffer
        """
        # First get the type field, why is this little-endian?
        self.remote_id_type = unpack_from('<H', buffer, offset=offset)[0]
        my_offset = self.parse_remote_id_header(buffer, offset, length)

        remote_id_len = length - my_offset
        self.remote_id_data = buffer[offset + my_offset:offset + my_offset + remote_id_len]
        my_offset += remote_id_len

        return my_offset

    def save(self) -> bytes:
        """
        Save the internal state of this object as a buffer.

        :return: The buffer with the data from this element
        """
        return pack('<H', self.remote_id_type) + self.remote_id_data


class CiscoEthernetRemoteId(CiscoRemoteId):
    """
    Information in a Cisco ethernet Remote-ID based on the information found on
    https://supportforums.cisco.com/discussion/11349231/ipv6-dhcp-relay-and-remote-identifier-option-37

    The essential bits of the answer given by user shwethab are included below:

    Here's the interpretation of the fields in remote id:

                             000000000011111111112222222222333333
                             012345678901234567890123456789012345

    Fa2/3     Remote-ID:     020023000200000a00030001c47d4f73a0bf
    Fa2/10    Remote-ID:     02002a000200000a00030001c47d4f73a0bf
    Fa2/11    Remote-ID:     02002b000200000a00030001c47d4f73a0bf
    Fa2/15    Remote-ID:     02002f000200000a00030001c47d4f73a0bf
    Fa2/16    Remote-ID:     020020080200000a00030001c47d4f73a0bf
    Fa2/17    Remote-ID:     020021080200000a00030001c47d4f73a0bf
    Fa2/18    Remote-ID:     020022080200000a00030001c47d4f73a0bf
    Fa2/31    Remote-ID:     02002f080200000a00030001c47d4f73a0bf
    Fa2/32    Remote-ID:     020028090200000a00030001c47d4f73a0bf
    Fa2/37    Remote-ID:     02002d090200000a00030001c47d4f73a0bf
    Fa2/39    Remote-ID:     02002f090200000a00030001c47d4f73a0bf
    Fa2/40    Remote-ID:     0200280a0200000a00030001c47d4f73a0bf

    Field 0  - 3:   Remote ID type - for ethernet it is 2, if type is 2 remaining fields are interpreted as below
    Field 4  - 7:   interface information (detailed below)
    Field 8  - 11:  VLAN id
    Field 12 - 15:  Length of the DUID that follows
    Field 16 - 35:  DUID

    Field 4-7 consists of 2 bytes that are interpreted as
      4-5 (in binary): - interface_info  -> slot : 4(ssss); module : 1(m); port :3(ppp);
      6-7 (in binary): - extension_info  -> slot : 4(SSSS); module : 1(M); port :3(PPP);

    field 4-5: form the lower order information
    field 6-7: form the higher order information

    slot :  field 6  and field 4 are stitched together to form slot (SSSSssss)
    module: first bit of field 7 and first bit of field 5 are stitched together (Mm)
    port:   last 3 bits of field 7 and last 3 bits of 5 are stitched together (PPPppp)

    FastEthernetX/Y
    X = slot
    Y = module * 8 + port

    for e.g. to arrive at fa2/3 = 0x2300 - 2 is the slot, module is 0, port = 3 so it is fa2/3
    0x280a -> slot = 2, module = 3, port = 16 , fa 2/ (3*8 + 16) = fa2/40
    """

    remote_id_type = CISCO_ETHERNET_REMOTE_ID

    def __init__(self, slot: int = 0, module: int = 0, port: int = 0, vlan: int = 0, duid: DUID = None):
        self.slot = slot
        self.module = module
        self.port = port
        self.vlan = vlan
        self.duid = duid

    def validate(self):
        """
        Validate that the contents of this object conform to protocol specs.
        """
        if not isinstance(self.slot, int) or not (0 <= self.slot < 2 ** 8):
            raise ValueError("Slot must be an unsigned 8 bit integer")

        if not isinstance(self.module, int) or not (0 <= self.module < 2 ** 2):
            raise ValueError("Module must be an unsigned 2 bit integer")

        if not isinstance(self.port, int) or not (0 <= self.port < 2 ** 6):
            raise ValueError("Port must be an unsigned 6 bit integer")

        if not isinstance(self.vlan, int) or not (0 <= self.vlan < 2 ** 12):
            raise ValueError("VLAN must be an unsigned 12 bit integer")

        if not isinstance(self.duid, DUID):
            raise ValueError("DUID must contact a valid DUID object")

    def load_from(self, buffer: bytes, offset: int = 0, length: int = None) -> int:
        """
        Load the internal state of this object from the given buffer. The buffer may contain more data after the
        structured element is parsed. This data is ignored.

        :param buffer: The buffer to read data from
        :param offset: The offset in the buffer where to start reading
        :param length: The amount of data we are allowed to read from the buffer
        :return: The number of bytes used from the buffer
        """
        my_offset = self.parse_remote_id_header(buffer, offset, length)

        # Then the interface number in its weird way
        slot_lower = (buffer[offset + my_offset] & 0b11110000) >> 4
        module_lower = (buffer[offset + my_offset] & 0b00001000) >> 3
        port_lower = buffer[offset + my_offset] & 0b00000111
        my_offset += 1

        slot_higher = buffer[offset + my_offset] & 0b11110000
        module_higher = (buffer[offset + my_offset] & 0b00001000) >> 2
        port_higher = (buffer[offset + my_offset] & 0b00000111) << 3
        my_offset += 1

        self.slot = slot_higher | slot_lower
        self.module = module_higher | module_lower
        self.port = port_higher | port_lower

        # Next is the VLAN
        self.vlan = unpack_from('!H', buffer, offset=offset + my_offset)[0]
        my_offset += 2

        # Read the DUID length and check the data length
        duid_length = unpack_from('!H', buffer, offset=offset + my_offset)[0]
        my_offset += 2
        if length != duid_length + my_offset:
            # Mismatch in length, invalid remote-id?
            raise ValueError("Cisco Remote-ID length incorrect")

        # Get the DUID
        read_length, self.duid = DUID.parse(buffer, offset=8, length=duid_length)
        my_offset += read_length
        if read_length != duid_length:
            # Mismatch in length, invalid DUID?
            raise ValueError("Cisco Remote-ID DUID length incorrect")

        return my_offset

    def save(self) -> bytes:
        """
        Save the internal state of this object as a buffer.

        :return: The buffer with the data from this element
        """
        # Build the weird interface number
        lower = 0
        higher = 0

        # Add the slot
        lower |= (self.slot & 0b00001111) << 4
        higher |= self.slot & 0b11110000

        # Add the module
        lower |= (self.module & 0b00000001) << 3
        higher |= (self.module & 0b00000010) << 2

        # Add the port
        lower |= self.port & 0b00000111
        higher |= (self.port & 0b00111000) >> 3

        # Prepare the DUID
        duid_bytes = self.duid.save()
        duid_len = len(duid_bytes)

        return pack('<H', self.remote_id_type) + pack('!BBHH', lower, higher, self.vlan, duid_len) + duid_bytes
