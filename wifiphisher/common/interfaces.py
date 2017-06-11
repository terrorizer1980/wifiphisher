"""
This module was made to handle all the interface related operations of
the program
"""

import random
import pyric
import pyric.pyw as pyw
import dbus
import wifiphisher.common.constants as constants


class InvalidInterfaceError(Exception):
    """ Exception class to raise in case of a invalid interface """

    def __init__(self, interface_name, mode=None):
        """
        Construct the class

        :param self: A InvalidInterfaceError object
        :param interface_name: Name of an interface
        :type self: InvalidInterfaceError
        :type interface_name: str
        :return: None
        :rtype: None
        """

        message = "The provided interface \"{0}\" is invalid!".format(interface_name)

        # provide more information if mode is given
        if mode:
            message += "Interface {0} doesn't support {1} mode".format(interface_name, mode)

        Exception.__init__(self, message)


class InvalidMacAddressError(Exception):
    """
    Exception class to raise in case of specifying invalid mac address
    """

    def __init__(self, mac_address):
        """
        Construct the class

        :param self: A InvalidMacAddressError object
        :param mac_address: A MAC address
        :type self: InvalidMacAddressError
        :type mac_address: str
        :return: None
        :rtype: None
        """
        message = "The provided MAC address {0} is invalid".format(mac_address)
        Exception.__init__(self, message)


class InvalidValueError(Exception):
    """
    Exception class to raise in case of a invalid value is supplied
    """

    def __init__(self, value, correct_value_type):
        """
        Construct the class

        :param self: A InvalidValueError object
        :param value_type: The value supplied
        :param correct_value_type: The correct value type
        :type self: InvalidValueError
        :type value_type: any
        :type correct_value_type: any
        :return: None
        :rtype: None
        """

        value_type = type(value)

        message = ("Expected value type to be {0} while got {1}."
                   .format(correct_value_type, value_type))
        Exception.__init__(self, message)


class InterfaceCantBeFoundError(Exception):
    """
    Exception class to raise in case of a invalid value is supplied
    """

    def __init__(self, interface_modes):
        """
        Construct the class

        :param self: A InterfaceCantBeFoundError object
        :param interface_modes: Modes of interface required
        :type self: InterfaceCantBeFoundError
        :type interface_modes: tuple
        :return: None
        :rtype: None
        .. note: For interface_modes the tuple should contain monitor
            mode as first argument followed by AP mode
        """

        monitor_mode = interface_modes[0]
        ap_mode = interface_modes[1]

        message = "Failed to find an interface with "

        # add appropriate mode
        if monitor_mode:
            message += "monitor"
        elif ap_mode:
            message += "AP"

        message += " mode"

        Exception.__init__(self, message)


class InterfaceManagedByNetworkManagerError(Exception):
    """
    Exception class to raise in case of NetworkManager controls the AP or deauth interface
    """
    def __init__(self, interface_name):
        """
        Construct the class.
        :param self: An InterfaceManagedByNetworkManagerError object
        :param interface_name: Name of interface
        :type self: InterfaceManagedByNetworkManagerError
        :type interface_name: str
        :return: None
        :rtype: None
        """

        message = (
            "Interface \"{0}\" is controlled by NetworkManager."
            "You need to manually set the devices that should be ignored by NetworkManager "
            "using the keyfile plugin (unmanaged-directive). For example, '[keyfile] "
            "unmanaged-devices=interface-name:\"{0}\"' needs to be added in your "
            "NetworkManager configuration file.".format(interface_name))
        Exception.__init__(self, message)


class NetworkAdapter(object):
    """ This class represents a network interface """

    def __init__(self, name, card_obj, mac_address):
        """
        Setup the class with all the given arguments

        :param self: A NetworkAdapter object
        :param name: Name of the interface
        :param card_obj: A pyric.pyw.Card object
        :param mac_address: The MAC address of interface
        :type self: NetworkAdapter
        :type name: str
        :type card_obj: pyric.pyw.Card
        :type mac_address: str
        :return: None
        :rtype: None
        """

        # Setup the fields
        self._name = name
        self._has_ap_mode = False
        self._has_monitor_mode = False
        self._is_managed_by_nm = False
        self._card = card_obj
        self._original_mac_address = mac_address
        self._current_mac_address = mac_address

    @property
    def name(self):
        """
        Return the name of the interface

        :param self: A NetworkAdapter object
        :type self: NetworkAdapter
        :return: The name of the interface
        :rtype: str
        """

        return self._name

    @property
    def is_managed_by_nm(self):
        """
        Return whether the interface controlled by NetworkManager

        :param self: A NetworkAdapter object
        :type self: NetworkAdapter
        :return: True if interface is controlled by NetworkManager
        :rtype: bool
        """
        return self._is_managed_by_nm

    @is_managed_by_nm.setter
    def is_managed_by_nm(self, value):
        """
        Set whether the interface is controlled by NetworkManager

        :param self: A NetworkAdapter object
        :param value: A value representing interface controlled by NetworkManager
        :type self: NetworkAdapter
        :type value: bool
        :return: None
        :rtype: None
        :raises InvalidValueError: When the given value is not bool
        """

        if isinstance(value, bool):
            self._is_managed_by_nm = value
        else:
            raise InvalidValueError(value, bool)

    @property
    def has_ap_mode(self):
        """
        Return whether the interface supports AP mode

        :param self: A NetworkAdapter object
        :type self: NetworkAdapter
        :return: True if interface supports AP mode and False otherwise
        :rtype: bool
        """

        return self._has_ap_mode

    @has_ap_mode.setter
    def has_ap_mode(self, value):
        """
        Set whether the interface supports AP mode

        :param self: A NetworkAdapter object
        :param value: A value representing AP mode support
        :type self: NetworkAdapter
        :type value: bool
        :return: None
        :rtype: None
        :raises InvalidValueError: When the given value is not bool
        """

        if isinstance(value, bool):
            self._has_ap_mode = value
        else:
            raise InvalidValueError(value, bool)

    @property
    def has_monitor_mode(self):
        """
        Return whether the interface supports monitor mode

        :param self: A NetworkAdapter object
        :type self: NetworkAdapter
        :return: True if interface supports monitor mode and False otherwise
        :rtype: bool
        """

        return self._has_monitor_mode

    @has_monitor_mode.setter
    def has_monitor_mode(self, value):
        """
        Set whether the interface supports monitor mode

        :param self: A NetworkAdapter object
        :param value: A value representing monitor mode support
        :type self: NetworkAdapter
        :type value: bool
        :return: None
        :rtype: None
        :raises InvalidValueError: When the given value is not bool
        """

        if isinstance(value, bool):
            self._has_monitor_mode = value
        else:
            raise InvalidValueError(value, bool)

    @property
    def card(self):
        """
        Return the card object associated with the interface

        :param self: A NetworkAdapter object
        :type self: NetworkAdapter
        :return: The card object
        :rtype: pyric.pyw.Card
        """

        return self._card

    @property
    def mac_address(self):
        """
        Return the current MAC address of the interface

        :param self: A NetworkAdapter object
        :type self: NetworkAdapter
        :return: The MAC of the interface
        :rtype: str
        """

        return self._current_mac_address

    @mac_address.setter
    def mac_address(self, value):
        """
        Set the MAC address of the interface

        :param self: A NetworkAdapter object
        :param value: A value representing monitor mode support
        :type self: NetworkAdapter
        :type value: str
        :return: None
        :rtype: None
        """

        self._current_mac_address = value

    @property
    def original_mac_address(self):
        """
        Return the original MAC address of the interface

        :param self: A NetworkAdapter object
        :type self: NetworkAdapter
        :return: The original MAC of the interface
        :rtype: str
        """

        return self._original_mac_address


class NetworkManager(object):
    """
    This class represents a network manager where it handles all the management
    for the interfaces.
    """

    def __init__(self):
        """
        Setup the class with all the given arguments.

        :param self: A NetworkManager object
        :type self: NetworkManager
        :return: None
        :rtype: None
        """

        self._name_to_object = dict()
        self._active = set()
        self._exclude_shutdown = set()

    def is_interface_valid(self, interface_name, mode=None):
        """
        Check if interface is valid

        :param self: A NetworkManager object
        :param interface_name: Name of an interface
        :param mode: The mode of the interface to be checked
        :type self: NetworkManager
        :type interface_name: str
        :type mode: str
        :return: True if interface is valid
        :rtype: bool
        :raises InvalidInterfaceError: If the interface is invalid
        :raises InterfaceManagedByNetworkManagerError: If the card is managed and
                is being used as deauth/ap mode
        .. note: The available modes are monitor, AP and internet
            The internet adapter should be put in the _exclude_shutdown set
            so that it will not be shutdown after the program exits.
        """

        # raise an error if interface can't be found
        try:
            interface_adapter = self._name_to_object[interface_name]
            if mode == "internet":
                self._exclude_shutdown.add(interface_name)

            # raise an error if interface doesn't support the mode
            if mode != "internet" and interface_adapter.is_managed_by_nm:
                raise InterfaceManagedByNetworkManagerError(interface_name)
            if mode == "monitor" and not interface_adapter.has_monitor_mode:
                raise InvalidInterfaceError(interface_name, mode)
            elif mode == "AP" and not interface_adapter.has_ap_mode:
                raise InvalidInterfaceError(interface_name, mode)
            # add the valid card to _active set
            self._active.add(interface_name)
            return True
        except KeyError:
            raise InvalidInterfaceError(interface_name)

    def set_interface_mac(self, interface_name, mac_address):
        """
        Set the specified MAC address for the interface

        :param self: A NetworkManager object
        :param interface_name: Name of an interface
        :param mac_address: A MAC address
        :type self: NetworkManager
        :type interface_name: str
        :type mac_address: str
        :return: None
        :rtype: None
        .. note: This method will set the interface to managed mode
        """

        card = self._name_to_object[interface_name].card
        self.set_interface_mode(interface_name, "managed")

        # card must be turned off(down) before setting mac address
        try:
            pyw.down(card)
            pyw.macset(card, mac_address)
            pyw.up(card)
        # make sure to catch an invalid mac address
        except pyric.error as error:
            if error[0] == 22:
                raise InvalidMacAddressError(mac_address)
            else:
                raise

    def get_interface_mac(self, interface_name):
        """
        Return the MAC address of the interface

        :param self: A NetworkManager object
        :param interface_name: Name of an interface
        :type self: NetworkManager
        :type interface_name: str
        :return: Interface MAC address
        :rtype: str
        """

        return self._name_to_object[interface_name].mac_address

    def set_interface_mac_random(self, interface_name):
        """
        Set random MAC address for the interface

        :param self: A NetworkManager object
        :param interface_name: Name of an interface
        :type self: NetworkManager
        :type interface_name: str
        :return: None
        :rtype: None
        .. note: This method will set the interface to managed mode.
            Also the first 3 octets are always 00:00:00 by default
        """

        # generate a new mac address and set it to adapter's new address
        new_mac_address = generate_random_address()
        self._name_to_object[interface_name].mac_address = new_mac_address

        # change the mac address of adapter
        self.set_interface_mac(interface_name, new_mac_address)

    def set_interface_mode(self, interface_name, mode):
        """
        Set the specified mode for the interface

        :param self: A NetworkManager object
        :param interface_name: Name of an interface
        :param mode: Mode of an interface
        :type self: NetworkManager
        :type interface_name: str
        :type mode: str
        :return: None
        :rtype: None
        .. note: Available modes are unspecified, ibss, managed, AP
            AP VLAN, wds, monitor, mesh, p2p
        """

        card = self._name_to_object[interface_name].card

        # set interface mode between brining it down and up
        pyw.down(card)
        pyw.modeset(card, mode)
        pyw.up(card)

    def get_interface(self, has_ap_mode=False, has_monitor_mode=False):
        """
        Return the name of a valid interface with modes supplied

        :param self: A NetworkManager object
        :param has_ap_mode: AP mode support
        :param has_monitor_mode: Monitor mode support
        :type self: NetworkManager
        :type has_ap_mode: bool
        :type has_monitor_mode: bool
        :return: Name of valid interface
        :rtype: str
        .. raises InterfaceCantBeFoundError: When an interface with
            supplied modes can't be found
        .. raises InterfaceManagedByNetworkManagerError: When the chosen
        interface is managed by NetworkManager
        .. note: This method guarantees that an interface with perfect
            match will be returned if available
        """

        possible_adapters = list()
        for interface, adapter in self._name_to_object.iteritems():
            # check to make sure interface is not active and not already in the possible list
            if (interface not in self._active) and (adapter not in possible_adapters):
                # in case of perfect match case
                if (adapter.has_ap_mode == has_ap_mode and
                        adapter.has_monitor_mode == has_monitor_mode):
                    possible_adapters.insert(0, adapter)

                # in case of requested AP mode and interface has AP mode (Partial match)
                elif has_ap_mode and adapter.has_ap_mode:
                    possible_adapters.append(adapter)
                # in case of requested monitor mode and interface has monitor mode (Partial match)
                elif has_monitor_mode and adapter.has_monitor_mode:
                    possible_adapters.append(adapter)

        for adapter in possible_adapters:
            if not adapter.is_managed_by_nm:
                chosen_interface = adapter.name
                self._active.add(chosen_interface)
                return chosen_interface

        if possible_adapters:
            raise InterfaceManagedByNetworkManagerError("ALL")
        else:
            raise InterfaceCantBeFoundError((has_monitor_mode, has_ap_mode))

    def get_interface_automatically(self):
        """
        Return a name of two interfaces
        :param self: A NetworkManager object
        :param self: NetworkManager
        :return: Name of monitor interface followed by AP interface
        :rtype: tuple
        """

        monitor_interface = self.get_interface(has_monitor_mode=True)
        ap_interface = self.get_interface(has_ap_mode=True)

        return (monitor_interface, ap_interface)

    def unblock_interface(self, interface_name):
        """
        Unblock interface if it is blocked

        :param self: A NetworkManager object
        :param interface_name: Name of an interface
        :type self: NetworkManager
        :type interface_name: str
        :return: None
        :rtype: None
        """

        card = self._name_to_object[interface_name].card

        # unblock card if it is blocked
        if pyw.isblocked(card):
            pyw.unblock(card)

    def set_interface_channel(self, interface_name, channel):
        """
        Set the channel for the interface

        :param self: A NetworkManager object
        :param interface_name: Name of an interface
        :param channel: A channel number
        :type self: NetworkManager
        :type interface_name: str
        :type channel: int
        :return: None
        :rtype: None
        """

        card = self._name_to_object[interface_name].card

        pyw.chset(card, channel)

    def start(self):
        """
        Start the network manager

        :param self: A NetworkManager object
        :type self: NetworkManager
        :return: None
        :rtype: None
        """

        # populate our dictionary with all the available interfaces on the system
        for interface in pyw.interfaces():
            try:
                card = pyw.getcard(interface)
                mac_address = pyw.macget(card)
                adapter = NetworkAdapter(interface, card, mac_address)
                self._name_to_object[interface] = adapter
                interface_property_detector(adapter)
            # ignore devices that are not supported(93) and no such device(19)
            except pyric.error as error:
                if error[0] == 93 or error[0] == 19:
                    pass
                else:
                    raise error

    def on_exit(self):
        """
        Perform a clean up for the class

        :param self: A NetworkManager object
        :type self: NetworkManager
        :return: None
        :rtype: None
        ..note: The cards in _exclude_shutdown will not set to the original mac address
                since these cards are not changed the mac addresses by the program.
        """

        for interface in self._active:
            if interface not in self._exclude_shutdown:
                adapter = self._name_to_object[interface]
                mac_address = adapter.original_mac_address
                self.set_interface_mac(interface, mac_address)


def is_managed_by_network_manager(interface_name):
    """
    Check if the interface is managed by NetworkManager

    :param network_adapter: A NetworkAdapter object
    :type interface_name: NetworkAdapter
    :return if managed by NetworkManager return True
    :rtype: bool
    .. note: When the NetworkManager service is not running, using bus.get_object
        will raise the exception. It's safe to pass this exception since when
        NetworkManger doesn't run, the manage property will be unmanaged.

        We first create the network_manager_proxy first, and use it to get the
        network_manager object that implements the interface NM_MANAGER_INTERFACE_PATH.
        This network_manager object can then get all the assoicated devices, and we can
        uses these devices' paths to get the device objects. After finding the target
        device object we can then check if this device is managed by NetworkManager or not.
    """

    bus = dbus.SystemBus()
    is_managed = False
    try:
        # get the network manager proxy
        network_manager_proxy = bus.get_object(
            constants.NM_APP_PATH, constants.NM_MANAGER_OBJ_PATH)
        # get the network manager object that implements the NM_MANAGER_INTERFACE
        network_manager = dbus.Interface(
            network_manager_proxy,
            dbus_interface=constants.NM_MANAGER_INTERFACE_PATH)

        # get all the wireless devices
        devices = network_manager.GetDevices()
        for dev_obj_path in devices:
            # get the device proxy object
            device_proxy = bus.get_object(constants.NM_APP_PATH, dev_obj_path)

            # get the device object that implements the PROPERTIES_IFACE interface
            device = dbus.Interface(device_proxy, dbus_interface=dbus.PROPERTIES_IFACE)

            # check if the device is the target interface
            if device.Get(constants.NM_DEV_INTERFACE_PATH, 'Interface') == interface_name:
                is_managed = device.Get(constants.NM_DEV_INTERFACE_PATH, 'Managed')
                break
    except dbus.exceptions.DBusException:
        # NetworkManager service is not running so the devices must be unmanaged
        pass
    return bool(is_managed)


def interface_property_detector(network_adapter):
    """
    Add appropriate properties of the interface such as supported modes
    and wireless type(wireless)

    :param network_adapter: A NetworkAdapter object
    :type interface_name: NetworkAdapter
    :return: None
    :rtype: None
    """

    supported_modes = pyw.devmodes(network_adapter.card)

    # check for monitor, AP and wireless mode support
    if "monitor" in supported_modes:
        network_adapter.has_monitor_mode = True
    if "AP" in supported_modes:
        network_adapter.has_ap_mode = True

    interface_name = network_adapter.name
    network_adapter.is_managed_by_nm = is_managed_by_network_manager(interface_name)


def generate_random_address():
    """
    Make and return the randomized MAC address

    :return: A MAC address
    :rtype str
    .. warning: The first 3 octets are 00:00:00 by default
    """

    mac_address = constants.DEFAULT_OUI + ":{:02x}:{:02x}:{:02x}".format(random.randint(0, 255),
                                                                         random.randint(0, 255),
                                                                         random.randint(0, 255))
    return mac_address