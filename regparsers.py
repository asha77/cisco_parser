import re


def obtain_stack_members(config):
    match = re.findall("ip address unit (.*)", config)
    if match:
        return len(match)
    else:
        return None


def obtain_hostname(config):
    '''
    Extract device hostname
    '''

    match = re.search("hostname (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not Found"


def obtain_model(config):
    '''
    Extract model number
    '''

    match = re.search("Model \wumber\ *: (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        match = re.search("\wisco (.*) \(.*\) \w* (with )*\d+K\/\d+K bytes of memory.", config)
        if match:
            return match.group(1).strip()
        else:
            match = re.search("\ \ cisco Nexus9000 (.*) Chassis", config)
            if match:
                return "N9K-"+match.group(1).strip()
            else:
                return "Not Found"


def obtain_serial(config):
    '''
    Extract serial number
    '''

    match = re.search("\wystem \werial \wumber\ *: (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        match = re.search("\s*\wrocessor \woard ID (.*)", config)
        if match:
            return match.group(1).strip()
        return "Not Found"


def obtain_domain(config):
    '''
    Extract domain name
    '''

    match = re.search("ip domain[\s\S]name (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not set"


def obtain_software_version(config):
    '''
    Extract software version
    '''

    match = re.search("Version (.*),", config)
    if match:
        return match.group(1).strip()
    else:
        match = re.search("\ *NXOS: version (.*)", config)
        if match:
            return match.group(1).strip()
        else:
            return "Not Found"


def obtain_mng_ip_from_config(filename):
    '''
    Extract mng ip - TODO: need to rethink - return just first ip on interface !!!!!
    '''

    match = re.search(" ip address ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", filename)
    if match:
        return match.group(1).strip()
    else:
        return "Not Found"


def fill_devinfo_from_config(config):
    devinfo = [obtain_hostname(config),
               obtain_mng_ip_from_config(config),
               obtain_domain(config),
               obtain_model(config),
               obtain_serial(config),
               obtain_software_version(config)]
    return devinfo


def get_type_of_sw_from_hostname(hostname):
    '''
    Extract switch type from device hostname
    '''

    match = re.search("\S+asw\S+", hostname)
    if match:
        return "asw"
    else:
        match = re.search("\S+dsw\S+", hostname)
        if match:
            return "dsw"
        else:
            match = re.search("\S*csw\S+", hostname)
            if match:
                return "csw"
            else:
                return "undefined"


def get_num_of_access_int_from_interface_list(ints):
    '''
    Extract num of access interfaces from list of interfaces
    '''
    i: int = 0
    intcount = 0

    for i in range(0, len(ints)):
        if ints[i][4] != "" or ints[i][5] == "access":
            intcount = intcount + 1
    return (intcount)


def get_num_of_trunk_int_from_interface_list(ints):
    '''
    Extract num of trunk interfaces from list of interfaces
    '''

    i: int = 0
    intcount = 0

    for i in range(0, len(ints)):
        if ints[i][5] == "trunk":
            intcount = intcount + 1
    return (intcount)


def get_num_of_dot1x_interfaces(ints):
    '''
    Extract num of interfaces with dot1x settings
    '''
    i: int = 0
    intcount = 0

    for i in range(0, len(ints)):
        if ints[i][11] != "":
            intcount = intcount + 1
    return (intcount)


def get_num_of_ints_with_ip(ints):
    '''
    Extract num of interfaces with ip addresses
    '''
    i: int = 0
    intcount = 0

    for i in range(0, len(ints)):
        if ints[i][2] != "":
            intcount = intcount + 1
    return (intcount)




def get_access_vlan_ids(ints):
    '''
    Extract access vlan id numbers
    Returns set of vlan id values
    '''
    i: int = 0
    vlan_ids = set()
    for i in range(0, len(ints)):
        if ints[i][5] == "access":
            if ints[i][4] != "":
                vlan_ids.add(ints[i][4])
    return (vlan_ids)

def get_native_vlan_ids(ints):
    '''
    Extract native vlan ids on any port
    Returns set of vlan id values
    '''
    i: int = 0
    vlan_ids = set()
    for i in range(0, len(ints)):
        if ints[i][8] != "":
            vlan_ids.add(ints[i][8])
    return (vlan_ids)



def get_voice_vlan_ids(ints):
    '''
    Extract voice vlan ids on access ports
    Returns set of vlan id values
    '''
    i: int = 0
    vlan_ids = set()
    for i in range(0, len(ints)):
        if ints[i][5] == "access":
            if ints[i][6] != "":
                vlan_ids.add(ints[i][6])
    return (vlan_ids)



def get_trunk_vlan_ids(ints):
    '''
    Extract vlan ids on trunk ports
    Returns set of vlan id values
    '''
    i: int = 0
    vlan_ids = set()
    for i in range(0, len(ints)):
        if ints[i][5] == "trunk":
            if ints[i][7] != "":
                vlan_ids.add(ints[i][7])

    if len(vlan_ids) == 0:
        vlan_ids.add("all")
    return (vlan_ids)


def get_num_of_physical_ints(ints):
    '''
    Extract num of physical interfaces from list of interfaces
    '''

    i: int = 0
    intcount = 0

    for i in range(0, len(ints)):
        if is_physical_int(ints[i][0]):
            intcount = intcount + 1
    return (intcount)


def get_num_of_svi_ints(ints):
    '''
    Extract num of svi interfaces from list of interfaces
    '''

    i: int = 0
    intcount = 0

    for i in range(0, len(ints)):
        if is_svi_int(ints[i][0]):
            intcount = intcount + 1
    return (intcount)


def is_physical_int(intname):
    '''
    Check interface is physical
    '''
    if intname.find('Vlan') == -1:
        if intname.find('Loopback') == -1:
            if intname.find('Port-channel') == -1:
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def is_svi_int(intname):
    '''
    Check interface is SVI
    '''

    if intname.find('Vlan') == 0:
        return True
    else:
        return False

def is_portchannel_int(intname):
    '''
    Check interface is port-channel
    '''
    if intname.find('Port-channel') == 0:
        return True
    else:
        return False

def is_loopback_int(intname):
    '''
    Check interface is loopback
    '''
    if intname.find('Loopback') == 0:
        return True
    else:
        return False



def is_logical_int(intname):
    '''
    Check interface is logical (not physical)
    '''
    if is_svi_int(intname) or is_portchannel_int(intname) or is_loopback_int(intname):
        return True
    else:
        return False
