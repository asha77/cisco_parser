
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

