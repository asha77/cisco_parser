import re
import netaddr


def obtain_stack_members(config):
    match = re.findall("ip address unit (.*)", config)
    if match:
        return len(match)
    else:
        return None


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
    Extract SNMP version
    '''

    match = re.search("snmp-server group", config)
    if match:           # SNMP v3 with secured auth
        return "v3"
    else:
        match = re.search("snmp-server community", config)
        if match:       # SNMP v2c
            return "v2c"
        else:
            return "Not set"


def check_snmpv3_authencr(config):
    '''
    Get SNMPv3 mode
    '''

    # in SNMPv3:
    # noAuthNoPriv — пароли передаются в открытом виде, конфиденциальность данных отсутствует;
    # authNoPriv — аутентификация без конфиденциальности;
    # authPriv — аутентификация и шифрование, максимальный уровень защищенности.

    match = re.search("snmp-server group (\w+) v3 (\w+)\s(.*)", config)        # user v3 with priv
    if match:           # SNMP v3 with secured auth
        return match.group(2).strip()
    else:
        return "Not set"


def check_snmpv2_ACL(config):
    '''
    Check SNMPv2 has access ACL
    '''

    match = re.search("snmp-server community\s(.+)\sR\w\s(\d+)", config)
    if match:       # SNMP v2c
        return match.group(2).strip()
    else:
        return "Not set"


def obtain_snmp_user_encr(config):
    '''
    Check SNMP v3 user password md5 hashed
    '''
    # snmp-server user admin network-admin auth md5 0x661ce46ac35c6d0f8a7b37bbc6afcf2b priv aes-128 0x661ce46ac35c6d0f8a7b37bbc6afcf2b localizedkey

    match = re.search("snmp-server user (\s+) v3", config)        # user v3 with md 5 and priv
    if match:           # SNMP v3 user present
        match = re.search("snmp-server (.+) v3 auth md5 (.+) priv\s(aes.+)\s(.*)", config)  # user v3 with md 5 and priv
        if match:  # SNMP v3 with secured auth
            return "Ok"
        else:
            return "Fail"
    else:
        return "Not set"


def check_source_route(config):
    '''
    Check source-routing disabled
    '''

    match = re.search("no ip source-route", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_service_password_encryption(config):
    '''
    Check service password encryption
    '''

    match = re.search("no service password-encryption", config)
    if match:
        return "Fail"
    else:
        match = re.search("service password-encryption", config)
        if not match:
            return "Not set"
        else:
            return "Ok"


def check_weak_enable_password_encryption(config):
    '''
    Check weak (reversive) Viginere password hash for enable
    '''

    match = re.search("enable password (\d*)", config)
    if match:
        return "Fail("+str(match.group(1).strip())+")"
    else:
        return "Not set"


def check_enable_password_encryption_method(config):
    '''
    Check enable password encryption method (5 - md5, 7 - weak, 9 - best)
    '''
    match = re.search("enable secret (\d) (.*)", config)
    if match:
        if match.group(1).strip() == "7":
            return "Fail(7)"
        elif match.group(1).strip() == "4":
            return "Fail(4)"
        elif match.group(1).strip() == "9":
            return "Best(9)"
        elif match.group(1).strip() == "5":
            return "Ok(5)"
        elif match.group(1).strip() == "8":
            return "Ok(8)"
        else:
            return str(match.group(1).strip())
    else:
        return "Not set"


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
        return "Not set"


def check_logging_buffered(config):
    '''
    Check logging buffered size
    '''
    match = re.search("logging buffered (.*)", config)
    if match:
        return "Ok("+match.group(1).strip()+")"
    else:
        return "Not set"


def check_ssh_timeout(config):
    '''
    Check ssh timeout
    '''

    match = re.search("ip ssh time-out (\d+)", config)
    if match:
        return "Ok("+match.group(1).strip()+")"
    else:
        return "Not set"


def check_boot_network(config):
    '''
    Check boot network configuration
    '''

    match = re.search("no boot network", config)
    if match:
        return "Ok"
    else:
        match = re.search("boot network (.*)", config)
        if match:
            return "Fail"
        else:
            return "Not set"


def check_service_config(config):
    '''
    Check service config configuration
    '''

    match = re.search("no service config", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_cns_config(config):
    '''
    Check cns config configuration
    '''

    match = re.search("cns trusted-server config (.*)", config)
    if match:
        return "Fail"
    else:
        return "Ok"


def check_syslog_timestamp(config):
    '''
    Check syslog format add timestamps to messages
    '''

    match = re.search("service timestamps debug datetime (.*)", config)
    if match:
        return "Ok"
    else:
        return "Not set"


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

    match = re.search("logging console (\w+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not set"


def check_logging_syslog(config):
    '''
    Check for logging to syslog configuration (informational recommended)
    '''

    match = re.search("logging trap (\w+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not set"


def check_log_failures(config):
    '''
    Check for unsuccessfull login attempts to syslog
    '''

    match = re.search("login on-failure log every (\d+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not set"


def check_log_success(config):
    '''
    Check for success login message to syslog
    '''

    match = re.search("login on-success log", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_tcp_keepalives_in(config):
    '''
    Check for keepalives-in option enabled
    '''

    match = re.search("service tcp-keepalives-in", config)
    if match:
        return "Ok"
    else:
        return "Not set"

def check_tcp_keepalives_out(config):
    '''
    Check for keepalives-out option enabled
    '''

    match = re.search("service tcp-keepalives-out", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_inetd_disable(config):
    '''
    Check for inetd services disable
    '''

    match = re.search("no ip inetd", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_bootp_disable(config):
    '''
    Check for bootp protocol disable
    '''

    match = re.search("no ip bootp server", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_authentication_retries(config):
    '''
    Check for authentication retries limit
    '''

    match = re.search("ip ssh authentication-retries (\d+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not set"


def check_weak_local_users_passwords(config):
    '''
    Check for weak passwords for local users
    '''

    match = re.search("username (\S+) password (\d*)", config)
    if match:
        return "Fail(" + match.group(2).strip() + ")"
    else:
        match = re.search("username (\S+) secret (\d*)", config)
        if match:
            return "Ok(" + match.group(2).strip() + ")"
        else:
            return "Not set"


def check_motd_banner(config):
    '''
    Check for banner
    '''

    match = re.search("banner motd (.*)", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_accounting_commands(config):
    '''
    Check for commands accounting
    '''

    match = re.search("aaa accounting commands(.+)", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_connection_accounting(config):
    '''
    Check for accounting for connections
    '''

    match = re.search("aaa accounting connection(.+)", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_exec_commands_accounting(config):
    '''
    Check for accounting for exec commands
    '''

    match = re.search("aaa accounting exec(.+)", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_system_accounting(config):
    '''
    Check for system accounting
    '''

    match = re.search("aaa accounting system(.+)", config)
    if match:
        return "Ok"
    else:
        return "Not set"

def check_new_model(config):
    '''
    Check for aaa new-model enabled
    '''

    match = re.search("aaa new-model", config)
    if match:
        return "Ok"
    else:
        return "Not set"


def check_auth_login(config):
    '''
    Check for login authentification
    '''

    match = re.search("aaa authentication login (.+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not set"


def check_auth_enable(config):
    '''
    Check for authentification enabled
    '''

    match = re.search("aaa authentication enable (.+)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not set"


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
        match = re.findall('^ntp server vrf [\w.-_]* ([0-9]+.[0-9]+.[0-9]+.[0-9]+)', config, re.MULTILINE)
        if match:
            s = ""
            for i in range(len(match)):
                s = s + " "+match[i]+","
            return s[:-1]
        else:
            return "Not set"


def obtain_model(config):
    '''
    Extract model number
    '''
    match = re.search("Model \wumber\ *: (.*)", config)
    if match:
        return match.group(1).strip()
    else:
#        match = re.search("\wisco (.*) \(.*\) \w* (with )*\d+K\/\d+K bytes of memory.", config)
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
                else:
                    match = re.search(";\s(\S+)\sConfiguration\sEditor;", config)
                    if match:
                        return get_hp_model_from_pn(match.group(1).strip())
                    else:
                        match = re.search('System Description "HPE OfficeConnect Switch.+\)\s(\S+),\s.+', config)
                        if match:
                            return get_hp_model_from_pn(match.group(1).strip())
                        else:
                            match = re.search('\sversion\s(\S+),\sRelease\s(\S+)\n#\n\ssysname\s(\S+)', config)
                            if match:
                                return 'hp_switch'
                            else:
                                return "Not found"


def get_hp_model_from_pn(partnumber):
    if partnumber == 'J9781A':
        return 'HPE Aruba 2530-48'
    if partnumber == 'J9775A':
        return 'HPE Aruba 2530-48G'
    if partnumber == 'J9773A':
        return 'HPE Aruba 2530-24G-PoE+'
    if partnumber == 'J9782A':
        return 'HPE Aruba 2530-24'
    if partnumber == 'JL385A':
        return 'HPE 1920S-24G-2SFP-PoE+'
    if partnumber == 'J9774A':
        return 'HPE 2530-8G-PoE+'
    if partnumber == 'J9783A':
        return 'HPE Aruba 2530-8FE'
    if partnumber == 'J9780A':
        return 'HPE Aruba 2530-8-PoE+'
    if partnumber == 'J9776A':
        return 'HPE Aruba 2530-24G-PoE+'
    if partnumber == 'J9772A':
        return 'HPE Aruba 2530-48G-PoE+'
    if partnumber == 'J9778A':
        return 'HPE Aruba 2530-48G-PoE+'
    if partnumber == 'J9779A':
        return 'HPE Aruba 2530-24-PoE+'
    if partnumber == 'hpStack_WC':
        return 'HPE Aruba-VSF-2930F'
    else:
        return 'HP unknown'


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


def obtain_domain(config):
    '''
    Extract domain name
    '''

    match = re.search("ip domain[\s\S]name (.*)", config)
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
    elif os == 'aruba_aos-s':
        match = re.search("; \S+ Configuration Editor; Created on release #(\S+)", config)
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


def check_bpduguard(filename):
    '''
    Check bpduguard setting globally or on interface
    '''
    # spanning-tree portfast edge bpduguard default

    match = re.search("spanning-tree portfast (\w*)(\s*)bpduguard(.*)", filename)
    if match:
        return "Ok(glb pf)"
    else:
        match = re.search(" spanning-tree bpduguard(.*)", filename)
        if match:
            return "Ок(int)"
        else:
            return "Not set"


def check_iparp_inspect(filename):
    '''
    Check ip arp inspection settings
    '''

    match = re.search("ip arp inspection", filename)
    if match:
        return "Ок"
    else:
        return "Not set"


def check_dhcp_snooping(filename):
    '''
    Check dhcp snooping settings
    '''

    match = re.search("ip dhcp snooping", filename)
    if match:
        return "Ок"
    else:
        return "Not set"


def check_aux(filename):
    '''
    Check aux settings
    '''
    match = re.search("line aux", filename)
    if match:
        match = re.search("line aux 0\n\sno exec", filename)
        if match:
            return "Ок"
        else:
            return "Not set"
    else:
        return "No aux"


def check_portsecurity(filename):
    '''
    Check port security settings
    '''

    match = re.findall(" switchport port-security(.*)", filename)
    if match:
        return "Ok (" + str(len(match)) + ")"
    else:
        return "Not set"


def check_stormcontrol(filename):
    '''
    Check port security settings
    '''

    match = re.findall("storm-control(.*)", filename)
    if match:
        return "Ok (" + str(len(match)) + ")"
    else:
        return "Not set"


def fill_devinfo_to_model_from_config(empty_device, config, file):
    empty_device['family'] = obtain_device_family(config)
    empty_device['os'] = obtain_device_os(config)
    empty_device['config_filename'] = file
    empty_device['hostname'] = obtain_hostname(config)
    empty_device['mgmt_ipv4_from_filename'] = obtain_mng_ip_from_filename(file)
    empty_device['mgmt_v4_autodetect'] = obtain_mng_ip_from_config(empty_device, config)
    empty_device['domain_name'] = obtain_domain(config)
    empty_device['model'] = obtain_model(config)
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


def obtain_device_family(config):
        '''
        Extract device family: cisco_catalyst, cisco_isr, cisco_nexus, arista_switch, cisco_vrouter, huawei_ce, huawei_s, huawei_ar
        '''
        match = re.search("Model\s+\wumber\s*:\s+(.*)", config)
        if match:
            return 'cisco_catalyst'
        else:
            match = re.search("\wisco\s+(\S+)\s+.*\s+(with)*\d+K\/\d+K\sbytes\sof\smemory.", config)
            if match:
                return 'cisco_isr'
            else:
                match = re.search("\s+cisco Nexus9000 (.*) Chassis", config)
                if match:
                    return 'cisco_nexus'
                else:
                    match = re.search("Arista vEOS", config)
                    if match:
                        return 'arista_switch'
                    else:
                        match = re.search("ROM: Bootstrap program is Linux", config)
                        if match:
                            return 'cisco_vrouter'
                        else:
                            match = re.search('(Quidway|HUAWEI)\s(\S+)\s+Routing\sSwitch\S*', config)
                            if match:
                                return 'huawei_s'
                            else:
                                match = re.search('HUAWEI\sCE(\S+)\s+uptime\S*', config)
                                if match:
                                    return 'huawei_ce'
                                else:
                                    match = re.search('Huawei\s(\S+)\s+Router\s\S*', config)
                                    if match:
                                        return 'huawei_ar'
                                    else:
                                        match = re.search(';\s(\S+)\sConfiguration\sEditor;', config)
                                        if match:
                                            return 'hpe_aruba_switch'
                                        else:
                                            match = re.search('System Description "HPE(.+)', config)
                                            if match:
                                                return 'hpe_comware_switch'
                                            else:
                                                match = re.search('\sversion\s(\S+),\sRelease\s(\S+)\n#\n\ssysname\s(\S+)', config)
                                                if match:
                                                    return 'hpe_switch2'
                                                else:
                                                    return "Not Found"


def obtain_device_os(config):
    '''
    Extract software family from show version: cisco_ios_xe, cisco_ios, cisco_ios_xr, arista_eos, cisco_nx_os, huawei_vrp, aruba_aoscx
    '''
    match = re.search("Cisco IOS.XE .oftware", config)
    if match:
        return 'cisco_ios_xe'
    else:
        match = re.search("Cisco Nexus Operating System", config)
        if match:
            return 'cisco_nx_os'
        else:
            match = re.search("Cisco IOS Software", config)
            if match:
                return 'cisco_ios'
            else:
                match = re.search("Arista", config)
                if match:
                    return 'arista_eos'
                else:
                    match = re.search("Huawei Versatile Routing Platform", config)
                    if match:
                        return 'huawei_vrp'
                    else:
                        match = re.search(';\s(\S+)\sConfiguration\sEditor;', config)
                        if match:
                            return 'aruba_aos-s'
                        else:
                            match = re.search('!System\sDescription\s"HPE(.+)', config)
                            if match:
                                return 'hpe_os'
                            else:
                                match = re.search('\sversion\s(\S+),\sRelease\s(\S+)\n#\n\ssysname\s(\S+)', config)
                                if match:
                                    return 'hpe_comware'
                                else:
                                    return "Not Found"

