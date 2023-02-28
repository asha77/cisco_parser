import textfsm
from regparsers import *
#from cisco_parser import all_interfaces


def get_cdp_neighbours(config, curr_path, file, devinfo):
    nei_template = open(curr_path + '\\nrt_cdp_nei.template')
    fsm = textfsm.TextFSM(nei_template)

    fsm.Reset()
    neighbours = fsm.ParseText(config)
    all_neighbours = []
    lastindex = 0
    i = 0

    if devinfo[2] == "Not set":
        dev_id = devinfo[0]
    else:
        dev_id = devinfo[0] + '.' + devinfo[2]

    for i in range(lastindex, len(neighbours)):
        all_neighbours.append([])
        all_neighbours[len(all_neighbours) - 1].append(file)        # ConfigFile
        all_neighbours[len(all_neighbours) - 1].append(dev_id)      # Source hostname
        all_neighbours[len(all_neighbours) - 1].append(devinfo[3])  # Source Model
        all_neighbours[len(all_neighbours) - 1].append(devinfo[1])  # Source Mng IP
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][4])    # Source port
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][1])    # Dest hostname
        all_neighbours[len(all_neighbours) - 1].append(strip_cisco_from_cdp_name(neighbours[i][3]))   # Dest Model
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][2])    # Dest IP
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][5])    # Dest portn

    if i != 0:
        lastindex = i + 1

    nei_template.close()
    return all_neighbours


def get_cdp_neighbours_to_model(devindex, config, curr_path):
    nei_template = open(curr_path + '\\nrt_cdp_nei.template')
    fsm = textfsm.TextFSM(nei_template)
    fsm.Reset()
    neighbours = fsm.ParseText(config)
    nei_template.close()

    lastindex = 0

    if devices[devindex]['domain_name'] == "Not set":
        dev_id = devices[devindex]['hostname']
    else:
        dev_id = devices[devindex]['hostname'] + '.' + devices[devindex]['domain_name']

    for i in range(lastindex, len(neighbours)):
        cdp_record = {'local_id': dev_id,
                      'local_model': devices[devindex]['model'],
                      'local_ip_addr': devices[devindex]['mgmt_ipv4_from_filename'],
                      'local_interface': neighbours[i][4],
                      'remote_id': neighbours[i][1],
                      'remote_model': strip_cisco_from_cdp_name(neighbours[i][3]),
                      'remote_ip_addr': neighbours[i][2],
                      'remote_interface': neighbours[i][5]
                      }

        devices[0]['cdp_neighbours'].append(cdp_record)
    return


def get_vrfs(config, curr_path, file, devinfo):
    nei_template = open(curr_path + '\\nrt_cdp_nei.template')
    fsm = textfsm.TextFSM(nei_template)

    fsm.Reset()
    neighbours = fsm.ParseText(config)
    all_neighbours = []
    lastindex = 0
    i = 0

    for i in range(lastindex, len(neighbours)):
        all_neighbours.append([])
        all_neighbours[len(all_neighbours) - 1].append(file)
        all_neighbours[len(all_neighbours) - 1].append(devinfo[0] + '.' + devinfo[2])
        all_neighbours[len(all_neighbours) - 1].append(devinfo[3])
        all_neighbours[len(all_neighbours) - 1].append(devinfo[1])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][4])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][1])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][3])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][2])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][5])
    if i != 0:
        lastindex = i + 1

    nei_template.close()
    return all_neighbours


def get_interfaces_config(config, curr_path, file, devinfo):
#    global all_interfaces

    interfaces = []
    int_template = open(curr_path + '\\nrt_interfaces_config.template')
    fsm = textfsm.TextFSM(int_template)
    fsm.Reset()
    interfaces = fsm.ParseText(config)
    int_template.close()

    interfaces_configuration = []
    lastindex = 0
    i = 0
    j = 0
    vlan_id = 0

    # interfaces_configuration
    # [0] - file
    # [1] - hostname
    # [2] - type of switch (asw, dsw, csw, undefined)
    # [3] - number of physical interfaces
    # [4] - number of SVI interfaces
    # [5] - number of access interfaces
    # [6] - number of trunk interfaces
    # [7] - number of access ports with dot1x
    # [8] - number of ip addresses
    # [9] - list of access vlan(s)
    # [10] - list of native vlan(s)
    # [11] - list of voice vlan(s)
    # [12] - list of vlan(s) on trunks
    # [13] - all vlan from vlan database
    # [14] - vlan id of users vlan
    # [15] - vlan id of iot_toro vlan
    # [16] - vlan id of media_equip vlan
    # [17] - vlan id of off_equip vlan
    # [18] - vlan id of admin vlan
    if devinfo[2] == "Not set":
        dev_id = devinfo[0]
    else:
        dev_id = devinfo[0] + '.' + devinfo[2]

    interfaces_configuration.append(file)
    interfaces_configuration.append(dev_id)
    interfaces_configuration.append(get_type_of_sw_from_hostname(devinfo[0]))
    interfaces_configuration.append(get_num_of_physical_ints(interfaces))
    interfaces_configuration.append(get_num_of_svi_ints(interfaces))
    interfaces_configuration.append(get_num_of_access_int_from_interface_list(interfaces))
    interfaces_configuration.append(get_num_of_trunk_int_from_interface_list(interfaces))
    interfaces_configuration.append(get_num_of_dot1x_interfaces(interfaces))
    interfaces_configuration.append(get_num_of_ints_with_ip(interfaces))
    interfaces_configuration.append(get_access_vlan_ids(interfaces))
    interfaces_configuration.append(get_native_vlan_ids(interfaces))
    interfaces_configuration.append(get_voice_vlan_ids(interfaces))
    interfaces_configuration.append(get_trunk_vlan_ids(interfaces))

    vlans_from_config = get_vlan_config(config, curr_path)
    interfaces_configuration.append(vlans_from_config)

    all_interfaces.append(interfaces)

    """
    fill vlan id for vlans with names   
     - users
     - iot_toro
     - media_equip
     - off_equip
     - admin
    """

    vlan_id = "0"
    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'users':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'iot_toro':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'media_equip':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'off_equip':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'admin':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    return interfaces_configuration


def get_interfaces_config_to_model(devindex, config, curr_path):
#    global all_interfaces
    interfaces = []
    int_template = open(curr_path + '\\nrt_interfaces_config.template')
    fsm = textfsm.TextFSM(int_template)
    fsm.Reset()
    interfaces = fsm.ParseText(config)
    int_template.close()

    interfaces_configuration = []
    lastindex = 0
    i = 0
    j = 0
    vlan_id = 0

    # interfaces_configuration
    # [0] - file
    # [1] - hostname
    # [2] - type of switch (asw, dsw, csw, undefined)
    # [3] - number of physical interfaces
    # [4] - number of SVI interfaces
    # [5] - number of access interfaces
    # [6] - number of trunk interfaces
    # [7] - number of access ports with dot1x
    # [8] - number of ip addresses
    # [9] - list of access vlan(s)
    # [10] - list of native vlan(s)
    # [11] - list of voice vlan(s)
    # [12] - list of vlan(s) on trunks
    # [13] - all vlan from vlan database
    # [14] - vlan id of users vlan
    # [15] - vlan id of iot_toro vlan
    # [16] - vlan id of media_equip vlan
    # [17] - vlan id of off_equip vlan
    # [18] - vlan id of admin vlan


    if devices[devindex]['domain_name'] == "Not set":
        dev_id = devices[devindex]['hostname']
    else:
        dev_id = devices[devindex]['hostname'] + '.' + devices[devindex]['domain_name']

    interfaces_status = get_int_status(config)

    check_management_int()

    interfaces_status

    for interf in interfaces:
        interface = {
            'name': interf[0],
            'description': interf[1],
            'ipv4': interf[2],
            'mgmt': "no",
            'status': 'active',
            'vrf': 'GRT',
            'type': 'access',  # access, trunk, svi, po, l3, tunnel, loopback, not set
            'access_vlan': '100',
            'portfast': 'yes',
            'bpduguard': 'yes',
            'trunk_vlan_id': ['10', '20'],
            'trunk_vlans': '100',
            'ip_helper': ['10.76.131.19', '10.76.131.20'],
            'ip_redirects': 'no',
            'proxy_arp': 'no',
            'native_vlan': '2',
            'channel_group': '2',
            'channel_group_mode': 'active',
            'sw_negotiate': 'no',
            'mdix': 'auto',
            'dot1x_mab': 'no',
            'dot1x_auth_order': 'mab dot1x',
            'dot1x_auth_prio': 'dot1x mab',
            'dot1x_auth_port_control': 'auto'
        }



    interfaces_configuration.append(file)
    interfaces_configuration.append(dev_id)
    interfaces_configuration.append(get_type_of_sw_from_hostname(devinfo[0]))
    interfaces_configuration.append(get_num_of_physical_ints(interfaces))
    interfaces_configuration.append(get_num_of_svi_ints(interfaces))
    interfaces_configuration.append(get_num_of_access_int_from_interface_list(interfaces))
    interfaces_configuration.append(get_num_of_trunk_int_from_interface_list(interfaces))
    interfaces_configuration.append(get_num_of_dot1x_interfaces(interfaces))
    interfaces_configuration.append(get_num_of_ints_with_ip(interfaces))
    interfaces_configuration.append(get_access_vlan_ids(interfaces))
    interfaces_configuration.append(get_native_vlan_ids(interfaces))
    interfaces_configuration.append(get_voice_vlan_ids(interfaces))
    interfaces_configuration.append(get_trunk_vlan_ids(interfaces))

    vlans_from_config = get_vlan_config(config, curr_path)
    interfaces_configuration.append(vlans_from_config)

    all_interfaces.append(interfaces)

    """
    fill vlan id for vlans with names   
     - users
     - iot_toro
     - media_equip
     - off_equip
     - admin
    """

    vlan_id = "0"
    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'users':
            vlan_id = vlans_from_config[j][0]

    if vlan_id !="0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'iot_toro':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'media_equip':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'off_equip':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'admin':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    return interfaces_configuration






def get_vlan_config(config, curr_path):
    # Extract vlan information (id, name) from configuration

    vlan_template = open(curr_path + '\\nrt_vlans_config.template')
    fsm = textfsm.TextFSM(vlan_template)
    fsm.Reset()
    vlans = fsm.ParseText(config)

    vlans_configuration = []

    i: int = 0
    j: int = 0
    w: int = 0

    for i in range(0, len(vlans)):
        if vlans[i][0] != "internal":
            if vlans[i][0].find(',') != -1:
                vlans_list =vlans[i][0].split(',')
                for j in range(0, len(vlans_list)):
                    vlans_configuration.append([])
                    vlans_configuration[w].append(vlans_list[j])
                    vlans_configuration[w].append("")
                    w = w +1
            else:
                vlans_configuration.append([])
                vlans_configuration[w].append(vlans[i][0])
                vlans_configuration[w].append(vlans[i][1])
                w = w + 1
    vlan_template.close()
    return vlans_configuration


def get_access_config(config, curr_path):
    # Extract vty device access parameters
    access_template = open(curr_path + '\\nrt_dev_access.template')
    fsm = textfsm.TextFSM(access_template)
    fsm.Reset()
    access = fsm.ParseText(config)

    access_config = []

    for i in range(0, len(access)):
        access_config.append([])
        access_config[i] = access[i]

    if (len(access) == 0):
        access_config.append([])
        access_config[0].append("Not set")
        access_config[0].append("Not set")
        access_config[0].append("Not set")
        access_config[0].append("Not set")
        access_config[0].append("Not set")

        access_config.append([])
        access_config[1].append("Not set")
        access_config[1].append("Not set")
        access_config[1].append("Not set")
        access_config[1].append("Not set")
        access_config[1].append("Not set")

    if (len(access) == 1):
        access_config.append([])
        access_config[1].append("Not set")
        access_config[1].append("Not set")
        access_config[1].append("Not set")
        access_config[1].append("Not set")
        access_config[1].append("Not set")

    if (access_config[0][0] == ""):
        access_config[0][0] = "Not set"

    if (access_config[0][1] == ""):
        access_config[0][1] = "Not set"

    if (access_config[0][2] == ""):
        access_config[0][2] = "Not set"

    if (access_config[0][3] == ""):
        access_config[0][3] = "Not set"

    if (access_config[0][4] == ""):
        access_config[0][4] = "Not set"

    if (access_config[1][0] == ""):
        access_config[1][0] = "Not set"

    if (access_config[1][1] == ""):
        access_config[1][1] = "Not set"

    if (access_config[1][2] == ""):
        access_config[1][2] = "Not set"

    if (access_config[1][3] == ""):
        access_config[1][3] = "Not set"

    if (access_config[1][4] == ""):
        access_config[1][4] = "Not set"

    access_template.close()
    return access_config


def get_con_access_config(config, curr_path):
    # Extract console device access parameters
    access_template = open(curr_path + '\\nrt_dev_con_access.template')
    fsm = textfsm.TextFSM(access_template)
    fsm.Reset()
    access = fsm.ParseText(config)

    access_config = []

    for i in range(0, len(access)):
        access_config.append([])
        access_config[i] = access[i]

    if (len(access) == 0):
        access_config.append([])
        access_config[0].append("Not set")
        access_config[0].append("Not set")
        access_config[0].append("Not set")
        access_config[0].append("Not set")
        access_config[0].append("Not set")

    if (access_config[0][0] == ""):
        access_config[0][0] = "Not set"

    if (access_config[0][1] == ""):
        access_config[0][1] = "Not set"

    if (access_config[0][2] == ""):
        access_config[0][2] = "Not set"

    if (access_config[0][3] == ""):
        access_config[0][3] = "Not set"

    if (access_config[0][4] == ""):
        access_config[0][4] = "Not set"

    access_template.close()
    return access_config


def get_tacacs_server_ips(config, curr_path):
    '''
    Get tacacs server IPs
    '''

    if ("N9K" in obtain_model(config)):
        match = re.findall('^tacacs-server\shost\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)', config, re.MULTILINE)
        if match:
            s = ""
            for i in range(len(match)):
                s = s + " "+match[i]+","
            return s[:-1]
        else:
            return "Fail"
    else:
        # Extract vlan information (id, name) from configuration
        tacacs_template = open(curr_path + '\\nrt_tacacs_servers.template')
        fsm = textfsm.TextFSM(tacacs_template)
        fsm.Reset()
        ips = fsm.ParseText(config)
        tacacs_template.close()

        if ips:
            s = ""
            for i in range(len(ips)):
                s = s + " "+ips[i][1]+","
            return s[:-1]
        else:
            match = re.findall('^tacacs-server\shost\s([0-9]+.[0-9]+.[0-9]+.[0-9]+)', config, re.MULTILINE)
            if match:
                s = ""
                for i in range(len(match)):
                    s = s + " " + match[i] + ","
                return s[:-1]
            else:
                return "Fail"


def get_int_status(config):
    # Extract vty device access parameters
    int_stat_template = open(curr_path + '\\nrt_interface_status.template')
    fsm = textfsm.TextFSM(int_stat_template)
    fsm.Reset()
    int_stat = fsm.ParseText(config)

    interfaces_status = []

    for interf in int_stat:
    # Port      Name     Status     Vlan    Duplex Speed    Type
    # Gi1/0/1           notconnect  1267     auto   auto    10/100/1000BaseTX

        interfaces_status.append({
            'interface': interf[0],
            'name': interf[1],
            'status': interf[2],
            'vlan': interf[3],
            'duplex': interf[4],
            'speed': interf[5],
            'type': interf[6]
        })

    return interfaces_status