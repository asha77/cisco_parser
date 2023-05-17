import re
import netaddr
import device_detection




def obtain_hostname(config):
    """
    Extract device hostname
    """

    match = re.search('hostname\s(.*)', config)
    if match:
        return match.group(1).strip().replace('"', '')
    else:
        match = re.search('sysname\s(.*)', config)
        if match:
            return match.group(1).strip().replace('"', '')
        else:
            match = re.search('snmp-server\ssysname\s(.*)', config)
            if match:
                return match.group(1).strip().replace('"', '')
            else:
                return "Not Found"


def obtain_timezone(config):
    """
    Extract clock timezone value
    """

    match = re.search("clock timezone (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not set"


def obtain_model(vendor_id, config):
    '''
    Extract model number
    '''
    if vendor_id == 'cisco':
        match = re.search("Model \wumber\ *: (.*)", config)
        if match:
            return match.group(1).strip()
        else:
            # match = re.search("\wisco (.*) \(.*\) \w* (with )*\d+K\/\d+K bytes of memory.", config)
            match = re.search("\wisco (\S+) .* (with)*\d+K\/\d+K bytes of memory.", config)
            if match:
                return match.group(1).strip()
            else:
                match = re.search("\ \ cisco Nexus9000 (.*) Chassis", config)
                if match:
                    return "N9K-"+match.group(1).strip()
                else:
                    match = re.search("ROM: Bootstrap program is Linux", config)
                    if match:
                        return "Cisco IOS vRouter "

    if vendor_id == 'huawei':
        match = re.search("Copyright.*HUAWEI.*\nHUAWEI\s([\w-]+)\s", config)
        if match:
            return match.group(1).strip()

    if vendor_id == 'hpe' or vendor_id == 'hpe_comware' or vendor_id == 'hpe_aruba':
        match = re.search(";\s(\S+)\sConfiguration\sEditor;", config)
        if match:
            return device_detection.get_hp_model_from_pn(match.group(1).strip())
        else:
            match = re.search('System Description "HPE OfficeConnect Switch.+\)\s(\S+),\s.+', config)
            if match:
                return device_detection.get_hp_model_from_pn(match.group(1).strip())
            else:
                match = re.search('\sversion\s(\S+),\sRelease\s(\S+)\n#\n\ssysname\s(\S+)', config)
                if match:
                    return 'hp_switch'

    return "Not found"


def obtain_serial(config):
    '''
    Extract serial number
    '''

    vendor_id = device_detection.obtain_device_vendor_id(config)

    if vendor_id == 'cisco':
        match = re.search("\wystem \werial \wumber\ *: (.*)", config)
        if match:
            return match.group(1).strip()
        else:
            match = re.search("\s*\wrocessor \woard ID (.*)", config)
            if match:
                return match.group(1).strip()
            else:
                match = re.search("\s*ROM Version\s*:\s*\S*\s*Serial\sNumber\s*:\s*(\S+)", config)
                if match:
                    return match.group(1).strip()
                else:
                    match = re.search("\s*Serial\sNumber\s*:\s*(\S+)", config)
                    if match:
                        return match.group(1).strip()
                    else:
                        return "Not Found"

    if vendor_id == 'huawei':
        match = re.search("Slot       Card   Type               Serial-number            Manu-date", config)
        if match:
            match = re.search("\w*Manu-date\n.+\n\d[\s-]*[\w-]*\s*(\w*)", config)
            if match:
                return match.group(1).strip()

        match = re.search("Slot  Sub  Serial-number          Manu-date", config)
        if match:
            match = re.search("\w*Manu-date\n.+\n\d[\s-]*\s*(\w*)", config)
            if match:
                return match.group(1).strip()


        match = re.search("Equipment SN\(ESN\): (\S+)", config)
        if match:
            return match.group(1).strip()

    if vendor_id == 'hpe_comware' or vendor_id == 'hpe_aruba':
        match = re.search("\wystem \werial \wumber\ *: (.*)", config)
        if match:
            return match.group(1).strip()
        else:
            match = re.search("\s*\wrocessor \woard ID (.*)", config)
            if match:
                return match.group(1).strip()
            else:
                match = re.search("\s*ROM Version\s*:\s*\S*\s*Serial\sNumber\s*:\s*(\S+)", config)
                if match:
                    return match.group(1).strip()
                else:
                    match = re.search("\s*Serial\sNumber\s*:\s*(\S+)", config)
                    if match:
                        return match.group(1).strip()
                    else:
                        return "Not Found"
    return "Not Found"


def obtain_domain(config):
    '''
    Extract domain name
    '''

    match = re.search("domain[\s\S-]name (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not set"


def obtain_software_version(os, config):
    '''
    Extract software version
    '''

    # os: cisco_ios_xe, cisco_ios, cisco_ios_xr, arista_eos, cisco_nx_os, aruba_aos-s, hpe_os
    if os == 'cisco_ios_xe':
        match = re.search("Cisco .+ Version ([0-9.()A-Za-z]+)", config)
        if match:
            return match.group(1).strip()
    elif os == 'cisco_ios':
        match = re.search("Cisco .+ Version ([0-9.()A-Za-z]+)", config)
        if match:
            return match.group(1).strip()
    elif os == 'cisco_nx_os':
        match = re.search("\ *NXOS: version (.*)", config)
        if match:
            return match.group(1).strip()
    elif os == 'EOS':
        match = re.search("Software image version: (.*)", config)
        if match:
            return match.group(1).strip()
    elif os == 'aruba_aos-s':
        match = re.search("; \S+ Configuration Editor; Created on release #(\S+)", config)
        # match = re.search("\s*Software revision\s*:\s*(\S+)", config)
        if match:
            return match.group(1).strip()
    elif os == 'huawei_vrp':
        match = re.search("VRP \(R\) software, Version (.*)", config)

        if match:
            return match.group(1).strip()
    else:
        return "Not Found"


def obtain_mng_ip_from_filename(filename):
    '''
    Extract mng ip from filename
    '''

    # ip default-gateway 10.2.254.1
    # Gateway of last resort is 10.2.220.1 to network 0.0.0.0
    # Default gateway is 10.2.254.1

    gw_match = re.search("([0-9]+.[0-9]+.[0-9]+.[0-9]+)", filename)
    if gw_match:
        return gw_match.group(1).strip()
    else:
        return "Not Found"


def obtain_mng_ip_from_config(device, config):
    '''
    Extract mng ip - TODO: situations like "Gateway of last resort is 0.0.0.0 to network 0.0.0.0" - on routers not handled correctly (Not found)
    '''

    # ip default-gateway 10.2.254.1
    # Gateway of last resort is 10.2.220.1 to network 0.0.0.0
    # Default gateway is 10.2.254.1

    if device['os'] == 'cisco_ios_xe' or device['os'] == 'cisco_ios' or device['os'] == 'cisco_ios_xr' or device['os'] == 'cisco_nx_os':
        gw_match = re.search("Gateway of last resort is ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
        if gw_match:
            gwip = netaddr.IPAddress(gw_match.group(1).strip())
        else:
            gw_match = re.search("Default gateway is ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
            if gw_match:
                gwip = netaddr.IPAddress(gw_match.group(1).strip())
            else:
                gw_match = re.search("ip default-gateway ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
                if gw_match:
                    gwip = netaddr.IPAddress(gw_match.group(1).strip())
                else:
                    gwip = "0.0.0.0"    # Gateway not found, fake gwip

        match = re.findall("\sip address ([0-9]+.[0-9]+.[0-9]+.[0-9]+) ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
        found = False
        if match:
            for i in range(len(match)):
                ip = netaddr.IPNetwork(match[i][0])
                ip.netmask = match[i][1]
                if gwip in ip:
                    found = True
                    return match[i][0]
            if found == False:
                return "Not Found"
        else:
            return "Not Found"


    if device['os'] == 'huawei_vrp':
        gw_match = re.search("ip route-static 0.0.0.0 0.0.0.0 ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
        if gw_match:
            gwip = netaddr.IPAddress(gw_match.group(1).strip())
        else:
            gw_match = re.search("^\s+0.0.0.0\/0\s+\w+\s+\d+\s+\d+\s+\w+\s+([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
            if gw_match:
                gwip = netaddr.IPAddress(gw_match.group(1).strip())
            else:
                gwip = "0.0.0.0"    # Gateway not found, fake gwip

        match = re.findall("\s+ip address ([0-9]+.[0-9]+.[0-9]+.[0-9]+) ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
        found = False
        if match:
            for i in range(len(match)):
                ip = netaddr.IPNetwork(match[i][0])
                ip.netmask = match[i][1]
                if gwip in ip:
                    found = True
                    return match[i][0]
            if found == False:
                return "Not Found"
        else:
            return "Not Found"

    # aruba_aos-s, hpe_os
    if device['os'] == 'aruba_aos-s':
        gw_match = re.search("ip route 0.0.0.0 0.0.0.0\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
        if gw_match:
            gwip = netaddr.IPAddress(gw_match.group(1).strip())
        else:
            gw_match = re.search("\s*ip default-gateway\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
            if gw_match:
                gwip = netaddr.IPAddress(gw_match.group(1).strip())
            else:
                gwip = "0.0.0.0"    # Gateway not found, fake gwip

        match = re.findall("\s+ip address\s([0-9]+.[0-9]+.[0-9]+.[0-9]+) ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
        found = False
        if match:
            for i in range(len(match)):
                ip = netaddr.IPNetwork(match[i][0])
                ip.netmask = match[i][1]
                if gwip in ip:
                    found = True
                    return match[i][0]
            if found == False:
                return "Not Found"
        else:
            return "Not Found"

    if device['os'] == 'hpe_os':
        match = re.search("\s*network parms\s([0-9]+.[0-9]+.[0-9]+.[0-9]+).*", config)
        if match:
            return match.group(1).strip()

    if device['os'] == 'hpe_comware':       # TODO: check if two default gateways present
        gw_match = re.search("\s+ip route-static 0.0.0.0 0.0.0.0\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
        if gw_match:
            gwip = netaddr.IPAddress(gw_match.group(1).strip())

        match = re.findall("\s+ip address\s([0-9]+.[0-9]+.[0-9]+.[0-9]+) ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", config)
        found = False
        if match:
            for i in range(len(match)):
                ip = netaddr.IPNetwork(match[i][0])
                ip.netmask = match[i][1]
                if gwip in ip:
                    found = True
                    return match[i][0]
            if found == False:
                return "Not Found"
        else:
            return "Not Found"

    return "Not Found"      # if nothing found


def fill_devinfo_to_model_from_config(empty_device, config, file):
    vendor_id =  device_detection.obtain_device_vendor_id(config)
    empty_device['vendor_id'] = vendor_id
    empty_device['vendor'] = device_detection.vendor_id_to_vendor(vendor_id)
    empty_device['family'] = device_detection.obtain_device_family(vendor_id, config)
    empty_device['os'] = device_detection.obtain_device_os(vendor_id, config)
    empty_device['config_filename'] = file
    empty_device['hostname'] = obtain_hostname(config)
    empty_device['mgmt_ipv4_from_filename'] = obtain_mng_ip_from_filename(file)
    empty_device['mgmt_v4_autodetect'] = obtain_mng_ip_from_config(empty_device, config)
    empty_device['domain_name'] = obtain_domain(config)
    empty_device['model'] = obtain_model(vendor_id, config)
    empty_device['serial'] = obtain_serial(config)
    empty_device['sw_version'] = obtain_software_version(empty_device['os'], config)
    return empty_device


def get_type_of_sw_from_hostname(hostname):
    '''
    Extract switch type from device hostname (if any naming convention exist)
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


def get_number_of_acc_int(interfaces):
    '''
    Extract num of access interfaces from list of interfaces
    '''
    intcount = 0

    for inter in interfaces:
        if inter['switchport_mode'] == 'access':
            intcount = intcount + 1

    return intcount


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


def get_number_of_trunk_int(ints):
    '''
    Extract num of trunk interfaces from list of interfaces
    '''

    intcount = 0

    for inter in ints:
        if inter['switchport_mode'] == 'trunk':
            intcount = intcount + 1
    return intcount


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


def get_number_of_dot1x_ints(ints):
    '''
    Extract num of interfaces with dot1x settings
    '''
    intcount = 0

    for inter in ints:
        if (not inter['dot1x_mab'] == '') or (not inter['dot1x_auth_order'] == '') or (not inter['dot1x_auth_prio'] == '') or (not inter['dot1x_auth_port_control'] == ''):
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


def get_number_of_ints_with_ip(ints):
    '''
    Extract num of interfaces with ip addresses
    '''
    i: int = 0
    intcount = 0

    for inter in ints:
        if not inter['ipv4'] == '':
            intcount = intcount + 1
    return intcount


def get_access_vlan_ids(ints):
    '''
    Extract access vlan id numbers
    Returns set of vlan id values
    '''

    vlan_ids = set()
    for inter in ints:
        if inter['switchport_mode'] == 'access':
            if not inter['access_vlan'] == '':
                vlan_ids.add(inter['access_vlan'])
    return vlan_ids


def get_access_vlans(device):
    '''
    Extract access vlan id numbers
    Returns set of vlan id values
    '''

#    vlan_ids = set()
    vlan_ids = {}

    for interface in device['interfaces']:
        if interface['switchport_mode'] == 'access':
            if not interface['access_vlan'] == '':
                try:
                    vlan_ids[int(interface['access_vlan'])] = device['vlans'][int(interface['access_vlan'])]
                except KeyError:
                    vlan_ids[int(interface['access_vlan'])] = 'not in database'
    return vlan_ids



def get_native_vlan_ids(ints):
    '''
    Extract native vlan ids on any port
    Returns set of vlan id values
    '''

    vlan_ids = set()

    for inter in ints:
        if not inter['native_vlan'] == '':
            vlan_ids.add(inter['native_vlan'])
    return vlan_ids


def get_voice_vlan_ids(ints):
    '''
    Extract voice vlan ids on access ports
    Returns set of vlan id values
    '''

    vlan_ids = set()

    for inter in ints:
        if inter['switchport_mode'] == 'access':
            if not inter['voice_vlan'] == '':
                vlan_ids.add(inter['voice_vlan'])
    return vlan_ids


def get_trunk_vlan_ids(ints):
    '''
    Extract vlan ids on trunk ports
    Returns set of vlan id values
    '''
    i: int = 0
    vlan_ids = set()
    for inter in ints:
        if inter['switchport_mode'] == 'trunk':
            if inter['trunk_vlan_ids'] != '':
                vlan_ids.add(inter['trunk_vlan_ids'])
            else:
                vlan_ids.add("all")
    return vlan_ids


def get_vlan_ids_on_trunk(trunk_config):
    '''
    Extract vlan ids on trunk ports
    Returns set of vlan id values
    '''
    i: int = 0
    ids = []
    vlan_ids = set()

    trunk_config = trunk_config.replace(' ', '')
    ids = trunk_config.split(',')
    vlan_ids = ids

    if vlan_ids[0] != "":
        return vlan_ids
    else:
        vlan_ids[0] = "all"
        return vlan_ids



def get_all_vlan_ids_from_trunk(ints):
    '''
    Get all vlan ids fron all trunk ports
    Returns set of vlan id values
    '''

    vlan_ids = set()

    for inter in ints:
        if inter['switchport_mode'] == 'trunk':
            ids = inter['trunk_vlan_ids']
            if len(ids) > 0:
                for i in range(0, len(ids)):
                    vlan_ids.add(ids[i])
    return vlan_ids


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


def get_number_of_physical_ints(interfaces):
    '''
        Extract number of physical interfaces from list of interfaces
    '''
    intcount = 0

    for inter in interfaces:
        if is_physical_interface(inter['int_type']):
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
    return intcount


def get_number_of_svis(ints):
    '''
    Extract num of svi interfaces from list of interfaces
    '''

    i: int = 0
    intcount = 0

    for inter in ints:
        if inter['int_type'] == 'svi':
            intcount = intcount + 1
    return intcount


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


def is_physical_interface(inttype):
    '''
    Check interface type to be physical
    '''
    if inttype == 'ethernet':
        return True
    elif inttype == 'serial':
        return True
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


def get_only_name(name):
    '''
    Cut domain name from device name
    '''

    if (not name.find('.') == -1):
        return name[0:name.find('.')]
    else:
        return name


def strip_cisco_from_cdp_name(name):
    '''
    Cut "cisco " name from device name
    '''

    if (not name.find('cisco ') == -1):
        return name[len('cisco '):]
    elif (not name.find('Cisco ') == -1):
        return name[len('Cisco '):]
    else:
        return name


def strip_serial_from_cdp_name(name):
    '''
    Cut serial number "(FART34598BNY)" from nexus device name
    '''

    if (name.find('(') == -1):
        return name
    elif (not name.find('(') == -1):
        return name[:len(name)-13]
    else:
        return name



def get_num_of_up_access_interfaces(empty_device):
    num = 0
    for int in empty_device['interfaces']:
        if int['switchport_mode'] == 'access':
            if int['status'] == 'connected':
                num = num + 1
    return num


def get_number_of_connected_access_ints(ints):
    num = 0
    for inter in ints:
        if inter['status'] == 'connected' and inter['switchport_mode'] == 'access':
            num = num + 1
    return num


def get_number_of_connected_trunk_ints(ints):
    num = 0
    for inter in ints:
        if inter['status'] == 'connected' and inter['switchport_mode'] == 'trunk':
            num = num + 1
    return num


def get_number_of_connected_l3_ints(ints):
    num = 0
    for inter in ints:
        if ((inter['status'] == 'connected') and (inter['int_type'] == 'ethernet' or inter['int_type'] == 'serial') and (not inter['ipv4'] == '')):
            num = num + 1
    return num


def get_interface_type_by_name(int_name):
    '''
        Returns type of interface: { ethernet, svi, po, tunnel, loopback, not set }
        based on interface name i.e. "GigabitEthernet"
    '''

    if 'Ethernet' in int_name:
        return 'ethernet'
    elif 'Port-channel' in int_name:
        return 'po'
    elif 'Loopback' in int_name:
        return 'loopback'
    elif 'Vlan' in int_name:
        return 'svi'
    elif 'Serial' in int_name:
        return 'serial'
    elif 'Tunnel' in int_name:
        return 'tunnel'
    else:
        return 'unknown'


def ip_mask_to_prefix(ip, octet_mask):
    if octet_mask != '' and ip != '':
        ip = netaddr.IPNetwork(ip)
        ip.netmask = octet_mask
        return str(ip.ip) + '/' + str(ip.prefixlen)
    else:
        return ''

