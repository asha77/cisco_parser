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

def obtain_timezone(config):
    '''
    Extract clock timezone value
    '''

    match = re.search("clock timezone (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not Found"

"""
def obtain_secret_settings(config):
    '''
    Extract enable secret settings
    '''

    match = re.search("enable secret (\d) (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not Found"
"""

def obtain_snmp_version(config):
    '''
    Extract SNMP version and check if it is encrypted (priv)
    '''

    # in Nexus: snmp-server user admin network-admin auth md5 0x661ce46ac35c6d0f8a7b37bbc6afcf2b priv aes-128 0x661ce46ac35c6d0f8a7b37bbc6afcf2b localizedkey

    if ("N9K" in obtain_model(config)):
        match = re.search("snmp-server (.+) auth md5 (.+) priv\s(\w+-\d+)\s(.+)\s(\w+)", config)
        if match:
            return "priv"
        else:
            match = re.search("snmp-server community\s(.+)\sR\w\s(\d+)", config)
            if match:
                return "v2c"+match.group(2).strip()
            else:
                return "Not Found"
    elif (("WS-C" in obtain_model(config)) or ("C1000" in obtain_model(config))):
        match = re.search("snmp-server group (\w+) (\w+) priv(.*)", config)
        if match:
            return "priv "+match.group(2).strip()
        else:
            match = re.search("snmp-server community\s(.+)(\sR\w\s(\d+))*", config)
            if match:
                return "v2c"
            else:
                return "Not Found"
    elif (("C9200" in obtain_model(config)) or ("C9500" in obtain_model(config)) or ("C9300" in obtain_model(config))):
        match = re.search("snmp-server group (\w+) (\w+) priv (.*)", config)
        if match:
            return "priv "+match.group(2).strip()
        else:
            match = re.search("snmp-server community\s(.+)(\sR\w\s(\d+))*", config)
            if match:
                return "v2c"
            else:
                return "Not Found"
    else:
        match = re.search("snmp-server group (\w+) (\w+) priv (.*)", config)
        if match:
            return "priv "+match.group(2).strip()
        else:
            match = re.search("snmp-server community\s(.+)(\sR\w\s(\d+))*", config)
            if match:
                return "v2c"
            else:
                return "Not Found"

def check_source_route(config):
    '''
    Check source-routing disabled
    '''

    match = re.search("no ip source-route", config)
    if match:
        return "Ok"
    else:
        return "Fail"

def check_service_password_encryption(config):
    '''
    Check service password encryption
    '''

    match = re.search("service password-encryption", config)
    if match:
        return "Ok"
    else:
        return "Fail"

def check_weak_service_password_encryption(config):
    '''
    Check weak (reversive) Viginere password hash
    '''

    match = re.search("enable password (.*)", config)
    if match:
        return "Fail"
    else:
        return "Ok"


def check_md5_service_password_encryption(config):
    '''
    Check strong MD5 password hash (5 - md5, 7 - weak)
    '''

    match = re.search("enable secret (\d) (.*)", config)
    if match:
        return str(match.group(1).strip())
    else:
        return "Fail"


def check_ssh_version(config):
    '''
    Check using only ssh version 2
    '''

    match = re.search("ip ssh version (\d)", config)
    if match:
        if (match.group(1).strip() == '2'):
            return "Ok(2)"
        else:
            return "Fail(1)"
    else:
        return "Fail"


def check_logging_buffered(config):
    '''
    Check logging buffered size
    '''

    match = re.search("logging buffered (.*)", config)
    if match:
        return "Ok("+match.group(1).strip()+")"
    else:
        return "Fail"


def check_ssh_timeout(config):
    '''
    Check ssh timeout
    '''

    match = re.search("ip ssh time-out (\d+)", config)
    if match:
        return "Ok("+match.group(1).strip()+")"
    else:
        return "Fail"

def check_boot_network(config):
    '''
    Check boot network configuration
    '''

    match = re.search("boot network (.*)", config)
    if match:
        return "Fail"
    else:
        return "Ok"


def check_service_config(config):
    '''
    Check service config configuration
    '''

    match = re.search("service config", config)
    if match:
        return "Fail"
    else:
        return "Ok"


def check_cns_config(config):
    '''
    Check cns config configuration
    '''

    match = re.search("cns trusted-server config (.*)", config)
    if match:
        return "Fail"
    else:
        return "Ok"

    # new block started here

def check_syslog_timestamp(config):
    '''
    Check syslog format add timestamps to messages
    '''

    match = re.search("service timestamps debug datetime (.*)", config)
    if match:
        return "Ok"
    else:
        return "Fail"


def check_proxy_arp(config):
    '''
    Check for proxy arp configuration
    '''

    match = re.search("no ip proxy-arp", config)
    if match:
        return "Ok"
    else:
        return "Fail"


def check_logging_console(config):
    '''
    Check for console logging configuration (only critical recommended)
    '''

    match = re.search("logging console (\s+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Fail"


def check_logging_syslog(config):
    '''
    Check for logging to syslog configuration (informational recommended)
    '''

    match = re.search("logging trap (\s+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Fail"


def check_log_failures(config):
    '''
    Check for unsuccessfull login attempts to syslog
    '''

    match = re.search("login on-failure log every (\d+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Fail"


def check_log_success(config):
    '''
    Check for success login message to syslog
    '''

    match = re.search("login on-success log", config)
    if match:
        return "Ok"
    else:
        return "Fail"


def check_tcp_keepalives_in(config):
    '''
    Check for keepalives-in option enabled
    '''

    match = re.search("tcp-keepalives-in", config)
    if match:
        return "Ok"
    else:
        return "Fail"

def check_tcp_keepalives_out(config):
    '''
    Check for keepalives-out option enabled
    '''

    match = re.search("service tcp-keepalives-out", config)
    if match:
        return "Ok"
    else:
        return "Fail"


def check_inetd_disable(config):
    '''
    Check for inetd services disable
    '''

    match = re.search("no ip inetd", config)
    if match:
        return "Ok"
    else:
        return "Fail"


def check_bootp_disable(config):
    '''
    Check for bootp protocol disable
    '''

    match = re.search("no ip bootp server", config)
    if match:
        return "Ok"
    else:
        return "Fail"


def check_authentication_retries(config):
    '''
    Check for authentication retries limit
    '''

    match = re.search("ip ssh authentication-retries (\d+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Fail"


def check_weak_local_users_passwords(config):
    '''
    Check for weak passwords for local users
    '''

    match = re.search("username (\s+) password (.*)", config)
    if match:
        return "Fail"
    else:
        return "Ok"


def check_motd_banner(config):
    '''
    Check for banner
    '''

    match = re.search("banner motd (.*)", config)
    if match:
        return "Ok"
    else:
        return "Fail"


def check_accounting_commands(config):
    '''
    Check for commands accounting
    '''

    match = re.search("aaa accounting commands(.+)", config)
    if match:
        return "Ok"
    else:
        return "Fail"


def check_connection_accounting(config):
    '''
    Check for accounting for commands
    '''

    match = re.search("aaa accounting connection(.+)", config)
    if match:
        return "Ok"
    else:
        return "Fail"

def check_exec_commands_accounting(config):
    '''
    Check for accounting for exec commands
    '''

    match = re.search("aaa accounting exec(.+)", config)
    if match:
        return "Ok"
    else:
        return "Fail"

def check_system_accounting(config):
    '''
    Check for system accounting
    '''

    match = re.search("aaa accounting system(.+)", config)
    if match:
        return "Ok"
    else:
        return "Fail"

def check_new_model(config):
    '''
    Check for aaa new-model enabled
    '''

    match = re.search("aaa new-model", config)
    if match:
        return "Ok"
    else:
        return "Fail"

def check_auth_login(config):
    '''
    Check for login authentification
    '''

    match = re.search("aaa authentication login (.+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Fail"

def check_auth_enable(config):
    '''
    Check for authentification enabled
    '''

    match = re.search("aaa authentication enable (.+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Fail"


def get_ntp_servers(config):
    '''
    get ntp servers ip
    '''

    match = re.findall('^ntp server ([0-9]+.[0-9]+.[0-9]+.[0-9]+)', config, re.MULTILINE)
    if match:
        s = ""
        for i in range(len(match)):
            s = s + " "+match[i]+","
        return s[:-1]
    else:
        return "Fail"


    # new block finished here


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


def check_bpduguard(filename):
    '''
    Check bpduguard setting globally or on interface
    '''

    match = re.search("spanning-tree portfast bpduguard(.*)", filename)
    if match:
        return "Ok(glb pf)"
    else:
        match = re.search("spanning-tree bpduguard(.*)", filename)
        if match:
            return "Ок(int)"
        else:
            return "Not Found"


def check_iparp_inspect(filename):
    '''
    Check ip arp inspection settings
    '''

    match = re.search("ip arp inspection", filename)
    if match:
        return "Ок"
    else:
        return "Not Found"


def check_dhcp_snooping(filename):
    '''
    Check dhcp snooping settings
    '''

    match = re.search("ip dhcp snooping", filename)
    if match:
        return "Ок"
    else:
        return "Not Found"


def check_aux(filename):
    '''
    Check aux settings
    '''

    match = re.search("line aux 0\n\sno exec", filename)
    if match:
        return "Ок"
    else:
        return "Not Found"


def check_portsecurity(filename):
    '''
    Check port security settings
    '''

    match = re.findall("switchport port-security(.*)", filename)
    if match:
        return "Ok (" + str(len(match)) + ")"
    else:
        return "Not Found"


def check_stormcontrol(filename):
    '''
    Check port security settings
    '''

    match = re.findall("storm-control(.*)", filename)
    if match:
        return "Ok (" + str(len(match)) + ")"
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

